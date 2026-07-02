"""Evidence hardening for the Vancouver plant list proof of concept."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .diagnostics import Diagnostic, Severity
from .sources import SPECIES_ID_PATTERN
from .vancouver_poc import (
    DIAGNOSTIC_FIELDS,
    POC_PLANT_COLUMNS,
    validate_vancouver_poc_list,
)
from .vancouver_poc import (
    has_error_diagnostics as has_poc_error_diagnostics,
)

HARDENING_REQUIRED_FILES = (
    "hardened_plant_list.csv",
    "reviewed_sources.csv",
    "reviewed_fields.csv",
    "evidence_gap_report.csv",
    "score_readiness.csv",
    "manifest.json",
    "diagnostics.csv",
)

HARDENED_PLANT_COLUMNS = (
    *POC_PLANT_COLUMNS,
    "reviewed_field_count",
    "gap_count",
    "evidence_hardening_status",
    "score_readiness",
    "next_review_action",
)

REVIEWED_SOURCE_FIELDS = (
    "source_id",
    "source_name",
    "source_tier",
    "p7_review_status",
    "usable_for",
    "rationale",
)

REVIEWED_FIELD_FIELDS = (
    "species_id",
    "field_name",
    "field_value",
    "evidence_status",
    "source_ids",
    "evidence_confidence",
    "rationale",
)

GAP_FIELDS = (
    "species_id",
    "field_name",
    "field_value",
    "gap_type",
    "recommended_action",
    "current_source_ids",
)

SCORE_READINESS_FIELDS = (
    "species_id",
    "score_family",
    "readiness_status",
    "reason",
)

IDENTITY_NATIVE_RANGE_FIELDS = (
    "Botanical Name",
    "Common Name",
    "Family",
    "Native Status",
)

CANDIDATE_REVIEW_FIELDS = (
    "Plant Type",
    "Life Cycle",
    "Sun",
    "Soil Moisture",
    "Urban Toughness",
)

SCORE_FAMILIES = ("UNI", "PSI", "RVI")
REVIEWED_FIELD_STATUS = "poc_reviewed"
SCORE_NOT_READY = "not_ready"
TAXONOMY_CLAIM_FIELD = "Taxonomy / Native range / Habitat"
TAXONOMY_CONFIDENCE_VALUES = {"A", "B"}
TAXONOMY_SOURCE_TIERS = {"Tier 1", "Tier 2"}

HARDENING_CAVEAT = (
    "P7 hardening marks only identity/native-range display fields as "
    "PoC-reviewed where Tier 1/2 taxonomy attribution exists; horticultural "
    "and scoring fields remain candidate values pending field-level review."
)


@dataclass(frozen=True)
class EvidenceHardeningResult:
    """Generated or validated evidence-hardening artifact summary."""

    path: str
    counts: dict[str, int]
    diagnostics: tuple[Diagnostic, ...]
    paths: dict[str, str]

    def to_summary_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable summary."""
        return {
            "path": self.path,
            "counts": self.counts,
            "paths": self.paths,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


def generate_vancouver_evidence_hardening(
    poc_dir: Path,
    output_dir: Path,
) -> EvidenceHardeningResult:
    """Generate P7 evidence-hardening artifacts from the tracked Vancouver PoC."""
    poc_validation = validate_vancouver_poc_list(poc_dir)
    if has_poc_error_diagnostics(poc_validation.diagnostics):
        return EvidenceHardeningResult(
            path=str(output_dir),
            counts=_empty_counts(),
            diagnostics=poc_validation.diagnostics,
            paths={},
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    plant_rows = _load_csv(poc_dir / "plant_list.csv", [])
    source_rows = _load_csv(poc_dir / "sources.csv", [])
    attribution_rows = _load_csv(poc_dir / "source_attribution.csv", [])
    sources_by_id = {row.get("source_id", ""): row for row in source_rows}
    taxonomy_support = _taxonomy_support_by_species(attribution_rows, sources_by_id)

    reviewed_sources = _review_sources(source_rows)
    reviewed_fields: list[dict[str, str]] = []
    gap_rows: list[dict[str, str]] = []
    score_rows: list[dict[str, str]] = []
    hardened_rows: list[dict[str, str]] = []

    for plant in plant_rows:
        species_id = plant.get("Species ID", "")
        support = taxonomy_support.get(species_id, [])
        source_ids = sorted({row.get("source_id", "") for row in support if row.get("source_id")})
        evidence_confidence = _best_confidence(support)

        if source_ids:
            for field in IDENTITY_NATIVE_RANGE_FIELDS:
                reviewed_fields.append(
                    {
                        "species_id": species_id,
                        "field_name": field,
                        "field_value": plant.get(field, ""),
                        "evidence_status": REVIEWED_FIELD_STATUS,
                        "source_ids": ";".join(source_ids),
                        "evidence_confidence": evidence_confidence,
                        "rationale": (
                            "Tier 1/2 taxonomy/native-range attribution supports "
                            "this identity/native-range display field for PoC use."
                        ),
                    }
                )

        for field in CANDIDATE_REVIEW_FIELDS:
            value = plant.get(field, "")
            gap_rows.append(
                {
                    "species_id": species_id,
                    "field_name": field,
                    "field_value": value,
                    "gap_type": (
                        "candidate_value_needs_field_review"
                        if value
                        else "missing_value_needs_review"
                    ),
                    "recommended_action": (
                        "Add field-specific reviewed source attribution before "
                        "promoting this value or using it in scores."
                    ),
                    "current_source_ids": plant.get("Primary References", ""),
                }
            )

        for score_family in SCORE_FAMILIES:
            score_rows.append(
                {
                    "species_id": species_id,
                    "score_family": score_family,
                    "readiness_status": SCORE_NOT_READY,
                    "reason": (
                        "PoC workbook suitability/toughness values are candidate "
                        "display values and are not accepted P4 score inputs."
                    ),
                }
            )

        hardened = dict(plant)
        hardened.update(
            {
                "reviewed_field_count": str(
                    len(IDENTITY_NATIVE_RANGE_FIELDS) if source_ids else 0
                ),
                "gap_count": str(len(CANDIDATE_REVIEW_FIELDS)),
                "evidence_hardening_status": (
                    "identity_native_range_reviewed_use_fields_candidate"
                    if source_ids
                    else "needs_identity_native_range_review"
                ),
                "score_readiness": SCORE_NOT_READY,
                "next_review_action": (
                    "Review horticultural/use fields and create explicit P4 "
                    "score-input rows before calculating UNI, PSI, or RVI."
                ),
            }
        )
        hardened_rows.append(hardened)

    diagnostics = (
        Diagnostic(
            code="evidence_hardening_caveat",
            message=HARDENING_CAVEAT,
            severity=Severity.WARNING,
            context={"species_count": len(hardened_rows)},
        ),
    )
    paths = _paths(output_dir)
    _write_csv(Path(paths["hardened_plant_list"]), hardened_rows, HARDENED_PLANT_COLUMNS)
    _write_csv(Path(paths["reviewed_sources"]), reviewed_sources, REVIEWED_SOURCE_FIELDS)
    _write_csv(Path(paths["reviewed_fields"]), reviewed_fields, REVIEWED_FIELD_FIELDS)
    _write_csv(Path(paths["evidence_gap_report"]), gap_rows, GAP_FIELDS)
    _write_csv(Path(paths["score_readiness"]), score_rows, SCORE_READINESS_FIELDS)
    _write_csv(
        Path(paths["diagnostics"]),
        [diagnostic.to_dict() for diagnostic in diagnostics],
        DIAGNOSTIC_FIELDS,
    )
    _write_json(
        Path(paths["manifest"]),
        {
            "artifact_name": "Vancouver Evidence Hardening",
            "input_poc_dir": str(poc_dir),
            "status": "p7_evidence_hardened_poc",
            "species_count": len(hardened_rows),
            "reviewed_source_count": len(reviewed_sources),
            "reviewed_field_count": len(reviewed_fields),
            "evidence_gap_count": len(gap_rows),
            "score_readiness_count": len(score_rows),
            "score_policy": (
                "All UNI/PSI/RVI score families are not_ready until explicit "
                "reviewed numeric P4 score inputs exist."
            ),
            "public_hygiene": {
                "raw_sources_tracked": False,
                "external_downloads_required": False,
                "private_data_tracked": False,
            },
            "caveat": HARDENING_CAVEAT,
        },
    )

    return validate_vancouver_evidence_hardening(output_dir)


def validate_vancouver_evidence_hardening(path: Path) -> EvidenceHardeningResult:
    """Validate a generated Vancouver evidence-hardening artifact directory."""
    diagnostics: list[Diagnostic] = []
    counts = _empty_counts()
    for filename in HARDENING_REQUIRED_FILES:
        if not (path / filename).exists():
            diagnostics.append(_diagnostic("missing_hardening_file", field="path", value=filename))
    if diagnostics:
        return EvidenceHardeningResult(str(path), counts, tuple(diagnostics), {})

    hardened_rows = _load_csv(path / "hardened_plant_list.csv", diagnostics)
    reviewed_source_rows = _load_csv(path / "reviewed_sources.csv", diagnostics)
    reviewed_field_rows = _load_csv(path / "reviewed_fields.csv", diagnostics)
    gap_rows = _load_csv(path / "evidence_gap_report.csv", diagnostics)
    score_rows = _load_csv(path / "score_readiness.csv", diagnostics)
    diagnostic_rows = _load_csv(path / "diagnostics.csv", diagnostics)
    manifest = _load_json(path / "manifest.json", diagnostics)

    counts.update(
        {
            "hardened_plant_list": len(hardened_rows),
            "reviewed_sources": len(reviewed_source_rows),
            "reviewed_fields": len(reviewed_field_rows),
            "evidence_gaps": len(gap_rows),
            "score_readiness": len(score_rows),
        }
    )
    species_ids = {row.get("Species ID", "") for row in hardened_rows}
    source_ids = {row.get("source_id", "") for row in reviewed_source_rows}
    diagnostics.extend(_validate_hardened_rows(hardened_rows))
    diagnostics.extend(_validate_reviewed_sources(reviewed_source_rows))
    diagnostics.extend(_validate_reviewed_fields(reviewed_field_rows, species_ids, source_ids))
    diagnostics.extend(_validate_gap_rows(gap_rows, species_ids))
    diagnostics.extend(_validate_score_rows(score_rows, species_ids))
    diagnostics.extend(_validate_manifest(manifest, counts))
    diagnostics.extend(_validate_diagnostic_rows(diagnostic_rows))

    return EvidenceHardeningResult(str(path), counts, tuple(diagnostics), _paths(path))


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...]) -> bool:
    """Return whether diagnostics contain at least one error."""
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


