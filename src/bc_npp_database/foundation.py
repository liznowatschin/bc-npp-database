"""Foundation release artifact validation for BC-NPPD."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canonical import master_species_columns
from .config import EVIDENCE_CONFIDENCE_VALUES
from .diagnostics import Diagnostic, Severity
from .scoring import validate_score_inputs
from .sources import (
    SOURCE_ID_PATTERN,
    SPECIES_ID_PATTERN,
    validate_source_attribution_records,
    validate_source_records,
)
from .validate import diagnose_duplicate_species_ids

FOUNDATION_REQUIRED_FILES = (
    "schema_freeze.json",
    "species.csv",
    "sources.csv",
    "source_attribution.csv",
    "score_inputs.csv",
    "release_checklist.md",
)


@dataclass(frozen=True)
class FoundationValidationResult:
    """Validation result for a foundation artifact directory."""

    path: str
    diagnostics: tuple[Diagnostic, ...]
    counts: dict[str, int]

    def to_summary_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable validation summary."""
        return {
            "path": self.path,
            "counts": self.counts,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


def validate_foundation_dir(path: Path) -> FoundationValidationResult:
    """Validate a BC-NPPD foundation artifact directory."""
    diagnostics: list[Diagnostic] = []
    counts = {"species": 0, "sources": 0, "source_attribution": 0, "score_inputs": 0}

    for filename in FOUNDATION_REQUIRED_FILES:
        if not (path / filename).exists():
            diagnostics.append(
                Diagnostic(
                    code="missing_foundation_file",
                    message=f"Missing foundation artifact: {filename}",
                    severity=Severity.ERROR,
                    field="path",
                    value=filename,
                )
            )
    if any(diagnostic.code == "missing_foundation_file" for diagnostic in diagnostics):
        return FoundationValidationResult(
            path=str(path),
            diagnostics=tuple(diagnostics),
            counts=counts,
        )

    manifest = _load_json(path / "schema_freeze.json", diagnostics)
    species_rows = _load_csv(path / "species.csv", diagnostics)
    source_rows = _load_csv(path / "sources.csv", diagnostics)
    attribution_rows = _load_csv(path / "source_attribution.csv", diagnostics)
    score_rows = _load_csv(path / "score_inputs.csv", diagnostics)

    counts.update(
        {
            "species": len(species_rows),
            "sources": len(source_rows),
            "source_attribution": len(attribution_rows),
            "score_inputs": len(score_rows),
        }
    )

    diagnostics.extend(_validate_manifest(manifest))
    diagnostics.extend(_validate_species_rows(species_rows))
    diagnostics.extend(validate_source_records(source_rows))
    diagnostics.extend(validate_source_attribution_records(attribution_rows))
    diagnostics.extend(validate_score_inputs(score_rows))
    diagnostics.extend(
        _validate_cross_file_links(
            manifest,
            species_rows,
            source_rows,
            attribution_rows,
            score_rows,
        )
    )

    return FoundationValidationResult(path=str(path), diagnostics=tuple(diagnostics), counts=counts)


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...]) -> bool:
    """Return whether diagnostics contain at least one error."""
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


