"""Vancouver plant list proof-of-concept generation and validation."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canonical import import_canonical_workbook
from .diagnostics import Diagnostic, Severity
from .sources import (
    SPECIES_ID_PATTERN,
    validate_source_attribution_records,
    validate_source_records,
)

POC_REQUIRED_FILES = (
    "plant_list.csv",
    "sources.csv",
    "source_attribution.csv",
    "manifest.json",
    "diagnostics.csv",
)

POC_PLANT_COLUMNS = (
    "Species ID",
    "Legacy ID",
    "Botanical Name",
    "Common Name",
    "Family",
    "Native Status",
    "Plant Type",
    "Life Cycle",
    "Sun",
    "Soil Moisture",
    "Urban Toughness",
    "Evidence Level",
    "Primary References",
    "record_status",
    "evidence_status",
    "poc_caveat",
)

SOURCE_FIELDS = (
    "source_id",
    "source_name",
    "source_tier",
    "citation",
    "url",
    "external_id",
    "review_status",
    "notes",
)

ATTRIBUTION_FIELDS = (
    "source_id",
    "species_id",
    "claim_field",
    "claim_value",
    "claim_scope",
    "evidence_confidence",
    "external_id",
    "review_status",
    "notes",
)

DIAGNOSTIC_FIELDS = ("severity", "code", "message", "row_number", "field", "value", "context")

POC_CAVEAT = (
    "PoC candidate row generated from the legacy workbook; use for inspection "
    "and prioritization, not final planting decisions."
)


@dataclass(frozen=True)
class VancouverPocResult:
    """Generated or validated Vancouver PoC artifact summary."""

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


def migrate_legacy_species_id(value: str) -> str:
    """Map legacy CDF IDs to stable BC-NPPD IDs."""
    text = value.strip()
    match = re.fullmatch(r"CDF-(\d{4})", text)
    if match:
        return f"BCNPPD-{match.group(1)}"
    return text


def generate_vancouver_poc_list(workbook_path: Path, output_dir: Path) -> VancouverPocResult:
    """Generate tracked Vancouver plant list PoC artifacts from a workbook."""
    import_result = import_canonical_workbook(workbook_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_registry: dict[tuple[str, str], dict[str, str]] = {}
    source_ids_by_legacy_species: dict[str, list[str]] = {}
    attribution_rows: list[dict[str, str]] = []

    for row in import_result.source_attribution:
        legacy_id = row.get("species_id", "")
        species_id = migrate_legacy_species_id(legacy_id)
        source = _source_record_for_row(row, source_registry)
        source_id = source["source_id"]
        source_ids_by_legacy_species.setdefault(legacy_id, [])
        if source_id not in source_ids_by_legacy_species[legacy_id]:
            source_ids_by_legacy_species[legacy_id].append(source_id)
        attribution_rows.append(
            {
                "source_id": source_id,
                "species_id": species_id,
                "claim_field": row.get("claim_field", ""),
                "claim_value": row.get("claim_scope", row.get("claim_value", "")),
                "claim_scope": "species",
                "evidence_confidence": row.get("evidence_confidence", "Pending review"),
                "external_id": row.get("external_id", ""),
                "review_status": "pending_review",
                "notes": row.get("notes", ""),
            }
        )

    plant_rows: list[dict[str, str]] = []
    for record in import_result.species:
        values = record.to_dict()
        legacy_id = values.get("Species ID", "")
        source_ids = source_ids_by_legacy_species.get(legacy_id, [])
        plant_rows.append(
            {
                "Species ID": migrate_legacy_species_id(legacy_id),
                "Legacy ID": legacy_id,
                "Botanical Name": values.get("Botanical Name", ""),
                "Common Name": values.get("Common Name", ""),
                "Family": values.get("Family", ""),
                "Native Status": values.get("Native Status", ""),
                "Plant Type": values.get("Plant Type", ""),
                "Life Cycle": values.get("Life Cycle", ""),
                "Sun": values.get("Sun", ""),
                "Soil Moisture": values.get("Soil Moisture", ""),
                "Urban Toughness": values.get("Urban Toughness", ""),
                "Evidence Level": values.get("Evidence Level", ""),
                "Primary References": ";".join(source_ids),
                "record_status": "poc_candidate",
                "evidence_status": "candidate_attributed",
                "poc_caveat": POC_CAVEAT,
            }
        )

    sources = sorted(source_registry.values(), key=lambda source: source["source_id"])
    diagnostics = (
        Diagnostic(
            code="poc_candidate_caveat",
            message="Vancouver PoC list is caveated and not a final reviewed planting list.",
            severity=Severity.WARNING,
            context={"species_count": len(plant_rows)},
        ),
    )

    paths = {
        "plant_list": str(output_dir / "plant_list.csv"),
        "sources": str(output_dir / "sources.csv"),
        "source_attribution": str(output_dir / "source_attribution.csv"),
        "manifest": str(output_dir / "manifest.json"),
        "diagnostics": str(output_dir / "diagnostics.csv"),
    }
    _write_csv(Path(paths["plant_list"]), plant_rows, POC_PLANT_COLUMNS)
    _write_csv(Path(paths["sources"]), sources, SOURCE_FIELDS)
    _write_csv(Path(paths["source_attribution"]), attribution_rows, ATTRIBUTION_FIELDS)
    _write_csv(
        Path(paths["diagnostics"]),
        [diagnostic.to_dict() for diagnostic in diagnostics],
        DIAGNOSTIC_FIELDS,
    )
    _write_json(
        Path(paths["manifest"]),
        {
            "poc_name": "Vancouver Plant List PoC",
            "source_workbook": str(workbook_path),
            "status": "poc_candidate",
            "species_count": len(plant_rows),
            "source_count": len(sources),
            "source_attribution_count": len(attribution_rows),
            "legacy_id_policy": "CDF-0001 maps to BCNPPD-0001; legacy ID retained.",
            "public_hygiene": {
                "raw_sources_tracked": False,
                "generated_from_tracked_workbook": True,
                "external_downloads_required": False,
                "private_data_tracked": False,
            },
            "caveat": POC_CAVEAT,
        },
    )

    validation = validate_vancouver_poc_list(output_dir)
    return VancouverPocResult(
        path=str(output_dir),
        counts=validation.counts,
        diagnostics=validation.diagnostics,
        paths=paths,
    )


def validate_vancouver_poc_list(path: Path) -> VancouverPocResult:
    """Validate a generated Vancouver PoC artifact directory."""
    diagnostics: list[Diagnostic] = []
    counts = {"plant_list": 0, "sources": 0, "source_attribution": 0}
    for filename in POC_REQUIRED_FILES:
        if not (path / filename).exists():
            diagnostics.append(_diagnostic("missing_poc_file", field="path", value=filename))
    if diagnostics:
        return VancouverPocResult(str(path), counts, tuple(diagnostics), {})

    plant_rows = _load_csv(path / "plant_list.csv", diagnostics)
    source_rows = _load_csv(path / "sources.csv", diagnostics)
    attribution_rows = _load_csv(path / "source_attribution.csv", diagnostics)
    diagnostic_rows = _load_csv(path / "diagnostics.csv", diagnostics)
    manifest = _load_json(path / "manifest.json", diagnostics)

    counts.update(
        {
            "plant_list": len(plant_rows),
            "sources": len(source_rows),
            "source_attribution": len(attribution_rows),
        }
    )
    diagnostics.extend(_validate_manifest(manifest, plant_rows, source_rows, attribution_rows))
    diagnostics.extend(_validate_plant_rows(plant_rows))
    diagnostics.extend(validate_source_records(source_rows))
    diagnostics.extend(validate_source_attribution_records(attribution_rows))
    diagnostics.extend(_validate_links(plant_rows, source_rows, attribution_rows))
    diagnostics.extend(_validate_diagnostic_rows(diagnostic_rows))

    return VancouverPocResult(
        path=str(path),
        counts=counts,
        diagnostics=tuple(diagnostics),
        paths={
            filename.removesuffix(".csv").removesuffix(".json"): str(path / filename)
            for filename in POC_REQUIRED_FILES
        },
    )


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...]) -> bool:
    """Return whether diagnostics contain at least one error."""
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


def _source_record_for_row(
    row: dict[str, str],
    source_registry: dict[tuple[str, str], dict[str, str]],
) -> dict[str, str]:
    source_name = row.get("Source_Name", "").strip() or "Unspecified workbook source"
    url = row.get("URL", "").strip()
    key = (source_name.casefold(), url)
    if key in source_registry:
        return source_registry[key]
    source_id = f"SRC-{len(source_registry) + 1:04d}"
    source_registry[key] = {
        "source_id": source_id,
        "source_name": source_name,
        "source_tier": row.get("Source_Tier", "").strip() or "Tier 3",
        "citation": f"{source_name}. Candidate source from legacy workbook attribution.",
        "url": url,
        "external_id": "",
        "review_status": "pending_review",
        "notes": row.get("notes", ""),
    }
    return source_registry[key]


def _validate_plant_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        species_id = row.get("Species ID", "")
        legacy_id = row.get("Legacy ID", "")
        if not SPECIES_ID_PATTERN.fullmatch(species_id):
            diagnostics.append(
                _diagnostic("invalid_species_id", row_number, "Species ID", species_id)
            )
        if not re.fullmatch(r"CDF-\d{4}", legacy_id):
            diagnostics.append(
                _diagnostic("invalid_legacy_species_id", row_number, "Legacy ID", legacy_id)
            )
        if migrate_legacy_species_id(legacy_id) != species_id:
            diagnostics.append(
                _diagnostic("legacy_id_mismatch", row_number, "Legacy ID", legacy_id)
            )
        if row.get("record_status") != "poc_candidate":
            diagnostics.append(_diagnostic("invalid_record_status", row_number, "record_status"))
        if not row.get("poc_caveat"):
            diagnostics.append(_diagnostic("missing_poc_caveat", row_number, "poc_caveat"))
    return diagnostics


def _validate_links(
    plant_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
    attribution_rows: list[dict[str, str]],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    species_ids = {row.get("Species ID", "") for row in plant_rows}
    source_ids = {row.get("source_id", "") for row in source_rows}
    for row_number, row in enumerate(attribution_rows, start=2):
        if row.get("species_id") not in species_ids:
            diagnostics.append(
                _diagnostic(
                    "unknown_poc_species_id",
                    row_number,
                    "species_id",
                    row.get("species_id"),
                )
            )
        if row.get("source_id") not in source_ids:
            diagnostics.append(
                _diagnostic("unknown_poc_source_id", row_number, "source_id", row.get("source_id"))
            )
    for row_number, row in enumerate(plant_rows, start=2):
        for source_id in row.get("Primary References", "").split(";"):
            if source_id and source_id not in source_ids:
                diagnostics.append(
                    _diagnostic(
                        "unknown_primary_reference",
                        row_number,
                        "Primary References",
                        source_id,
                    )
                )
    return diagnostics


def _validate_manifest(
    manifest: dict[str, Any],
    plant_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
    attribution_rows: list[dict[str, str]],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    expected = {
        "species_count": len(plant_rows),
        "source_count": len(source_rows),
        "source_attribution_count": len(attribution_rows),
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
        hygiene.get("external_downloads_required") is not False
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
                    "poc_diagnostics_contain_error",
                    row_number,
                    "severity",
                    row.get("code"),
                )
            )
    return diagnostics


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
        diagnostics.append(_diagnostic("poc_csv_unreadable", field="path", value=f"{path}: {exc}"))
        return []


def _load_json(path: Path, diagnostics: list[Diagnostic]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        diagnostics.append(_diagnostic("poc_json_unreadable", field="path", value=f"{path}: {exc}"))
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
