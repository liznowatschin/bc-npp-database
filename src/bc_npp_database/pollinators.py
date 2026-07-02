"""Pollinator evidence-review artifacts for the Vancouver PoC."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .diagnostics import Diagnostic, Severity
from .sources import SPECIES_ID_PATTERN
from .usability import (
    has_error_diagnostics as has_usability_error_diagnostics,
)
from .usability import (
    validate_vancouver_usability,
)
from .vancouver_poc import DIAGNOSTIC_FIELDS

POLLINATOR_REQUIRED_FILES = (
    "pollinator_review.csv",
    "pollinator_evidence_gaps.csv",
    "pollinator_source_requirements.csv",
    "manifest.json",
    "diagnostics.csv",
)

POLLINATOR_REVIEW_FIELDS = (
    "species_id",
    "botanical_name",
    "common_name",
    "family",
    "review_status",
    "psi_readiness",
    "pollinator_queue_reason",
    "evidence_caveat",
    "next_review_action",
)

POLLINATOR_REQUIRED_REVIEW_FIELDS = (
    "species_id",
    "botanical_name",
    "review_status",
    "psi_readiness",
    "pollinator_queue_reason",
    "evidence_caveat",
    "next_review_action",
)

POLLINATOR_GAP_FIELDS = (
    "species_id",
    "pollinator_field",
    "current_value",
    "gap_type",
    "required_evidence",
    "review_status",
    "score_impact",
)

POLLINATOR_SOURCE_REQUIREMENT_FIELDS = (
    "requirement_id",
    "pollinator_field",
    "preferred_source_tiers",
    "minimum_review_status",
    "notes",
)

POLLINATOR_FIELDS = (
    "bloom_period",
    "floral_resources",
    "native_bee_support",
    "butterfly_support",
    "hummingbird_support",
    "specialist_relationships",
    "larval_host_use",
)

SOURCE_REQUIREMENTS = (
    {
        "requirement_id": "POL-SRC-001",
        "pollinator_field": "bloom_period",
        "preferred_source_tiers": "Tier 1;Tier 2",
        "minimum_review_status": "accepted",
        "notes": "Use regional flora, phenology, or reviewed local observations.",
    },
    {
        "requirement_id": "POL-SRC-002",
        "pollinator_field": "floral_resources",
        "preferred_source_tiers": "Tier 1;Tier 2;Tier 3",
        "minimum_review_status": "accepted",
        "notes": "Record nectar, pollen, or both only when explicitly supported.",
    },
    {
        "requirement_id": "POL-SRC-003",
        "pollinator_field": "native_bee_support",
        "preferred_source_tiers": "Tier 1;Tier 2;Tier 3",
        "minimum_review_status": "accepted",
        "notes": "Prefer peer-reviewed or expert regional plant-pollinator evidence.",
    },
    {
        "requirement_id": "POL-SRC-004",
        "pollinator_field": "butterfly_support",
        "preferred_source_tiers": "Tier 1;Tier 2;Tier 3",
        "minimum_review_status": "accepted",
        "notes": "Separate adult nectar use from larval host claims.",
    },
    {
        "requirement_id": "POL-SRC-005",
        "pollinator_field": "hummingbird_support",
        "preferred_source_tiers": "Tier 1;Tier 2;Tier 3",
        "minimum_review_status": "accepted",
        "notes": "Treat as absent or unknown unless source explicitly supports it.",
    },
    {
        "requirement_id": "POL-SRC-006",
        "pollinator_field": "specialist_relationships",
        "preferred_source_tiers": "Tier 1;Tier 2",
        "minimum_review_status": "accepted",
        "notes": "Specialist relationships require explicit source attribution.",
    },
    {
        "requirement_id": "POL-SRC-007",
        "pollinator_field": "larval_host_use",
        "preferred_source_tiers": "Tier 1;Tier 2;Tier 3",
        "minimum_review_status": "accepted",
        "notes": "Host use must name the insect group or taxon when available.",
    },
)

POLLINATOR_CAVEAT = (
    "Pollinator module rows are review scaffolding for the Vancouver PoC. They "
    "do not contain reviewed pollinator-support claims and are not PSI scores."
)

REVIEW_STATUS_VALUES = {"review_queue", "needs_review", "accepted", "rejected"}
PSI_READINESS_VALUES = {"not_ready", "ready"}


@dataclass(frozen=True)
class PollinatorResult:
    """Generated or validated pollinator artifact summary."""

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


def generate_vancouver_pollinator_module(
    usability_dir: Path,
    output_dir: Path,
) -> PollinatorResult:
    """Generate pollinator evidence-review artifacts from P8 usability outputs."""
    usability_validation = validate_vancouver_usability(usability_dir)
    if has_usability_error_diagnostics(usability_validation.diagnostics):
        return PollinatorResult(
            path=str(output_dir),
            counts=_empty_counts(),
            diagnostics=usability_validation.diagnostics,
            paths={},
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    plant_rows = _load_csv(usability_dir / "plant_table.csv", [])
    view_rows = _load_csv(usability_dir / "use_case_views.csv", [])
    pollinator_species = {
        row.get("species_id", "")
        for row in view_rows
        if row.get("use_case") == "pollinator_support"
        and row.get("candidate_status") == "review_queue"
    }

    review_rows: list[dict[str, str]] = []
    gap_rows: list[dict[str, str]] = []
    for plant in plant_rows:
        species_id = plant.get("Species ID", "")
        if species_id not in pollinator_species:
            continue
        review_rows.append(_review_row(plant))
        for pollinator_field in POLLINATOR_FIELDS:
            gap_rows.append(_gap_row(species_id, pollinator_field))

    diagnostics = (
        Diagnostic(
            code="pollinator_module_caveat",
            message=POLLINATOR_CAVEAT,
            severity=Severity.WARNING,
            context={
                "species_count": len(review_rows),
                "pollinator_gap_count": len(gap_rows),
            },
        ),
    )
    paths = _paths(output_dir)
    _write_csv(Path(paths["pollinator_review"]), review_rows, POLLINATOR_REVIEW_FIELDS)
    _write_csv(Path(paths["pollinator_evidence_gaps"]), gap_rows, POLLINATOR_GAP_FIELDS)
    _write_csv(
        Path(paths["pollinator_source_requirements"]),
        list(SOURCE_REQUIREMENTS),
        POLLINATOR_SOURCE_REQUIREMENT_FIELDS,
    )
    _write_csv(
        Path(paths["diagnostics"]),
        [diagnostic.to_dict() for diagnostic in diagnostics],
        DIAGNOSTIC_FIELDS,
    )
    _write_json(
        Path(paths["manifest"]),
        {
            "artifact_name": "Vancouver Pollinator Module",
            "input_usability_dir": str(usability_dir),
            "status": "pollinator_review_scaffold",
            "species_count": len(review_rows),
            "pollinator_gap_count": len(gap_rows),
            "source_requirement_count": len(SOURCE_REQUIREMENTS),
            "psi_policy": (
                "PSI remains not_ready until accepted field-level pollinator "
                "evidence exists for score inputs."
            ),
            "public_hygiene": {
                "raw_sources_tracked": False,
                "external_downloads_required": False,
                "private_data_tracked": False,
            },
            "caveat": POLLINATOR_CAVEAT,
        },
    )
    return validate_vancouver_pollinator_module(output_dir)


def validate_vancouver_pollinator_module(path: Path) -> PollinatorResult:
    """Validate generated Vancouver pollinator module artifacts."""
    diagnostics: list[Diagnostic] = []
    counts = _empty_counts()
    for filename in POLLINATOR_REQUIRED_FILES:
        if not (path / filename).exists():
            diagnostics.append(_diagnostic("missing_pollinator_file", field="path", value=filename))
    if diagnostics:
        return PollinatorResult(str(path), counts, tuple(diagnostics), {})

    review_rows = _load_csv(path / "pollinator_review.csv", diagnostics)
    gap_rows = _load_csv(path / "pollinator_evidence_gaps.csv", diagnostics)
    requirement_rows = _load_csv(path / "pollinator_source_requirements.csv", diagnostics)
    diagnostic_rows = _load_csv(path / "diagnostics.csv", diagnostics)
    manifest = _load_json(path / "manifest.json", diagnostics)

    counts.update(
        {
            "pollinator_review": len(review_rows),
            "pollinator_evidence_gaps": len(gap_rows),
            "pollinator_source_requirements": len(requirement_rows),
        }
    )
    species_ids = {row.get("species_id", "") for row in review_rows}
    diagnostics.extend(_validate_review_rows(review_rows))
    diagnostics.extend(_validate_gap_rows(gap_rows, species_ids))
    diagnostics.extend(_validate_requirement_rows(requirement_rows))
    diagnostics.extend(_validate_manifest(manifest, counts))
    diagnostics.extend(_validate_diagnostic_rows(diagnostic_rows))
    return PollinatorResult(str(path), counts, tuple(diagnostics), _paths(path))


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...]) -> bool:
    """Return whether diagnostics contain at least one error."""
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


def _review_row(plant: dict[str, str]) -> dict[str, str]:
    return {
        "species_id": plant.get("Species ID", ""),
        "botanical_name": plant.get("Botanical Name", ""),
        "common_name": plant.get("Common Name", ""),
        "family": plant.get("Family", ""),
        "review_status": "review_queue",
        "psi_readiness": "not_ready",
        "pollinator_queue_reason": (
            "Native Vancouver PoC species queued for field-level pollinator "
            "evidence review."
        ),
        "evidence_caveat": POLLINATOR_CAVEAT,
        "next_review_action": (
            "Add accepted source-attributed pollinator fields before calculating PSI."
        ),
    }


def _gap_row(species_id: str, pollinator_field: str) -> dict[str, str]:
    return {
        "species_id": species_id,
        "pollinator_field": pollinator_field,
        "current_value": "Unknown",
        "gap_type": "pollinator_field_needs_review",
        "required_evidence": (
            "Accepted source-attributed evidence is required before this field "
            "can become a candidate claim or score input."
        ),
        "review_status": "needs_review",
        "score_impact": "Blocks PSI readiness.",
    }


def _validate_review_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        species_id = row.get("species_id", "")
        if not SPECIES_ID_PATTERN.fullmatch(species_id):
            diagnostics.append(_diagnostic("invalid_species_id", index, "species_id", species_id))
        if species_id in seen:
            diagnostics.append(_diagnostic("duplicate_species_id", index, "species_id", species_id))
        seen.add(species_id)
        for field in POLLINATOR_REQUIRED_REVIEW_FIELDS:
            if not row.get(field):
                diagnostics.append(_diagnostic("missing_required_field", index, field))
        if row.get("review_status") not in REVIEW_STATUS_VALUES:
            diagnostics.append(
                _diagnostic(
                    "invalid_review_status",
                    index,
                    "review_status",
                    row.get("review_status"),
                )
            )
        if row.get("psi_readiness") not in PSI_READINESS_VALUES:
            diagnostics.append(
                _diagnostic(
                    "invalid_psi_readiness",
                    index,
                    "psi_readiness",
                    row.get("psi_readiness"),
                )
            )
        if row.get("psi_readiness") == "ready" and row.get("review_status") != "accepted":
            diagnostics.append(
                _diagnostic("psi_ready_without_accepted_review", index, "psi_readiness")
            )
    return diagnostics


def _validate_gap_rows(
    rows: list[dict[str, str]],
    species_ids: set[str],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    seen_pairs: set[tuple[str, str]] = set()
    for index, row in enumerate(rows, start=2):
        species_id = row.get("species_id", "")
        field = row.get("pollinator_field", "")
        if species_id not in species_ids:
            diagnostics.append(
                _diagnostic("unknown_gap_species_id", index, "species_id", species_id)
            )
        if field not in POLLINATOR_FIELDS:
            diagnostics.append(
                _diagnostic("invalid_pollinator_field", index, "pollinator_field", field)
            )
        pair = (species_id, field)
        if pair in seen_pairs:
            diagnostics.append(
                _diagnostic("duplicate_pollinator_gap", index, "pollinator_field", field)
            )
        seen_pairs.add(pair)
        if row.get("review_status") not in REVIEW_STATUS_VALUES:
            diagnostics.append(
                _diagnostic(
                    "invalid_review_status",
                    index,
                    "review_status",
                    row.get("review_status"),
                )
            )
        if row.get("review_status") == "accepted" and row.get("current_value") in {"", "Unknown"}:
            diagnostics.append(_diagnostic("accepted_gap_without_value", index, "current_value"))
    expected_gap_count = len(species_ids) * len(POLLINATOR_FIELDS)
    if len(rows) != expected_gap_count:
        diagnostics.append(
            Diagnostic(
                code="unexpected_gap_count",
                message=(
                    "Pollinator evidence gap row count does not match species x field "
                    "contract."
                ),
                severity=Severity.ERROR,
                context={"expected": expected_gap_count, "actual": len(rows)},
            )
        )
    return diagnostics


def _validate_requirement_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    fields = {row.get("pollinator_field", "") for row in rows}
    missing = sorted(set(POLLINATOR_FIELDS) - fields)
    for pollinator_field in missing:
        diagnostics.append(
            _diagnostic(
                "missing_source_requirement",
                field="pollinator_field",
                value=pollinator_field,
            )
        )
    for index, row in enumerate(rows, start=2):
        if row.get("pollinator_field") not in POLLINATOR_FIELDS:
            diagnostics.append(
                _diagnostic(
                    "invalid_requirement_field",
                    index,
                    "pollinator_field",
                    row.get("pollinator_field"),
                )
            )
        if row.get("minimum_review_status") != "accepted":
            diagnostics.append(
                _diagnostic(
                    "invalid_minimum_review_status",
                    index,
                    "minimum_review_status",
                    row.get("minimum_review_status"),
                )
            )
    return diagnostics


def _validate_manifest(manifest: dict[str, Any], counts: dict[str, int]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if manifest.get("status") != "pollinator_review_scaffold":
        diagnostics.append(_diagnostic("invalid_manifest_status", field="status"))
    if manifest.get("species_count") != counts["pollinator_review"]:
        diagnostics.append(_diagnostic("manifest_count_mismatch", field="species_count"))
    if manifest.get("pollinator_gap_count") != counts["pollinator_evidence_gaps"]:
        diagnostics.append(_diagnostic("manifest_count_mismatch", field="pollinator_gap_count"))
    if manifest.get("source_requirement_count") != counts["pollinator_source_requirements"]:
        diagnostics.append(_diagnostic("manifest_count_mismatch", field="source_requirement_count"))
    hygiene = manifest.get("public_hygiene", {})
    for field in ("raw_sources_tracked", "external_downloads_required", "private_data_tracked"):
        if hygiene.get(field) is not False:
            diagnostics.append(_diagnostic("invalid_public_hygiene_flag", field=field))
    return diagnostics


def _validate_diagnostic_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for index, row in enumerate(rows, start=2):
        if row.get("severity") == "error":
            diagnostics.append(
                _diagnostic(
                    "error_diagnostic_recorded",
                    index,
                    "severity",
                    row.get("code", ""),
                )
            )
    return diagnostics


def _load_csv(path: Path, diagnostics: list[Diagnostic]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    except OSError as exc:
        diagnostics.append(
            Diagnostic(
                code="csv_read_error",
                message=f"Could not read CSV file {path}: {exc}",
                severity=Severity.ERROR,
                value=str(path),
            )
        )
        return []


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: tuple[str, ...]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _load_json(path: Path, diagnostics: list[Diagnostic]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        diagnostics.append(
            Diagnostic(
                code="json_read_error",
                message=f"Could not read JSON file {path}: {exc}",
                severity=Severity.ERROR,
                value=str(path),
            )
        )
        return {}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _paths(path: Path) -> dict[str, str]:
    return {
        "pollinator_review": str(path / "pollinator_review.csv"),
        "pollinator_evidence_gaps": str(path / "pollinator_evidence_gaps.csv"),
        "pollinator_source_requirements": str(path / "pollinator_source_requirements.csv"),
        "manifest": str(path / "manifest.json"),
        "diagnostics": str(path / "diagnostics.csv"),
    }


def _empty_counts() -> dict[str, int]:
    return {
        "pollinator_review": 0,
        "pollinator_evidence_gaps": 0,
        "pollinator_source_requirements": 0,
    }


def _diagnostic(
    code: str,
    row_number: int | None = None,
    field: str | None = None,
    value: str | None = None,
) -> Diagnostic:
    messages = {
        "missing_pollinator_file": "Required pollinator artifact file is missing.",
        "invalid_species_id": "Species ID does not follow the BCNPPD-0001 convention.",
        "duplicate_species_id": "Species ID appears more than once.",
        "missing_required_field": "Required field is missing.",
        "invalid_review_status": "Review status is not allowed.",
        "invalid_psi_readiness": "PSI readiness is not allowed.",
        "psi_ready_without_accepted_review": "PSI cannot be ready without accepted review.",
        "unknown_gap_species_id": "Pollinator gap references an unknown species ID.",
        "invalid_pollinator_field": "Pollinator field is not part of the P11 contract.",
        "duplicate_pollinator_gap": "Pollinator evidence gap appears more than once.",
        "accepted_gap_without_value": "Accepted pollinator evidence cannot be Unknown or blank.",
        "missing_source_requirement": "Pollinator field is missing a source requirement.",
        "invalid_requirement_field": "Source requirement references an invalid pollinator field.",
        "invalid_minimum_review_status": (
            "Pollinator source requirements must require accepted review."
        ),
        "invalid_manifest_status": "Manifest status is not the pollinator module status.",
        "manifest_count_mismatch": "Manifest count does not match artifact rows.",
        "invalid_public_hygiene_flag": "Public hygiene manifest flag must be false.",
        "error_diagnostic_recorded": "Diagnostics artifact records an error.",
    }
    return Diagnostic(
        code=code,
        message=messages[code],
        severity=Severity.ERROR,
        row_number=row_number,
        field=field,
        value=value,
    )