def _validate_manifest(manifest: dict[str, Any]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for field in (
        "foundation_version",
        "status",
        "schema_files",
        "contracts",
        "foundation_species_ids",
    ):
        if not manifest.get(field):
            diagnostics.append(_diagnostic("missing_manifest_field", field=field))
    species_ids = manifest.get("foundation_species_ids", [])
    if not isinstance(species_ids, list):
        diagnostics.append(
            _diagnostic("invalid_manifest_species_ids", field="foundation_species_ids")
        )
    else:
        for species_id in species_ids:
            if not isinstance(species_id, str) or not SPECIES_ID_PATTERN.fullmatch(species_id):
                diagnostics.append(
                    _diagnostic(
                        "invalid_species_id",
                        field="foundation_species_ids",
                        value=str(species_id),
                    )
                )
    hygiene = manifest.get("public_hygiene", {})
    if not isinstance(hygiene, dict):
        diagnostics.append(_diagnostic("invalid_public_hygiene", field="public_hygiene"))
    else:
        for field in (
            "raw_sources_tracked",
            "generated_outputs_tracked",
            "external_downloads_required",
            "private_data_tracked",
        ):
            if hygiene.get(field) is not False:
                diagnostics.append(_diagnostic("public_hygiene_not_false", field=field))
    return diagnostics


def _validate_species_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    expected_columns = master_species_columns()
    for column in expected_columns:
        if rows and column not in rows[0]:
            diagnostics.append(_diagnostic("missing_species_column", field=column))
    for row_number, row in enumerate(rows, start=2):
        species_id = row.get("Species ID", "").strip()
        if not species_id:
            diagnostics.append(_diagnostic("missing_required_field", row_number, "Species ID"))
        elif not SPECIES_ID_PATTERN.fullmatch(species_id):
            diagnostics.append(
                _diagnostic("invalid_species_id", row_number, "Species ID", species_id)
            )
        if not row.get("Botanical Name", "").strip():
            diagnostics.append(_diagnostic("missing_required_field", row_number, "Botanical Name"))
        evidence = row.get("Evidence Level", "").strip()
        if evidence not in EVIDENCE_CONFIDENCE_VALUES:
            diagnostics.append(
                _diagnostic("invalid_evidence_confidence", row_number, "Evidence Level", evidence)
            )
    diagnostics.extend(diagnose_duplicate_species_ids(rows))
    return diagnostics


def _validate_cross_file_links(
    manifest: dict[str, Any],
    species_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
    attribution_rows: list[dict[str, str]],
    score_rows: list[dict[str, str]],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    species_ids = {
        row.get("Species ID", "").strip() for row in species_rows if row.get("Species ID")
    }
    source_ids = {row.get("source_id", "").strip() for row in source_rows if row.get("source_id")}
    foundation_species_ids = set(manifest.get("foundation_species_ids", []))
    if foundation_species_ids != species_ids:
        diagnostics.append(
            _diagnostic(
                "foundation_species_mismatch",
                field="foundation_species_ids",
                value=";".join(sorted(foundation_species_ids ^ species_ids)),
            )
        )
    for row_number, row in enumerate(attribution_rows, start=2):
        _check_species_and_source_links(diagnostics, row, row_number, species_ids, source_ids)
    for row_number, row in enumerate(score_rows, start=2):
        _check_species_and_source_links(diagnostics, row, row_number, species_ids, source_ids)
    for source_id in source_ids:
        if not SOURCE_ID_PATTERN.fullmatch(source_id):
            diagnostics.append(_diagnostic("invalid_source_id", field="source_id", value=source_id))
    return diagnostics


def _check_species_and_source_links(
    diagnostics: list[Diagnostic],
    row: dict[str, str],
    row_number: int,
    species_ids: set[str],
    source_ids: set[str],
) -> None:
    species_id = row.get("species_id", row.get("Species ID", "")).strip()
    source_id = row.get("source_id", row.get("Source ID", "")).strip()
    if species_id and species_id not in species_ids:
        diagnostics.append(
            _diagnostic("unknown_foundation_species_id", row_number, "species_id", species_id)
        )
    if source_id and source_id not in source_ids:
        diagnostics.append(
            _diagnostic("unknown_foundation_source_id", row_number, "source_id", source_id)
        )


def _load_json(path: Path, diagnostics: list[Diagnostic]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        diagnostics.append(
            Diagnostic(
                code="foundation_json_unreadable",
                message=f"Foundation JSON could not be read: {exc}",
                severity=Severity.ERROR,
                field="path",
                value=str(path),
            )
        )
        return {}
    if not isinstance(payload, dict):
        diagnostics.append(_diagnostic("foundation_json_not_object", field="path", value=str(path)))
        return {}
    return payload


def _load_csv(path: Path, diagnostics: list[Diagnostic]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except OSError as exc:
        diagnostics.append(
            Diagnostic(
                code="foundation_csv_unreadable",
                message=f"Foundation CSV could not be read: {exc}",
                severity=Severity.ERROR,
                field="path",
                value=str(path),
            )
        )
        return []


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
