"""Approved provider sandbox integration for the Vancouver PoC."""

from __future__ import annotations

import csv
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .diagnostics import Diagnostic, Severity
from .evidence_hardening import generate_vancouver_evidence_hardening
from .pollinators import generate_vancouver_pollinator_module
from .providers import KNOWN_PROVIDER_IDS, MOWABILITY_VALUES
from .sources import (
    SPECIES_ID_PATTERN,
)
from .usability import generate_vancouver_usability
from .validate import diagnose_excluded_sources
from .vancouver_poc import (
    ATTRIBUTION_FIELDS,
    DIAGNOSTIC_FIELDS,
    POC_PLANT_COLUMNS,
    POC_REQUIRED_FILES,
    SOURCE_FIELDS,
    validate_vancouver_poc_list,
)

APPROVAL_STATUSES = {
    "approved",
    "rejected",
    "deferred",
    "needs_source_review",
    "needs_taxonomy_review",
}

IMPORTABLE_APPROVAL_STATUS = "approved"

APPROVAL_FIELDS = (
    "approval_id",
    "sandbox_table",
    "provider_id",
    "botanical_name",
    "common_name",
    "species_id",
    "approval_status",
    "target_action",
    "attribute_name",
    "attribute_value",
    "evidence_confidence",
    "source_url",
    "supplier_status",
    "product_url",
    "mowability_score",
    "reviewer",
    "review_date",
    "review_notes",
)

SUPPLIER_FIELDS = (
    "species_id",
    "provider_id",
    "botanical_name",
    "supplier_status",
    "product_url",
    "source_id",
    "review_status",
    "notes",
)

MOWABILITY_FIELDS = (
    "species_id",
    "provider_id",
    "botanical_name",
    "mowability_score",
    "source_url",
    "source_id",
    "review_status",
    "caveat",
    "notes",
)

PROVIDER_DATA_REQUIRED_FILES = (
    "approval_manifest.csv",
    "supplier_availability.csv",
    "mowability.csv",
    "manifest.json",
    "diagnostics.csv",
)

PROVIDER_APPROVAL_CAVEAT = (
    "Provider-approved observation remains candidate PoC data pending source, "
    "taxonomy, and ecological review."
)

MOWABILITY_CAVEAT = (
    "Mowability is a provisional 0-5 provider-derived candidate signal and does "
    "not make UNI, PSI, or RVI score inputs ready."
)


@dataclass(frozen=True)
class ProviderApprovalResult:
    """Provider approval validation or application summary."""

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


def validate_provider_approvals(path: Path) -> ProviderApprovalResult:
    """Validate a provider approval manifest file or provider-data directory."""
    diagnostics: list[Diagnostic] = []
    approval_path = _approval_manifest_path(path)
    counts = _empty_counts()
    paths = {"approval_manifest": str(approval_path)}
    if not approval_path.exists():
        diagnostics.append(
            _diagnostic(
                "missing_provider_approval_manifest",
                "Missing provider approval manifest.",
                field="path",
                value=str(approval_path),
            )
        )
        return ProviderApprovalResult(str(path), counts, tuple(diagnostics), paths)

    approval_rows = _load_csv(approval_path, diagnostics)
    counts["approval_manifest"] = len(approval_rows)
    counts["approved_rows"] = sum(
        1 for row in approval_rows if row.get("approval_status") == IMPORTABLE_APPROVAL_STATUS
    )
    diagnostics.extend(_validate_approval_rows(approval_rows, set()))

    if path.is_dir() and (path / "supplier_availability.csv").exists():
        supplier_rows = _load_csv(path / "supplier_availability.csv", diagnostics)
        mowability_rows = _load_csv(path / "mowability.csv", diagnostics)
        diagnostic_rows = _load_csv(path / "diagnostics.csv", diagnostics)
        manifest = _load_json(path / "manifest.json", diagnostics)
        counts.update(
            {
                "supplier_availability": len(supplier_rows),
                "mowability": len(mowability_rows),
            }
        )
        paths.update(_provider_data_paths(path))
        diagnostics.extend(_validate_supplier_rows(supplier_rows))
        diagnostics.extend(_validate_mowability_rows(mowability_rows))
        diagnostics.extend(_validate_provider_data_manifest(manifest, counts))
        diagnostics.extend(_validate_diagnostic_rows(diagnostic_rows))

    return ProviderApprovalResult(str(path), counts, tuple(diagnostics), paths)