def _taxonomy_support_by_species(
    attribution_rows: list[dict[str, str]],
    sources_by_id: dict[str, dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    support: dict[str, list[dict[str, str]]] = {}
    for row in attribution_rows:
        source = sources_by_id.get(row.get("source_id", ""), {})
        if (
            row.get("claim_field") == TAXONOMY_CLAIM_FIELD
            and row.get("evidence_confidence") in TAXONOMY_CONFIDENCE_VALUES
            and source.get("source_tier") in TAXONOMY_SOURCE_TIERS
        ):
            support.setdefault(row.get("species_id", ""), []).append(row)
    return support


def _review_sources(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    reviewed: list[dict[str, str]] = []
    for row in source_rows:
        source_tier = row.get("source_tier", "")
        if source_tier in TAXONOMY_SOURCE_TIERS:
            status = "accepted_for_poc_identity_native_range"
            usable_for = "identity_native_range"
            rationale = "Tier 1/2 source is acceptable for P7 PoC identity/native-range review."
        else:
            status = "candidate_practitioner_context"
            usable_for = "context_only"
            rationale = "Tier 3 source is retained as context, not as reviewed score input."
        reviewed.append(
            {
                "source_id": row.get("source_id", ""),
                "source_name": row.get("source_name", ""),
                "source_tier": source_tier,
                "p7_review_status": status,
                "usable_for": usable_for,
                "rationale": rationale,
            }
        )
    return reviewed


def _best_confidence(rows: list[dict[str, str]]) -> str:
    order = {"A": 0, "B": 1, "C": 2, "D": 3, "Mixed": 4, "Pending review": 5}
    values = [row.get("evidence_confidence", "Pending review") for row in rows]
    return sorted(values, key=lambda value: order.get(value, 99))[0] if values else "Pending review"


def _validate_hardened_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        species_id = row.get("Species ID", "")
        if not SPECIES_ID_PATTERN.fullmatch(species_id):
            diagnostics.append(
                _diagnostic("invalid_species_id", row_number, "Species ID", species_id)
            )
        if row.get("score_readiness") != SCORE_NOT_READY:
            diagnostics.append(
                _diagnostic("invalid_score_readiness", row_number, "score_readiness")
            )
        if not row.get("evidence_hardening_status"):
            diagnostics.append(
                _diagnostic(
                    "missing_evidence_hardening_status",
                    row_number,
                    "evidence_hardening_status",
                )
            )
    return diagnostics


def _validate_reviewed_sources(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    allowed_statuses = {
        "accepted_for_poc_identity_native_range",
        "candidate_practitioner_context",
    }
    for row_number, row in enumerate(rows, start=2):
        if not row.get("source_id"):
            diagnostics.append(_diagnostic("missing_source_id", row_number, "source_id"))
        if row.get("p7_review_status") not in allowed_statuses:
            diagnostics.append(
                _diagnostic(
                    "invalid_p7_source_review_status",
                    row_number,
                    "p7_review_status",
                    row.get("p7_review_status"),
                )
            )
    return diagnostics


def _validate_reviewed_fields(
    rows: list[dict[str, str]],
    species_ids: set[str],
    source_ids: set[str],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        species_id = row.get("species_id", "")
        if species_id not in species_ids:
            diagnostics.append(
                _diagnostic("unknown_species_id", row_number, "species_id", species_id)
            )
        if row.get("field_name") not in IDENTITY_NATIVE_RANGE_FIELDS:
            diagnostics.append(
                _diagnostic(
                    "unsupported_reviewed_field",
                    row_number,
                    "field_name",
                    row.get("field_name"),
                )
            )
        if row.get("evidence_status") != REVIEWED_FIELD_STATUS:
            diagnostics.append(
                _diagnostic("invalid_evidence_status", row_number, "evidence_status")
            )
        if not row.get("source_ids"):
            diagnostics.append(_diagnostic("missing_source_ids", row_number, "source_ids"))
        for source_id in row.get("source_ids", "").split(";"):
            if source_id and source_id not in source_ids:
                diagnostics.append(
                    _diagnostic("unknown_source_id", row_number, "source_ids", source_id)
                )
    return diagnostics


def _validate_gap_rows(rows: list[dict[str, str]], species_ids: set[str]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    allowed_gap_types = {"candidate_value_needs_field_review", "missing_value_needs_review"}
    for row_number, row in enumerate(rows, start=2):
        species_id = row.get("species_id", "")
        if species_id not in species_ids:
            diagnostics.append(
                _diagnostic("unknown_species_id", row_number, "species_id", species_id)
            )
        if row.get("field_name") not in CANDIDATE_REVIEW_FIELDS:
            diagnostics.append(_diagnostic("unsupported_gap_field", row_number, "field_name"))
        if row.get("gap_type") not in allowed_gap_types:
            diagnostics.append(_diagnostic("invalid_gap_type", row_number, "gap_type"))
    return diagnostics


def _validate_score_rows(rows: list[dict[str, str]], species_ids: set[str]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        species_id = row.get("species_id", "")
        if species_id not in species_ids:
            diagnostics.append(
                _diagnostic("unknown_species_id", row_number, "species_id", species_id)
            )
        if row.get("score_family") not in SCORE_FAMILIES:
            diagnostics.append(_diagnostic("invalid_score_family", row_number, "score_family"))
        if row.get("readiness_status") != SCORE_NOT_READY:
            diagnostics.append(
                _diagnostic("invalid_readiness_status", row_number, "readiness_status")
            )
    return diagnostics


def _validate_manifest(manifest: dict[str, Any], counts: dict[str, int]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    expected = {
        "species_count": counts["hardened_plant_list"],
        "reviewed_source_count": counts["reviewed_sources"],
        "reviewed_field_count": counts["reviewed_fields"],
        "evidence_gap_count": counts["evidence_gaps"],
        "score_readiness_count": counts["score_readiness"],
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            diagnostics.append(
                _diagnostic("manifest_count_mismatch", field=key, value=str(manifest.get(key)))
            )
    hygiene = manifest.get("public_hygiene", {})
    if not isinstance(hygiene, dict):
        diagnostics.append(_diagnostic("invalid_public_hygiene", field="public_hygiene"))
    elif (
        hygiene.get("raw_sources_tracked") is not False
        or hygiene.get("external_downloads_required") is not False
        or hygiene.get("private_data_tracked") is not False
    ):
        diagnostics.append(_diagnostic("public_hygiene_not_false", field="public_hygiene"))
    return diagnostics


def _validate_diagnostic_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        if row.get("severity") == Severity.ERROR.value:
            diagnostics.append(
                _diagnostic(
                    "hardening_diagnostics_contain_error",
                    row_number,
                    "severity",
                    row.get("code"),
                )
            )
    return diagnostics


def _empty_counts() -> dict[str, int]:
    return {
        "hardened_plant_list": 0,
        "reviewed_sources": 0,
        "reviewed_fields": 0,
        "evidence_gaps": 0,
        "score_readiness": 0,
    }


def _paths(path: Path) -> dict[str, str]:
    return {
        "hardened_plant_list": str(path / "hardened_plant_list.csv"),
        "reviewed_sources": str(path / "reviewed_sources.csv"),
        "reviewed_fields": str(path / "reviewed_fields.csv"),
        "evidence_gap_report": str(path / "evidence_gap_report.csv"),
        "score_readiness": str(path / "score_readiness.csv"),
        "manifest": str(path / "manifest.json"),
        "diagnostics": str(path / "diagnostics.csv"),
    }


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _clean(row.get(field)) for field in fieldnames})


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_csv(path: Path, diagnostics: list[Diagnostic]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except OSError as exc:
        diagnostics.append(
            _diagnostic("hardening_csv_unreadable", field="path", value=f"{path}: {exc}")
        )
        return []


def _load_json(path: Path, diagnostics: list[Diagnostic]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        diagnostics.append(
            _diagnostic("hardening_json_unreadable", field="path", value=f"{path}: {exc}")
        )
        return {}
    return payload if isinstance(payload, dict) else {}


def _diagnostic(
    code: str,
    row_number: int | None = None,
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


def _clean(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value).strip()
