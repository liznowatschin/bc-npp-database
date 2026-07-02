"""Evidence-aware scoring records and calculations for BC-NPPD."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .config import EVIDENCE_CONFIDENCE_VALUES
from .diagnostics import Diagnostic, Severity
from .sources import (
    SOURCE_ID_PATTERN,
    SPECIES_ID_PATTERN,
    ReviewStatus,
    is_review_accepted,
)

SCORE_VALUE_MIN = 0.0
SCORE_VALUE_MAX = 5.0


class ScoreFamily(StrEnum):
    """Supported BC-NPPD score families."""

    UNI = "UNI"
    PSI = "PSI"
    RVI = "RVI"


class ScoreStatus(StrEnum):
    """Score calculation status."""

    CALCULATED = "calculated"
    NOT_CALCULATED = "not_calculated"


@dataclass(frozen=True)
class ScoreWeightRecord:
    """One provisional score metric weight."""

    score_family: str
    metric: str
    weight: str
    review_status: str = ReviewStatus.PENDING.value
    notes: str = ""

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> ScoreWeightRecord:
        """Build a score weight from common CSV/JSON field names."""
        return cls(
            score_family=_first(row, "score_family", "Score Family", "family", "Family"),
            metric=_first(row, "metric", "Metric", "field", "Field"),
            weight=_first(row, "weight", "Weight"),
            review_status=_first(
                row,
                "review_status",
                "Review Status",
                default=ReviewStatus.PENDING.value,
            ),
            notes=_first(row, "notes", "Notes"),
        )

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable weight dictionary."""
        return {
            "score_family": self.score_family,
            "metric": self.metric,
            "weight": self.weight,
            "review_status": self.review_status,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ScoreInputRecord:
    """One reviewed numeric input for a score calculation."""

    species_id: str
    score_family: str
    metric: str
    value: str
    source_id: str
    evidence_confidence: str
    weight: str = ""
    review_status: str = ReviewStatus.PENDING.value
    external_id: str = ""
    context_id: str = ""
    notes: str = ""

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> ScoreInputRecord:
        """Build a score input from common CSV/JSON field names."""
        return cls(
            species_id=_first(row, "species_id", "Species ID", "Species_ID"),
            score_family=_first(row, "score_family", "Score Family", "family", "Family"),
            metric=_first(row, "metric", "Metric", "field", "Field"),
            value=_first(row, "value", "Value", "score_value", "Score Value"),
            source_id=_first(row, "source_id", "Source ID", "Reference ID", "reference_id"),
            evidence_confidence=_first(
                row,
                "evidence_confidence",
                "Evidence Confidence",
                "Evidence Level",
                "Evidence_Confidence",
            ),
            weight=_first(row, "weight", "Weight"),
            review_status=_first(
                row,
                "review_status",
                "Review Status",
                default=ReviewStatus.PENDING.value,
            ),
            external_id=_first(row, "external_id", "External ID", "external_source_id"),
            context_id=_first(row, "context_id", "Context ID", "media_id", "Media ID"),
            notes=_first(row, "notes", "Notes"),
        )

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable score input dictionary."""
        return {
            "species_id": self.species_id,
            "score_family": self.score_family,
            "metric": self.metric,
            "value": self.value,
            "source_id": self.source_id,
            "evidence_confidence": self.evidence_confidence,
            "weight": self.weight,
            "review_status": self.review_status,
            "external_id": self.external_id,
            "context_id": self.context_id,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ScoreResultRecord:
    """One calculated score result."""

    species_id: str
    score_family: str
    score: float | None
    status: str
    input_count: int
    weight_total: float
    evidence_summary: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable score result dictionary."""
        return {
            "species_id": self.species_id,
            "score_family": self.score_family,
            "score": self.score,
            "status": self.status,
            "input_count": self.input_count,
            "weight_total": self.weight_total,
            "evidence_summary": self.evidence_summary,
        }


@dataclass(frozen=True)
class ScoreRunSummary:
    """Summary of a score calculation run."""

    results: tuple[ScoreResultRecord, ...]
    diagnostics: tuple[Diagnostic, ...]

    def to_summary_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable score run summary."""
        return {
            "counts": {
                "results": len(self.results),
                "diagnostics": len(self.diagnostics),
            },
            "results": [result.to_dict() for result in self.results],
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


def score_family_values() -> set[str]:
    """Return supported score family values."""
    return {family.value for family in ScoreFamily}


def validate_score_weights(rows: Iterable[Mapping[str, object]]) -> list[Diagnostic]:
    """Validate score weight rows."""
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=1):
        record = ScoreWeightRecord.from_mapping(row)
        diagnostics.extend(_validate_weight(record, row_number))
    return diagnostics


def validate_score_inputs(
    rows: Iterable[Mapping[str, object]],
    weight_rows: Iterable[Mapping[str, object]] = (),
) -> list[Diagnostic]:
    """Validate score input rows and optional weight records."""
    weights = tuple(ScoreWeightRecord.from_mapping(row) for row in weight_rows)
    diagnostics = validate_score_weights(weight.to_dict() for weight in weights)
    weight_lookup = _weight_lookup(weights)
    for row_number, row in enumerate(rows, start=1):
        record = ScoreInputRecord.from_mapping(row)
        diagnostics.extend(_validate_input(record, row_number, weight_lookup))
    return diagnostics


def calculate_scores(
    rows: Iterable[Mapping[str, object]],
    weight_rows: Iterable[Mapping[str, object]] = (),
) -> ScoreRunSummary:
    """Calculate provisional scores from explicit reviewed numeric inputs."""
    inputs = tuple(ScoreInputRecord.from_mapping(row) for row in rows)
    weights = tuple(ScoreWeightRecord.from_mapping(row) for row in weight_rows)
    weight_lookup = _weight_lookup(weights)

    diagnostics: list[Diagnostic] = []
    diagnostics.extend(validate_score_weights(weight.to_dict() for weight in weights))

    accepted_inputs: list[tuple[ScoreInputRecord, float, float]] = []
    for row_number, record in enumerate(inputs, start=1):
        row_diagnostics = _validate_input(record, row_number, weight_lookup)
        diagnostics.extend(row_diagnostics)
        if any(diagnostic.severity == Severity.ERROR for diagnostic in row_diagnostics):
            continue
        if not is_review_accepted(record.review_status):
            continue
        value = float(record.value)
        weight = _resolved_weight(record, weight_lookup)
        accepted_inputs.append((record, value, weight))

    results: list[ScoreResultRecord] = []
    result_keys = {
        (record.species_id, record.score_family) for record, _, _ in accepted_inputs
    }
    for key in sorted(result_keys):
        species_id, score_family = key
        group = [
            (record, value, weight)
            for record, value, weight in accepted_inputs
            if record.species_id == species_id and record.score_family == score_family
        ]
        weight_total = sum(weight for _, _, weight in group)
        if weight_total <= 0:
            results.append(
                ScoreResultRecord(
                    species_id=species_id,
                    score_family=score_family,
                    score=None,
                    status=ScoreStatus.NOT_CALCULATED.value,
                    input_count=len(group),
                    weight_total=weight_total,
                    evidence_summary=_evidence_summary(group),
                )
            )
            continue
        weighted_average = sum(value * weight for _, value, weight in group) / weight_total
        results.append(
            ScoreResultRecord(
                species_id=species_id,
                score_family=score_family,
                score=round((weighted_average / SCORE_VALUE_MAX) * 100, 2),
                status=ScoreStatus.CALCULATED.value,
                input_count=len(group),
                weight_total=round(weight_total, 6),
                evidence_summary=_evidence_summary(group),
            )
        )

    return ScoreRunSummary(results=tuple(results), diagnostics=tuple(diagnostics))


def has_error_diagnostics(diagnostics: Iterable[Diagnostic]) -> bool:
    """Return whether diagnostics contain at least one error."""
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


def _validate_weight(record: ScoreWeightRecord, row_number: int) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    diagnostics.extend(_required(record.score_family, "score_family", row_number))
    diagnostics.extend(_required(record.metric, "metric", row_number))
    diagnostics.extend(_required(record.weight, "weight", row_number))
    if record.score_family and record.score_family not in score_family_values():
        diagnostics.append(
            _diagnostic("invalid_score_family", row_number, "score_family", record.score_family)
        )
    weight = _parse_float(record.weight)
    if record.weight and (weight is None or weight < 0):
        diagnostics.append(_diagnostic("invalid_score_weight", row_number, "weight", record.weight))
    if record.review_status not in {status.value for status in ReviewStatus}:
        diagnostics.append(
            _diagnostic("invalid_review_status", row_number, "review_status", record.review_status)
        )
    return diagnostics


def _validate_input(
    record: ScoreInputRecord,
    row_number: int,
    weight_lookup: Mapping[tuple[str, str], float],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    diagnostics.extend(_required(record.species_id, "species_id", row_number))
    diagnostics.extend(_required(record.score_family, "score_family", row_number))
    diagnostics.extend(_required(record.metric, "metric", row_number))
    diagnostics.extend(_required(record.value, "value", row_number))
    diagnostics.extend(_required(record.source_id, "source_id", row_number))
    diagnostics.extend(_required(record.evidence_confidence, "evidence_confidence", row_number))
    if record.species_id and not SPECIES_ID_PATTERN.fullmatch(record.species_id):
        diagnostics.append(
            _diagnostic("invalid_species_id", row_number, "species_id", record.species_id)
        )
    if record.source_id and not SOURCE_ID_PATTERN.fullmatch(record.source_id):
        diagnostics.append(
            _diagnostic("invalid_source_id", row_number, "source_id", record.source_id)
        )
    if record.score_family and record.score_family not in score_family_values():
        diagnostics.append(
            _diagnostic("invalid_score_family", row_number, "score_family", record.score_family)
        )
    value = _parse_float(record.value)
    if record.value and (value is None or not SCORE_VALUE_MIN <= value <= SCORE_VALUE_MAX):
        diagnostics.append(_diagnostic("invalid_score_value", row_number, "value", record.value))
    if record.evidence_confidence not in EVIDENCE_CONFIDENCE_VALUES:
        diagnostics.append(
            _diagnostic(
                "invalid_evidence_confidence",
                row_number,
                "evidence_confidence",
                record.evidence_confidence,
            )
        )
    if record.review_status not in {status.value for status in ReviewStatus}:
        diagnostics.append(
            _diagnostic("invalid_review_status", row_number, "review_status", record.review_status)
        )
    elif not is_review_accepted(record.review_status):
        diagnostics.append(
            Diagnostic(
                code="unreviewed_score_input",
                message="Score inputs must be accepted or manually corrected before calculation.",
                severity=Severity.ERROR,
                row_number=row_number,
                field="review_status",
                value=record.review_status,
            )
        )
    input_weight = _parse_float(record.weight) if record.weight else None
    if record.weight and (input_weight is None or input_weight < 0):
        diagnostics.append(_diagnostic("invalid_score_weight", row_number, "weight", record.weight))
    if not record.weight and (record.score_family, record.metric) not in weight_lookup:
        diagnostics.append(_diagnostic("missing_score_weight", row_number, "weight"))
    return diagnostics


def _weight_lookup(weights: Iterable[ScoreWeightRecord]) -> dict[tuple[str, str], float]:
    lookup: dict[tuple[str, str], float] = {}
    for weight in weights:
        parsed = _parse_float(weight.weight)
        if parsed is not None:
            lookup[(weight.score_family, weight.metric)] = parsed
    return lookup


def _evidence_summary(group: Iterable[tuple[ScoreInputRecord, float, float]]) -> dict[str, int]:
    return dict(Counter(record.evidence_confidence for record, _, _ in group))


def _resolved_weight(
    record: ScoreInputRecord,
    weight_lookup: Mapping[tuple[str, str], float],
) -> float:
    if record.weight:
        parsed = _parse_float(record.weight)
        if parsed is not None:
            return parsed
    return weight_lookup[(record.score_family, record.metric)]


def _required(value: str, field: str, row_number: int) -> list[Diagnostic]:
    if value:
        return []
    return [
        Diagnostic(
            code="missing_required_field",
            message=f"Missing required field: {field}.",
            severity=Severity.ERROR,
            row_number=row_number,
            field=field,
        )
    ]


def _diagnostic(
    code: str,
    row_number: int,
    field: str | None = None,
    value: str | None = None,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        message=code.replace("_", " ").capitalize() + ".",
        severity=Severity.ERROR,
        row_number=row_number,
        field=field,
        value=value,
    )


def _parse_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def _first(
    row: Mapping[str, object],
    *keys: str,
    default: str = "",
) -> str:
    for key in keys:
        if key in row:
            value = row[key]
            return "" if value is None else str(value).strip()
    return default