def apply_provider_approvals(
    approvals_path: Path,
    poc_dir: Path,
    output_dir: Path,
    *,
    regenerate_downstream: bool = True,
) -> ProviderApprovalResult:
    """Apply approved provider observations to a Vancouver PoC artifact directory."""
    diagnostics: list[Diagnostic] = []
    approval_manifest = _approval_manifest_path(approvals_path)
    approval_rows = _load_csv(approval_manifest, diagnostics)
    existing_validation = validate_vancouver_poc_list(poc_dir)
    if _has_errors(existing_validation.diagnostics):
        return ProviderApprovalResult(
            str(output_dir),
            _empty_counts(),
            existing_validation.diagnostics,
            {},
        )

    plant_rows = _load_csv(poc_dir / "plant_list.csv", diagnostics)
    source_rows = _load_csv(poc_dir / "sources.csv", diagnostics)
    attribution_rows = _load_csv(poc_dir / "source_attribution.csv", diagnostics)
    species_ids = {row.get("Species ID", "") for row in plant_rows}
    diagnostics.extend(_validate_approval_rows(approval_rows, species_ids))
    if _has_errors(diagnostics):
        return ProviderApprovalResult(str(output_dir), _empty_counts(), tuple(diagnostics), {})

    output_dir.mkdir(parents=True, exist_ok=True)
    approved_rows = [
        row for row in approval_rows if row.get("approval_status") == IMPORTABLE_APPROVAL_STATUS
    ]
    species_by_name = {
        row.get("Botanical Name", "").casefold(): row
        for row in plant_rows
        if row.get("Botanical Name")
    }
    next_species_index = _next_numeric_id(plant_rows, "Species ID", "BCNPPD")
    next_legacy_index = _next_numeric_id(plant_rows, "Legacy ID", "CDF")
    source_registry = _source_registry(source_rows)
    supplier_rows: list[dict[str, str]] = []
    mowability_rows: list[dict[str, str]] = []
    provider_attribution_rows: list[dict[str, str]] = []

    for row in approved_rows:
        plant_row = _resolve_or_create_species(
            row,
            plant_rows,
            species_by_name,
            next_species_index,
            next_legacy_index,
        )
        if plant_row["Species ID"] == f"BCNPPD-{next_species_index:04d}":
            next_species_index += 1
            next_legacy_index += 1
        source = _resolve_source(row, source_registry)
        if source not in source_rows:
            source_rows.append(source)
        _append_primary_reference(plant_row, source["source_id"])
        table = row.get("sandbox_table", "")
        if table == "candidate_attributes.csv":
            attribution = _attribution_row(row, plant_row["Species ID"], source["source_id"])
            attribution_rows.append(attribution)
            provider_attribution_rows.append(attribution)
            _maybe_apply_candidate_attribute(plant_row, row)
        elif table == "supplier_availability.csv":
            supplier_rows.append(_supplier_row(row, plant_row["Species ID"], source["source_id"]))
            attribution = _attribution_row(
                row,
                plant_row["Species ID"],
                source["source_id"],
                claim_field="supplier_availability",
                claim_value=row.get("supplier_status", ""),
            )
            attribution_rows.append(attribution)
            provider_attribution_rows.append(attribution)
        elif table == "mowability.csv":
            mowability_rows.append(
                _mowability_row(row, plant_row["Species ID"], source["source_id"])
            )
            attribution = _attribution_row(
                row,
                plant_row["Species ID"],
                source["source_id"],
                claim_field="mowability_score",
                claim_value=row.get("mowability_score", ""),
            )
            attribution_rows.append(attribution)
            provider_attribution_rows.append(attribution)
        else:
            attribution = _attribution_row(
                row,
                plant_row["Species ID"],
                source["source_id"],
                claim_field="provider_candidate",
                claim_value=row.get("botanical_name", ""),
            )
            attribution_rows.append(attribution)
            provider_attribution_rows.append(attribution)

    plant_rows = sorted(plant_rows, key=lambda row: row.get("Botanical Name", "").casefold())
    source_rows = sorted(source_rows, key=lambda row: row.get("source_id", ""))
    attribution_rows = sorted(
        attribution_rows,
        key=lambda row: (
            row.get("species_id", ""),
            row.get("source_id", ""),
            row.get("claim_field", ""),
            row.get("claim_value", ""),
        ),
    )
    supplier_rows = sorted(
        supplier_rows,
        key=lambda row: (
            row.get("species_id", ""),
            row.get("provider_id", ""),
            row.get("product_url", ""),
        ),
    )
    mowability_rows = sorted(
        mowability_rows,
        key=lambda row: (
            row.get("species_id", ""),
            row.get("provider_id", ""),
            row.get("source_url", ""),
        ),
    )
    provider_attribution_rows = sorted(
        provider_attribution_rows,
        key=lambda row: (
            row.get("species_id", ""),
            row.get("source_id", ""),
            row.get("claim_field", ""),
        ),
    )

    _copy_poc_sidecars(poc_dir, output_dir)
    _write_csv(output_dir / "plant_list.csv", plant_rows, POC_PLANT_COLUMNS)
    _write_csv(output_dir / "sources.csv", source_rows, SOURCE_FIELDS)
    _write_csv(output_dir / "source_attribution.csv", attribution_rows, ATTRIBUTION_FIELDS)
    diagnostics.append(
        Diagnostic(
            code="provider_approvals_applied",
            message="Provider approvals were applied as candidate PoC observations.",
            severity=Severity.INFO,
            context={"approved_rows": len(approved_rows)},
        )
    )
    _write_csv(
        output_dir / "diagnostics.csv",
        [diagnostic.to_dict() for diagnostic in diagnostics],
        DIAGNOSTIC_FIELDS,
    )
    _write_json(
        output_dir / "manifest.json",
        _poc_manifest(poc_dir, plant_rows, source_rows, attribution_rows, len(approved_rows)),
    )
    provider_data_dir = output_dir / "provider_data"
    provider_data_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(provider_data_dir / "approval_manifest.csv", approval_rows, APPROVAL_FIELDS)
    _write_csv(provider_data_dir / "supplier_availability.csv", supplier_rows, SUPPLIER_FIELDS)
    _write_csv(provider_data_dir / "mowability.csv", mowability_rows, MOWABILITY_FIELDS)
    _write_csv(
        provider_data_dir / "diagnostics.csv", [d.to_dict() for d in diagnostics], DIAGNOSTIC_FIELDS
    )
    _write_json(
        provider_data_dir / "manifest.json",
        {
            "artifact_name": "Vancouver Provider Approval Data",
            "approval_manifest": str(approval_manifest),
            "approved_observation_count": len(approved_rows),
            "supplier_availability_count": len(supplier_rows),
            "mowability_count": len(mowability_rows),
            "source_attribution_count": len(provider_attribution_rows),
            "public_hygiene": {
                "raw_provider_html_tracked": False,
                "external_downloads_required": False,
                "private_data_tracked": False,
            },
            "caveat": PROVIDER_APPROVAL_CAVEAT,
        },
    )
    _write_csv(
        provider_data_dir / "source_attribution.csv",
        provider_attribution_rows,
        ATTRIBUTION_FIELDS,
    )

    validation = validate_vancouver_poc_list(output_dir)
    provider_validation = validate_provider_approvals(provider_data_dir)
    all_diagnostics = tuple(diagnostics) + validation.diagnostics + provider_validation.diagnostics
    if regenerate_downstream and not _has_errors(all_diagnostics):
        generate_vancouver_evidence_hardening(output_dir, output_dir / "evidence_hardening")
        generate_vancouver_usability(output_dir / "evidence_hardening", output_dir / "usability")
        generate_vancouver_pollinator_module(
            output_dir / "usability", output_dir / "pollinator_module"
        )

    counts = {
        "approval_manifest": len(approval_rows),
        "approved_rows": len(approved_rows),
        "plant_list": len(plant_rows),
        "sources": len(source_rows),
        "source_attribution": len(attribution_rows),
        "supplier_availability": len(supplier_rows),
        "mowability": len(mowability_rows),
    }
    return ProviderApprovalResult(
        str(output_dir),
        counts,
        all_diagnostics,
        {
            "plant_list": str(output_dir / "plant_list.csv"),
            "sources": str(output_dir / "sources.csv"),
            "source_attribution": str(output_dir / "source_attribution.csv"),
            "provider_data": str(provider_data_dir),
            **_provider_data_paths(provider_data_dir),
        },
    )


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...] | list[Diagnostic]) -> bool:
    """Return whether diagnostics include an error."""
    return _has_errors(diagnostics)


def _validate_approval_rows(
    rows: list[dict[str, str]],
    known_species_ids: set[str],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    seen_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        approval_id = row.get("approval_id", "").strip()
        status = row.get("approval_status", "").strip()
        provider_id = row.get("provider_id", "").strip()
        table = row.get("sandbox_table", "").strip()
        if not approval_id:
            diagnostics.append(_diagnostic("missing_approval_id", row_number, "approval_id"))
        elif approval_id in seen_ids:
            diagnostics.append(
                _diagnostic("duplicate_approval_id", row_number, "approval_id", approval_id)
            )
        seen_ids.add(approval_id)
        if status not in APPROVAL_STATUSES:
            diagnostics.append(
                _diagnostic("invalid_approval_status", row_number, "approval_status", status)
            )
        if provider_id not in KNOWN_PROVIDER_IDS:
            diagnostics.append(
                _diagnostic("unknown_provider_id", row_number, "provider_id", provider_id)
            )
        if not row.get("botanical_name", "").strip():
            diagnostics.append(_diagnostic("missing_botanical_name", row_number, "botanical_name"))
        if table not in {
            "candidate_species.csv",
            "candidate_attributes.csv",
            "supplier_availability.csv",
            "mowability.csv",
        }:
            diagnostics.append(
                _diagnostic("invalid_sandbox_table", row_number, "sandbox_table", table)
            )
        if status == IMPORTABLE_APPROVAL_STATUS:
            diagnostics.extend(_validate_approved_row(row, row_number, known_species_ids))
        diagnostics.extend(diagnose_excluded_sources([row]))
    return diagnostics


def _validate_approved_row(
    row: dict[str, str],
    row_number: int,
    known_species_ids: set[str],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    species_id = row.get("species_id", "").strip()
    target_action = row.get("target_action", "").strip()
    if species_id:
        if not SPECIES_ID_PATTERN.fullmatch(species_id):
            diagnostics.append(
                _diagnostic("invalid_species_id", row_number, "species_id", species_id)
            )
        elif known_species_ids and species_id not in known_species_ids:
            diagnostics.append(
                _diagnostic("unknown_species_id", row_number, "species_id", species_id)
            )
    elif target_action != "add_species":
        diagnostics.append(_diagnostic("missing_species_id", row_number, "species_id"))
    source_url = row.get("source_url", "").strip() or row.get("product_url", "").strip()
    if not source_url:
        diagnostics.append(_diagnostic("missing_provider_source_url", row_number, "source_url"))
    table = row.get("sandbox_table", "").strip()
    if table == "candidate_attributes.csv":
        if not row.get("attribute_name", "").strip():
            diagnostics.append(_diagnostic("missing_attribute_name", row_number, "attribute_name"))
        if not row.get("attribute_value", "").strip():
            diagnostics.append(
                _diagnostic("missing_attribute_value", row_number, "attribute_value")
            )
    if table == "supplier_availability.csv" and not row.get("supplier_status", "").strip():
        diagnostics.append(_diagnostic("missing_supplier_status", row_number, "supplier_status"))
    if (
        table == "mowability.csv"
        and row.get("mowability_score", "").strip() not in MOWABILITY_VALUES
    ):
        diagnostics.append(
            _diagnostic(
                "invalid_mowability_score",
                row_number,
                "mowability_score",
                row.get("mowability_score"),
            )
        )
    return diagnostics


def _validate_supplier_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        for field in (
            "species_id",
            "provider_id",
            "botanical_name",
            "supplier_status",
            "product_url",
            "source_id",
        ):
            if not row.get(field, "").strip():
                diagnostics.append(_diagnostic("missing_supplier_field", row_number, field))
        if row.get("species_id") and not SPECIES_ID_PATTERN.fullmatch(row["species_id"]):
            diagnostics.append(
                _diagnostic("invalid_species_id", row_number, "species_id", row["species_id"])
            )
    diagnostics.extend(diagnose_excluded_sources(rows))
    return diagnostics


def _validate_mowability_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        for field in (
            "species_id",
            "provider_id",
            "botanical_name",
            "mowability_score",
            "source_url",
            "source_id",
        ):
            if not row.get(field, "").strip():
                diagnostics.append(_diagnostic("missing_mowability_field", row_number, field))
        if row.get("mowability_score", "").strip() not in MOWABILITY_VALUES:
            diagnostics.append(
                _diagnostic(
                    "invalid_mowability_score",
                    row_number,
                    "mowability_score",
                    row.get("mowability_score"),
                )
            )
        if row.get("species_id") and not SPECIES_ID_PATTERN.fullmatch(row["species_id"]):
            diagnostics.append(
                _diagnostic("invalid_species_id", row_number, "species_id", row["species_id"])
            )
        if row.get("review_status") != "pending_review":
            diagnostics.append(
                _diagnostic("invalid_mowability_review_status", row_number, "review_status")
            )
    diagnostics.extend(diagnose_excluded_sources(rows))
    return diagnostics


def _validate_provider_data_manifest(
    manifest: dict[str, Any],
    counts: dict[str, int],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    expected = {
        "supplier_availability_count": counts.get("supplier_availability", 0),
        "mowability_count": counts.get("mowability", 0),
    }
    for field, expected_count in expected.items():
        if manifest.get(field) != expected_count:
            diagnostics.append(_diagnostic("provider_data_manifest_count_mismatch", field=field))
    hygiene = manifest.get("public_hygiene", {})
    if not isinstance(hygiene, dict) or hygiene.get("raw_provider_html_tracked") is not False:
        diagnostics.append(_diagnostic("invalid_provider_data_hygiene", field="public_hygiene"))
    return diagnostics


def _validate_diagnostic_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    return [
        _diagnostic(
            "provider_approval_diagnostics_contain_error", index, "severity", row.get("code")
        )
        for index, row in enumerate(rows, start=2)
        if row.get("severity") == Severity.ERROR.value
    ]


def _resolve_or_create_species(
    row: dict[str, str],
    plant_rows: list[dict[str, str]],
    species_by_name: dict[str, dict[str, str]],
    next_species_index: int,
    next_legacy_index: int,
) -> dict[str, str]:
    species_id = row.get("species_id", "").strip()
    if species_id:
        for plant_row in plant_rows:
            if plant_row.get("Species ID") == species_id:
                return plant_row
    botanical_name = row.get("botanical_name", "").strip()
    existing = species_by_name.get(botanical_name.casefold())
    if existing:
        return existing
    plant_row = {
        "Species ID": f"BCNPPD-{next_species_index:04d}",
        "Legacy ID": f"CDF-{next_legacy_index:04d}",
        "Botanical Name": botanical_name,
        "Common Name": row.get("common_name", "").strip(),
        "Family": "",
        "Native Status": "Pending review",
        "Plant Type": "",
        "Life Cycle": "",
        "Sun": "",
        "Soil Moisture": "",
        "Urban Toughness": "",
        "Evidence Level": "Pending review",
        "Primary References": "",
        "record_status": "poc_candidate",
        "evidence_status": "candidate_provider_approved",
        "poc_caveat": PROVIDER_APPROVAL_CAVEAT,
    }
    plant_rows.append(plant_row)
    species_by_name[botanical_name.casefold()] = plant_row
    return plant_row


def _source_registry(source_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    registry: dict[tuple[str, str], dict[str, str]] = {}
    for row in source_rows:
        registry[(row.get("source_name", "").casefold(), row.get("url", ""))] = row
    return registry


def _resolve_source(
    row: dict[str, str],
    registry: dict[tuple[str, str], dict[str, str]],
) -> dict[str, str]:
    provider_id = row.get("provider_id", "")
    provider_name = _provider_name(provider_id)
    url = row.get("source_url", "").strip() or row.get("product_url", "").strip()
    key = (provider_name.casefold(), url)
    if key in registry:
        return registry[key]
    source_id = _next_source_id(registry.values())
    source = {
        "source_id": source_id,
        "source_name": provider_name,
        "source_tier": "Tier 3",
        "citation": f"{provider_name}. Approved provider observation for Vancouver PoC sandbox.",
        "url": url,
        "external_id": f"provider:{provider_id}",
        "review_status": "pending_review",
        "notes": PROVIDER_APPROVAL_CAVEAT,
    }
    registry[key] = source
    return source


def _provider_name(provider_id: str) -> str:
    return {
        "PROV-SATIN": "Satinflower Nurseries",
        "PROV-NWM": "Northwest Meadowscapes",
        "PROV-WCS": "West Coast Seeds",
        "PROV-PREMIER": "Premier Pacific Seeds",
    }.get(provider_id, provider_id)


def _attribution_row(
    row: dict[str, str],
    species_id: str,
    source_id: str,
    *,
    claim_field: str | None = None,
    claim_value: str | None = None,
) -> dict[str, str]:
    return {
        "source_id": source_id,
        "species_id": species_id,
        "claim_field": claim_field or row.get("attribute_name", "") or row.get("sandbox_table", ""),
        "claim_value": claim_value if claim_value is not None else row.get("attribute_value", ""),
        "claim_scope": "species",
        "evidence_confidence": row.get("evidence_confidence", "").strip() or "Pending review",
        "external_id": f"provider_approval:{row.get('approval_id', '')}",
        "review_status": "pending_review",
        "notes": row.get("review_notes", "").strip() or PROVIDER_APPROVAL_CAVEAT,
    }


def _supplier_row(row: dict[str, str], species_id: str, source_id: str) -> dict[str, str]:
    return {
        "species_id": species_id,
        "provider_id": row.get("provider_id", ""),
        "botanical_name": row.get("botanical_name", ""),
        "supplier_status": row.get("supplier_status", ""),
        "product_url": row.get("product_url", "") or row.get("source_url", ""),
        "source_id": source_id,
        "review_status": "pending_review",
        "notes": row.get("review_notes", "") or PROVIDER_APPROVAL_CAVEAT,
    }


def _mowability_row(row: dict[str, str], species_id: str, source_id: str) -> dict[str, str]:
    return {
        "species_id": species_id,
        "provider_id": row.get("provider_id", ""),
        "botanical_name": row.get("botanical_name", ""),
        "mowability_score": row.get("mowability_score", ""),
        "source_url": row.get("source_url", "") or row.get("product_url", ""),
        "source_id": source_id,
        "review_status": "pending_review",
        "caveat": MOWABILITY_CAVEAT,
        "notes": row.get("review_notes", "") or PROVIDER_APPROVAL_CAVEAT,
    }


def _maybe_apply_candidate_attribute(plant_row: dict[str, str], row: dict[str, str]) -> None:
    field = _attribute_to_plant_field(row.get("attribute_name", ""))
    if not field:
        return
    current = plant_row.get(field, "").strip()
    if current and current not in {"Pending review", "Unknown"}:
        return
    plant_row[field] = row.get("attribute_value", "").strip()


def _attribute_to_plant_field(attribute_name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", attribute_name.casefold()).strip()
    return {
        "common name": "Common Name",
        "family": "Family",
        "native status": "Native Status",
        "plant type": "Plant Type",
        "life cycle": "Life Cycle",
        "sun": "Sun",
        "soil moisture": "Soil Moisture",
        "urban toughness": "Urban Toughness",
        "evidence level": "Evidence Level",
    }.get(normalized, "")


def _append_primary_reference(plant_row: dict[str, str], source_id: str) -> None:
    values = [value for value in plant_row.get("Primary References", "").split(";") if value]
    if source_id not in values:
        values.append(source_id)
    plant_row["Primary References"] = ";".join(values)


def _poc_manifest(
    source_poc_dir: Path,
    plant_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
    attribution_rows: list[dict[str, str]],
    approved_count: int,
) -> dict[str, object]:
    original = _load_json(source_poc_dir / "manifest.json", [])
    return {
        **original,
        "species_count": len(plant_rows),
        "source_count": len(source_rows),
        "source_attribution_count": len(attribution_rows),
        "provider_approved_observation_count": approved_count,
        "provider_data_dir": "provider_data",
        "caveat": (
            "PoC candidate list includes legacy workbook rows, user-submitted "
            "expansion candidates, and explicitly approved provider observations; "
            "use for inspection and prioritization, not final planting decisions."
        ),
    }


def _copy_poc_sidecars(poc_dir: Path, output_dir: Path) -> None:
    for filename in POC_REQUIRED_FILES:
        source = poc_dir / filename
        destination = output_dir / filename
        if source.exists() and source.resolve() != destination.resolve():
            shutil.copyfile(source, destination)
    requested = poc_dir / "requested_species_additions.csv"
    if requested.exists() and requested.resolve() != (output_dir / requested.name).resolve():
        shutil.copyfile(requested, output_dir / requested.name)


def _approval_manifest_path(path: Path) -> Path:
    return path / "approval_manifest.csv" if path.is_dir() else path


def _provider_data_paths(path: Path) -> dict[str, str]:
    return {
        "approval_manifest": str(path / "approval_manifest.csv"),
        "supplier_availability": str(path / "supplier_availability.csv"),
        "mowability": str(path / "mowability.csv"),
        "manifest": str(path / "manifest.json"),
        "diagnostics": str(path / "diagnostics.csv"),
    }


def _next_numeric_id(rows: list[dict[str, str]], field: str, prefix: str) -> int:
    pattern = re.compile(rf"^{prefix}-(\d{{4}})$")
    values = [
        int(match.group(1))
        for row in rows
        if (match := pattern.fullmatch(row.get(field, "").strip()))
    ]
    return max(values, default=0) + 1


def _next_source_id(rows: Any) -> str:
    pattern = re.compile(r"^SRC-(\d{4})$")
    values = [
        int(match.group(1))
        for row in rows
        if (match := pattern.fullmatch(row.get("source_id", "").strip()))
    ]
    return f"SRC-{max(values, default=0) + 1:04d}"


def _empty_counts() -> dict[str, int]:
    return {
        "approval_manifest": 0,
        "approved_rows": 0,
        "plant_list": 0,
        "sources": 0,
        "source_attribution": 0,
        "supplier_availability": 0,
        "mowability": 0,
    }


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _clean(row.get(field)) for field in fieldnames})


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_csv(path: Path, diagnostics: list[Diagnostic]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except OSError as exc:
        diagnostics.append(
            _diagnostic("provider_approval_csv_unreadable", field="path", value=f"{path}: {exc}")
        )
        return []


def _load_json(path: Path, diagnostics: list[Diagnostic]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _diagnostic(
    code: str,
    row_number: int | None = None,
    field: str | None = None,
    value: str | None = None,
    message: str | None = None,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        message=message or code.replace("_", " ").capitalize() + ".",
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


def _has_errors(diagnostics: tuple[Diagnostic, ...] | list[Diagnostic]) -> bool:
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)
