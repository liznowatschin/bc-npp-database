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
from .providers import KNOWN_PROVIDER_IDS, MOWABILITY_VALUES, validate_provider_sandbox
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
    "candidate_status",
    "vancouver_eligibility_status",
    "product_category",
    "candidate_reason",
    "sandbox_review_status",
    "sandbox_notes",
)

PROVIDER_CANDIDATE_SPECIES_FIELDS = (
    "species_id",
    "provider_id",
    "botanical_name",
    "common_name",
    "candidate_status",
    "vancouver_eligibility_status",
    "source_url",
    "source_id",
    "product_url",
    "product_category",
    "candidate_reason",
    "review_status",
    "notes",
    "approval_id",
)

PROVIDER_CANDIDATE_ATTRIBUTE_FIELDS = (
    "species_id",
    "provider_id",
    "botanical_name",
    "attribute_name",
    "attribute_value",
    "evidence_confidence",
    "source_url",
    "source_id",
    "review_status",
    "notes",
    "approval_id",
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
    "candidate_species.csv",
    "candidate_attributes.csv",
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
                field="path",
                value=str(approval_path),
                message="Missing provider approval manifest.",
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
        diagnostics.extend(_validate_provider_data_files(path))
        candidate_species_rows = _load_csv(path / "candidate_species.csv", diagnostics)
        candidate_attribute_rows = _load_csv(path / "candidate_attributes.csv", diagnostics)
        supplier_rows = _load_csv(path / "supplier_availability.csv", diagnostics)
        mowability_rows = _load_csv(path / "mowability.csv", diagnostics)
        diagnostic_rows = _load_csv(path / "diagnostics.csv", diagnostics)
        manifest = _load_json(path / "manifest.json", diagnostics)
        counts.update(
            {
                "candidate_species": len(candidate_species_rows),
                "candidate_attributes": len(candidate_attribute_rows),
                "supplier_availability": len(supplier_rows),
                "mowability": len(mowability_rows),
            }
        )
        paths.update(_provider_data_paths(path))
        diagnostics.extend(_validate_candidate_species_rows(candidate_species_rows))
        diagnostics.extend(_validate_candidate_attribute_rows(candidate_attribute_rows))
        diagnostics.extend(_validate_supplier_rows(supplier_rows))
        diagnostics.extend(_validate_mowability_rows(mowability_rows))
        diagnostics.extend(_validate_provider_data_manifest(manifest, counts))
        diagnostics.extend(_validate_diagnostic_rows(diagnostic_rows))

    return ProviderApprovalResult(str(path), counts, tuple(diagnostics), paths)


def auto_approve_provider_manifest(
    approvals_path: Path,
    output_path: Path,
    *,
    approve_rejected: bool = False,
    reviewer: str = "auto-approve (greedy mode)",
) -> ProviderApprovalResult:
    """Write an all-included provider approval manifest from a draft manifest.

    This is the manifest equivalent of approving every species in the static
    review app and checking supplier, attributes, and mowability inclusion for
    every approved species. Explicitly rejected rows stay rejected unless
    ``approve_rejected`` is true.
    """
    diagnostics: list[Diagnostic] = []
    approval_manifest = _approval_manifest_path(approvals_path)
    approval_rows = _load_csv(approval_manifest, diagnostics)
    if diagnostics:
        return ProviderApprovalResult(str(output_path), _empty_counts(), tuple(diagnostics), {})

    approved_rows: list[dict[str, str]] = []
    approved_count = 0
    rejected_preserved_count = 0
    for row in approval_rows:
        copied = {field: row.get(field, "") for field in APPROVAL_FIELDS}
        original_status = copied.get("approval_status", "").strip()
        if original_status == "rejected" and not approve_rejected:
            rejected_preserved_count += 1
        else:
            copied["approval_status"] = IMPORTABLE_APPROVAL_STATUS
            copied["reviewer"] = copied.get("reviewer") or reviewer
            copied["review_notes"] = _auto_approval_note(copied)
            approved_count += 1
        approved_rows.append(copied)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(output_path, approved_rows, APPROVAL_FIELDS)
    validation = validate_provider_approvals(output_path)
    diagnostics.extend(validation.diagnostics)
    diagnostics.append(
        Diagnostic(
            code="provider_manifest_auto_approved",
            message="Provider approval manifest was converted to all-included auto-approval.",
            severity=Severity.INFO,
            context={
                "input_rows": len(approval_rows),
                "approved_rows": approved_count,
                "rejected_rows_preserved": rejected_preserved_count,
                "approve_rejected": approve_rejected,
            },
        )
    )
    counts = {
        **validation.counts,
        "auto_approved_rows": approved_count,
        "rejected_rows_preserved": rejected_preserved_count,
    }
    return ProviderApprovalResult(
        str(output_path),
        counts,
        tuple(diagnostics),
        {"approval_manifest": str(output_path)},
    )


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

    provider_data_input = poc_dir / "provider_data"
    existing_approval_rows = (
        _load_csv(provider_data_input / "approval_manifest.csv", diagnostics)
        if (provider_data_input / "approval_manifest.csv").exists()
        else []
    )
    supplier_rows = (
        _load_csv(provider_data_input / "supplier_availability.csv", diagnostics)
        if (provider_data_input / "supplier_availability.csv").exists()
        else []
    )
    provider_candidate_species_rows = (
        _load_csv(provider_data_input / "candidate_species.csv", diagnostics)
        if (provider_data_input / "candidate_species.csv").exists()
        else []
    )
    provider_candidate_attribute_rows = (
        _load_csv(provider_data_input / "candidate_attributes.csv", diagnostics)
        if (provider_data_input / "candidate_attributes.csv").exists()
        else []
    )
    mowability_rows = (
        _load_csv(provider_data_input / "mowability.csv", diagnostics)
        if (provider_data_input / "mowability.csv").exists()
        else []
    )
    provider_attribution_rows = (
        _load_csv(provider_data_input / "source_attribution.csv", diagnostics)
        if (provider_data_input / "source_attribution.csv").exists()
        else []
    )
    approval_rows = _namespace_colliding_approval_ids(approval_rows, existing_approval_rows)
    approved_rows = [
        row for row in approval_rows if row.get("approval_status") == IMPORTABLE_APPROVAL_STATUS
    ]

    output_dir.mkdir(parents=True, exist_ok=True)
    species_by_name = {
        row.get("Botanical Name", "").casefold(): row
        for row in plant_rows
        if row.get("Botanical Name")
    }
    next_species_index = _next_numeric_id(plant_rows, "Species ID", "BCNPPD")
    next_legacy_index = _next_numeric_id(plant_rows, "Legacy ID", "CDF")
    source_registry = _source_registry(source_rows)

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
            provider_candidate_attribute_rows.append(
                _candidate_attribute_row(row, plant_row["Species ID"], source["source_id"])
            )
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
            provider_candidate_species_rows.append(
                _candidate_species_row(row, plant_row["Species ID"], source["source_id"])
            )
            attribution = _attribution_row(
                row,
                plant_row["Species ID"],
                source["source_id"],
                claim_field="provider_candidate",
                claim_value=row.get("botanical_name", ""),
            )
            attribution_rows.append(attribution)
            provider_attribution_rows.append(attribution)

    attribution_rows = _dedupe_rows(attribution_rows, _ATTRIBUTION_KEY)
    provider_candidate_species_rows = _dedupe_rows(
        provider_candidate_species_rows, _PROVIDER_CANDIDATE_SPECIES_KEY
    )
    provider_candidate_attribute_rows = _dedupe_rows(
        provider_candidate_attribute_rows, _PROVIDER_CANDIDATE_ATTRIBUTE_KEY
    )
    supplier_rows = _dedupe_rows(supplier_rows, _SUPPLIER_KEY)
    mowability_rows = _dedupe_rows(mowability_rows, _MOWABILITY_KEY)
    provider_attribution_rows = _dedupe_rows(provider_attribution_rows, _ATTRIBUTION_KEY)

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
    provider_candidate_species_rows = sorted(
        provider_candidate_species_rows,
        key=lambda row: (
            row.get("species_id", ""),
            row.get("provider_id", ""),
            row.get("source_url", ""),
        ),
    )
    provider_candidate_attribute_rows = sorted(
        provider_candidate_attribute_rows,
        key=lambda row: (
            row.get("species_id", ""),
            row.get("provider_id", ""),
            row.get("source_url", ""),
            row.get("attribute_name", ""),
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
    provider_data_dir = output_dir / "provider_data"
    provider_data_dir.mkdir(parents=True, exist_ok=True)
    combined_approval_rows = [*existing_approval_rows, *approval_rows]
    combined_approved_count = sum(
        1
        for row in combined_approval_rows
        if row.get("approval_status") == IMPORTABLE_APPROVAL_STATUS
    )
    _write_json(
        output_dir / "manifest.json",
        _poc_manifest(
            poc_dir,
            plant_rows,
            source_rows,
            attribution_rows,
            combined_approved_count,
        ),
    )
    _write_csv(
        provider_data_dir / "approval_manifest.csv",
        combined_approval_rows,
        APPROVAL_FIELDS,
    )
    _write_csv(
        provider_data_dir / "candidate_species.csv",
        provider_candidate_species_rows,
        PROVIDER_CANDIDATE_SPECIES_FIELDS,
    )
    _write_csv(
        provider_data_dir / "candidate_attributes.csv",
        provider_candidate_attribute_rows,
        PROVIDER_CANDIDATE_ATTRIBUTE_FIELDS,
    )
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
            "approved_observation_count": combined_approved_count,
            "candidate_species_count": len(provider_candidate_species_rows),
            "candidate_attribute_count": len(provider_candidate_attribute_rows),
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
        "approval_manifest": len(combined_approval_rows),
        "approved_rows": combined_approved_count,
        "plant_list": len(plant_rows),
        "sources": len(source_rows),
        "source_attribution": len(attribution_rows),
        "candidate_species": len(provider_candidate_species_rows),
        "candidate_attributes": len(provider_candidate_attribute_rows),
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


def apply_provider_approval_sequence(
    approvals_paths: list[Path],
    poc_dir: Path,
    output_dir: Path,
    *,
    regenerate_downstream: bool = True,
) -> ProviderApprovalResult:
    """Apply multiple approval manifests cumulatively to a Vancouver PoC directory."""
    if not approvals_paths:
        return ProviderApprovalResult(
            str(output_dir),
            _empty_counts(),
            (
                Diagnostic(
                    code="approval_sequence_empty",
                    message="At least one provider approval manifest is required.",
                    severity=Severity.ERROR,
                    field="approvals_paths",
                ),
            ),
            {},
        )

    steps_dir = output_dir.parent / f".{output_dir.name}_approval_steps"
    if steps_dir.exists():
        shutil.rmtree(steps_dir)
    steps_dir.mkdir(parents=True, exist_ok=True)

    current_base = poc_dir
    result = ProviderApprovalResult(str(output_dir), _empty_counts(), (), {})
    for index, approvals_path in enumerate(approvals_paths, start=1):
        is_last = index == len(approvals_paths)
        step_output = output_dir if is_last else steps_dir / f"step_{index:02d}"
        result = apply_provider_approvals(
            approvals_path,
            current_base,
            step_output,
            regenerate_downstream=regenerate_downstream if is_last else False,
        )
        if _has_errors(result.diagnostics):
            return result
        current_base = step_output
    return result


def apply_provider_sandbox_sequence(
    sandbox_dirs: list[Path],
    poc_dir: Path,
    output_dir: Path,
    *,
    regenerate_downstream: bool = True,
) -> ProviderApprovalResult:
    """Apply multiple provider sandboxes cumulatively with auto-approval."""
    if not sandbox_dirs:
        return ProviderApprovalResult(
            str(output_dir),
            _empty_counts(),
            (
                Diagnostic(
                    code="provider_sandbox_sequence_empty",
                    message="At least one provider sandbox directory is required.",
                    severity=Severity.ERROR,
                    field="sandbox_dirs",
                ),
            ),
            {},
        )

    steps_dir = output_dir.parent / f".{output_dir.name}_sandbox_steps"
    if steps_dir.exists():
        shutil.rmtree(steps_dir)
    steps_dir.mkdir(parents=True, exist_ok=True)

    current_base = poc_dir
    result = ProviderApprovalResult(str(output_dir), _empty_counts(), (), {})
    diagnostics: list[Diagnostic] = []
    sequence_counts = {
        "sequence_sandbox_species": 0,
        "sequence_eligible_species": 0,
        "sequence_excluded_species": 0,
        "sequence_auto_approval_rows": 0,
        "sequence_supplier_included": 0,
        "sequence_attribute_included": 0,
        "sequence_mowability_included": 0,
    }
    for index, sandbox_dir in enumerate(sandbox_dirs, start=1):
        is_last = index == len(sandbox_dirs)
        step_output = output_dir if is_last else steps_dir / f"step_{index:02d}"
        result = apply_provider_sandbox(
            sandbox_dir,
            current_base,
            step_output,
            regenerate_downstream=regenerate_downstream if is_last else False,
        )
        diagnostics.extend(result.diagnostics)
        sequence_counts["sequence_sandbox_species"] += result.counts.get("sandbox_species", 0)
        sequence_counts["sequence_eligible_species"] += result.counts.get("eligible_species", 0)
        sequence_counts["sequence_excluded_species"] += result.counts.get("excluded_species", 0)
        sequence_counts["sequence_auto_approval_rows"] += result.counts.get(
            "auto_approval_rows", result.counts.get("approval_manifest", 0)
        )
        sequence_counts["sequence_supplier_included"] += result.counts.get(
            "supplier_included", 0
        )
        sequence_counts["sequence_attribute_included"] += result.counts.get(
            "attribute_included", 0
        )
        sequence_counts["sequence_mowability_included"] += result.counts.get(
            "mowability_included", 0
        )
        if _has_errors(result.diagnostics):
            return ProviderApprovalResult(
                result.path,
                {**result.counts, **sequence_counts},
                tuple(diagnostics),
                result.paths,
            )
        current_base = step_output
    return ProviderApprovalResult(
        result.path,
        {**result.counts, **sequence_counts},
        tuple(diagnostics),
        result.paths,
    )


def auto_import_provider_sandboxes(
    provider_ids: list[str],
    poc_dir: Path,
    output_dir: Path,
    *,
    sandbox_root: Path,
    input_dir: Path | None = None,
    live_fetch: bool = False,
    source_sweep: bool = True,
    max_pages: int = 5,
    regenerate_downstream: bool = True,
) -> ProviderApprovalResult:
    """Scrape provider sandboxes and auto-apply them cumulatively."""
    if not provider_ids:
        return ProviderApprovalResult(
            str(output_dir),
            _empty_counts(),
            (
                Diagnostic(
                    code="provider_auto_import_empty",
                    message="At least one provider ID is required.",
                    severity=Severity.ERROR,
                    field="provider_ids",
                ),
            ),
            {},
        )

    from .provider_scraping import has_error_diagnostics as has_scrape_errors
    from .provider_scraping import scrape_provider_sandbox

    diagnostics: list[Diagnostic] = []
    sandbox_dirs: list[Path] = []
    scrape_counts: dict[str, int] = {}
    paths: dict[str, str] = {}
    for provider_id in provider_ids:
        sandbox_dir = sandbox_root / provider_id
        scrape_result = scrape_provider_sandbox(
            provider_id,
            "vancouver",
            sandbox_dir,
            input_dir=input_dir,
            live_fetch=live_fetch,
            source_sweep=source_sweep,
            max_pages=max_pages,
        )
        diagnostics.extend(scrape_result.diagnostics)
        paths[f"{provider_id}_sandbox"] = scrape_result.path
        scrape_counts[f"{provider_id}_candidate_species"] = scrape_result.counts.get(
            "candidate_species", 0
        )
        if has_scrape_errors(scrape_result.diagnostics):
            return ProviderApprovalResult(
                str(output_dir),
                {**_empty_counts(), **scrape_counts},
                tuple(diagnostics),
                paths,
            )
        sandbox_dirs.append(sandbox_dir)

    apply_result = apply_provider_sandbox_sequence(
        sandbox_dirs,
        poc_dir,
        output_dir,
        regenerate_downstream=regenerate_downstream,
    )
    return ProviderApprovalResult(
        str(output_dir),
        {**scrape_counts, **apply_result.counts},
        tuple(diagnostics) + apply_result.diagnostics,
        {**paths, **apply_result.paths},
    )


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...] | list[Diagnostic]) -> bool:
    """Return whether diagnostics include an error."""
    return _has_errors(diagnostics)


def _namespace_colliding_approval_ids(
    rows: list[dict[str, str]],
    existing_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    used_ids = {
        row.get("approval_id", "").strip()
        for row in existing_rows
        if row.get("approval_id", "").strip()
    }
    namespaced_rows: list[dict[str, str]] = []
    for row in rows:
        copied = dict(row)
        approval_id = copied.get("approval_id", "").strip()
        provider_id = copied.get("provider_id", "").strip()
        if approval_id in used_ids and provider_id:
            candidate = f"{provider_id}-{approval_id}"
            suffix = 2
            while candidate in used_ids:
                candidate = f"{provider_id}-{approval_id}-{suffix}"
                suffix += 1
            copied["approval_id"] = candidate
            approval_id = candidate
        if approval_id:
            used_ids.add(approval_id)
        namespaced_rows.append(copied)
    return namespaced_rows


def _dedupe_rows(
    rows: list[dict[str, str]],
    key_fields: tuple[str, ...],
) -> list[dict[str, str]]:
    seen: set[tuple[str, ...]] = set()
    deduped: list[dict[str, str]] = []
    for row in rows:
        key = tuple(row.get(field, "") for field in key_fields)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


_SUPPLIER_KEY = ("species_id", "provider_id", "product_url", "supplier_status")
_MOWABILITY_KEY = ("species_id", "provider_id", "source_url", "mowability_score")
_PROVIDER_CANDIDATE_SPECIES_KEY = (
    "species_id",
    "provider_id",
    "source_url",
    "approval_id",
)
_PROVIDER_CANDIDATE_ATTRIBUTE_KEY = (
    "species_id",
    "provider_id",
    "source_url",
    "attribute_name",
    "attribute_value",
    "approval_id",
)
_ATTRIBUTION_KEY = (
    "species_id",
    "source_id",
    "claim_field",
    "claim_value",
    "evidence_confidence",
    "review_status",
)


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


def _validate_candidate_species_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        for field in (
            "species_id",
            "provider_id",
            "botanical_name",
            "source_url",
            "source_id",
            "approval_id",
        ):
            if not row.get(field, "").strip():
                diagnostics.append(
                    _diagnostic("missing_candidate_species_field", row_number, field)
                )
        if row.get("species_id") and not SPECIES_ID_PATTERN.fullmatch(row["species_id"]):
            diagnostics.append(
                _diagnostic("invalid_species_id", row_number, "species_id", row["species_id"])
            )
    diagnostics.extend(diagnose_excluded_sources(rows))
    return diagnostics


def _validate_candidate_attribute_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        for field in (
            "species_id",
            "provider_id",
            "botanical_name",
            "attribute_name",
            "attribute_value",
            "source_url",
            "source_id",
            "approval_id",
        ):
            if not row.get(field, "").strip():
                diagnostics.append(
                    _diagnostic("missing_candidate_attribute_field", row_number, field)
                )
        if row.get("species_id") and not SPECIES_ID_PATTERN.fullmatch(row["species_id"]):
            diagnostics.append(
                _diagnostic("invalid_species_id", row_number, "species_id", row["species_id"])
            )
    diagnostics.extend(diagnose_excluded_sources(rows))
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
        "candidate_species_count": counts.get("candidate_species", 0),
        "candidate_attribute_count": counts.get("candidate_attributes", 0),
        "supplier_availability_count": counts.get("supplier_availability", 0),
        "mowability_count": counts.get("mowability", 0),
    }
    for field, expected_count in expected.items():
        if field in manifest and manifest.get(field) != expected_count:
            diagnostics.append(_diagnostic("provider_data_manifest_count_mismatch", field=field))
    hygiene = manifest.get("public_hygiene", {})
    if not isinstance(hygiene, dict) or hygiene.get("raw_provider_html_tracked") is not False:
        diagnostics.append(_diagnostic("invalid_provider_data_hygiene", field="public_hygiene"))
    return diagnostics


def _validate_provider_data_files(path: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for filename in PROVIDER_DATA_REQUIRED_FILES:
        file_path = path / filename
        if not file_path.exists():
            diagnostics.append(
                _diagnostic(
                    "missing_provider_data_file",
                    field="path",
                    value=str(file_path),
                    message=f"Missing provider-data file: {filename}.",
                )
            )
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
        "PROV-OAKSUMMIT": "Oak Summit Nursery",
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


def _candidate_species_row(
    row: dict[str, str], species_id: str, source_id: str
) -> dict[str, str]:
    return {
        "species_id": species_id,
        "provider_id": row.get("provider_id", ""),
        "botanical_name": row.get("botanical_name", ""),
        "common_name": row.get("common_name", ""),
        "candidate_status": row.get("candidate_status", ""),
        "vancouver_eligibility_status": row.get("vancouver_eligibility_status", ""),
        "source_url": row.get("source_url", "") or row.get("product_url", ""),
        "source_id": source_id,
        "product_url": row.get("product_url", "") or row.get("source_url", ""),
        "product_category": row.get("product_category", ""),
        "candidate_reason": row.get("candidate_reason", ""),
        "review_status": "pending_review",
        "notes": row.get("sandbox_notes", "") or row.get("review_notes", ""),
        "approval_id": row.get("approval_id", ""),
    }


def _candidate_attribute_row(
    row: dict[str, str], species_id: str, source_id: str
) -> dict[str, str]:
    return {
        "species_id": species_id,
        "provider_id": row.get("provider_id", ""),
        "botanical_name": row.get("botanical_name", ""),
        "attribute_name": row.get("attribute_name", ""),
        "attribute_value": row.get("attribute_value", ""),
        "evidence_confidence": row.get("evidence_confidence", "") or "Pending review",
        "source_url": row.get("source_url", "") or row.get("product_url", ""),
        "source_id": source_id,
        "review_status": "pending_review",
        "notes": row.get("sandbox_notes", "") or row.get("review_notes", ""),
        "approval_id": row.get("approval_id", ""),
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
        "candidate_species": str(path / "candidate_species.csv"),
        "candidate_attributes": str(path / "candidate_attributes.csv"),
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
        "candidate_species": 0,
        "candidate_attributes": 0,
        "supplier_availability": 0,
        "mowability": 0,
    }


def _read_csv(path: Path, diagnostics: list[Diagnostic]) -> list[dict[str, str]]:
    """Read a CSV file into a list of dicts."""
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except OSError as exc:
        diagnostics.append(
            _diagnostic("provider_approval_csv_unreadable", field="path", value=f"{path}: {exc}")
        )
        return []


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


def _auto_approval_note(row: dict[str, str]) -> str:
    table = row.get("sandbox_table", "")
    return (
        "Auto-approved by greedy provider import: species approved and supplier, "
        f"attribute, and mowability inclusion enabled for {table}."
    )


def _sandbox_approval_metadata(row: dict[str, str]) -> dict[str, str]:
    return {
        "candidate_status": row.get("candidate_status", ""),
        "vancouver_eligibility_status": row.get("vancouver_eligibility_status", ""),
        "product_category": row.get("product_category", ""),
        "candidate_reason": row.get("candidate_reason", ""),
        "sandbox_review_status": row.get("review_status", ""),
        "sandbox_notes": row.get("notes", ""),
    }


def _has_errors(diagnostics: tuple[Diagnostic, ...] | list[Diagnostic]) -> bool:
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


# ---------------------------------------------------------------------------
# Auto-approve sandbox → PoC (fully unsupervised batch pipeline)
# ---------------------------------------------------------------------------


def apply_provider_sandbox(
    sandbox_dir: Path,
    poc_dir: Path,
    output_dir: Path,
    *,
    regenerate_downstream: bool = True,
) -> ProviderApprovalResult:
    """Auto-approve a provider sandbox and apply directly to the Vancouver PoC.

    Reads candidate species, supplier, attribute, and mowability rows from
    a validated provider sandbox, applies Vancouver eligibility filters,
    generates an approval manifest with all eligible candidates marked
    ``approved`` (including their linked supplier/attribute/mowability rows),
    and applies it directly -- creating a fully unsupervised batch ingestion
    pipeline.

    Eligibility filters applied:

    * Provider rows with ``vancouver_eligibility_status == "excluded"`` are
      dropped (e.g. PROV-WCS vegetables per VAN-PROV-003).
    * All other eligible candidates are auto-approved.

    All three "include" categories from the review app -- **supplier_availability**
    rows, **candidate_attributes** rows, and **mowability** rows -- are included
    by default when their parent species is approved.
    """
    diagnostics: list[Diagnostic] = []
    sandbox_dir = sandbox_dir.resolve()

    validation = validate_provider_sandbox(sandbox_dir)
    diagnostics.extend(validation.diagnostics)
    if _has_errors(validation.diagnostics):
        return ProviderApprovalResult(
            str(output_dir),
            _empty_counts(),
            validation.diagnostics,
            {},
        )

    # --- 1. Load sandbox tables ------------------------------------------------
    species_rows = _read_csv(sandbox_dir / "candidate_species.csv", diagnostics)
    attribute_rows = _read_csv(sandbox_dir / "candidate_attributes.csv", diagnostics)
    supplier_rows_raw = _read_csv(sandbox_dir / "supplier_availability.csv", diagnostics)
    mowability_rows_raw = _read_csv(sandbox_dir / "mowability.csv", diagnostics)

    # --- 2. Extract provider_id ------------------------------------------------
    provider_id = _extract_provider_id_from_sandbox(
        species_rows, attribute_rows, supplier_rows_raw, mowability_rows_raw
    )
    if not provider_id:
        diagnostics.append(
            Diagnostic(
                code="missing_provider_id",
                message="Could not determine provider_id from sandbox rows.",
                severity=Severity.ERROR,
            )
        )
        return ProviderApprovalResult(str(output_dir), _empty_counts(), tuple(diagnostics), {})

    # --- 3. Apply Vancouver eligibility filters ---------------------------------
    included_species = []
    excluded_count = 0
    for row in species_rows:
        elig = row.get("vancouver_eligibility_status", "candidate").strip().lower()
        candidate_status = row.get("candidate_status", "").strip().lower()
        if elig in {"excluded", "ineligible"} or candidate_status == "excluded":
            excluded_count += 1
            continue
        included_species.append(row)

    included_names = {r.get("botanical_name", "").strip().casefold() for r in included_species}

    # --- 4. Group related rows by botanical name --------------------------------
    attributes_by_name: dict[str, list[dict]] = {}
    for row in attribute_rows:
        if row.get("botanical_name", "").strip().casefold() not in included_names:
            continue
        name = row.get("botanical_name", "").strip().casefold()
        attributes_by_name.setdefault(name, []).append(row)

    supplier_by_name: dict[str, list[dict]] = {}
    for row in supplier_rows_raw:
        if row.get("botanical_name", "").strip().casefold() not in included_names:
            continue
        name = row.get("botanical_name", "").strip().casefold()
        supplier_by_name.setdefault(name, []).append(row)

    mowability_by_name: dict[str, list[dict]] = {}
    for row in mowability_rows_raw:
        if row.get("botanical_name", "").strip().casefold() not in included_names:
            continue
        name = row.get("botanical_name", "").strip().casefold()
        mowability_by_name.setdefault(name, []).append(row)

    # --- 5. Build approval manifest rows ----------------------------------------
    # First load POC plant_list to determine which species already exist
    existing_plant_rows = _load_csv(poc_dir / "plant_list.csv", diagnostics)
    existing_names = {r.get("Botanical Name", "").strip().casefold() for r in existing_plant_rows}

    # Build lookup dict for existing species
    existing_species_by_name: dict[str, dict[str, str]] = {
        row.get("Botanical Name", "").strip().casefold(): row
        for row in existing_plant_rows if row.get("Botanical Name")
    }

    approval_rows: list[dict[str, str]] = []
    included_supplier_count = 0
    included_attribute_count = 0
    included_mowability_count = 0

    for idx, species_row in enumerate(included_species, start=1):
        botanical_name = species_row.get("botanical_name", "").strip()
        common_name = species_row.get("common_name", "").strip()
        product_url = species_row.get("product_url", "") or ""
        source_url = species_row.get("source_url", "")

        # Determine if this is a new species or existing
        target_action = (
            "add_species" if botanical_name.casefold() not in existing_names else "update_existing"
        )

        # Get species_id if it's an update_existing
        species_id = ""
        if target_action == "update_existing":
            existing_row = existing_species_by_name.get(botanical_name.casefold())
            if existing_row:
                species_id = existing_row.get("Species ID", "")

        related_target_action = target_action if target_action == "add_species" else ""

        # Include supplier rows (Category 1: supplier_availability)
        related_suppliers = supplier_by_name.get(botanical_name.casefold(), [])
        for sup_idx, sup in enumerate(related_suppliers, start=1):
            included_supplier_count += 1
            approval_rows.append({
                "approval_id": f"PA-AUTO-{idx:04d}-SUP-{sup_idx:02d}",
                "sandbox_table": "supplier_availability.csv",
                "provider_id": provider_id,
                "botanical_name": botanical_name,
                "common_name": common_name,
                "species_id": species_id,  # Use parent species_id (can be empty for new species)
                "approval_status": IMPORTABLE_APPROVAL_STATUS,
                "target_action": related_target_action or "record_supplier",
                "attribute_name": "",
                "attribute_value": "",
                "evidence_confidence": "Pending review",
                "source_url": sup.get("product_url", "") or source_url,
                "supplier_status": sup.get("supplier_status", ""),
                "product_url": sup.get("product_url", ""),
                "mowability_score": "",
                "reviewer": "auto-approve (greedy mode)",
                "review_date": "",
                "review_notes": "Auto-approved supplier row via apply_provider_sandbox.",
                **_sandbox_approval_metadata(sup),
            })

        # Include attribute rows (Category 2: candidate_attributes)
        related_attrs = attributes_by_name.get(botanical_name.casefold(), [])
        for attr_idx, attr in enumerate(related_attrs, start=1):
            included_attribute_count += 1
            approval_rows.append({
                "approval_id": f"PA-AUTO-{idx:04d}-ATTR-{attr_idx:02d}",
                "sandbox_table": "candidate_attributes.csv",
                "provider_id": provider_id,
                "botanical_name": botanical_name,
                "common_name": common_name,
                "species_id": species_id,  # Use parent species_id (can be empty for new species)
                "approval_status": IMPORTABLE_APPROVAL_STATUS,
                "target_action": related_target_action or "update_existing",
                "attribute_name": attr.get("attribute_name", ""),
                "attribute_value": attr.get("attribute_value", ""),
                "evidence_confidence": "Pending review",
                "source_url": attr.get("source_url", source_url),
                "supplier_status": "",
                "product_url": attr.get("product_url", "") or source_url,
                "mowability_score": "",
                "reviewer": "auto-approve (greedy mode)",
                "review_date": "",
                "review_notes": "Auto-approved attribute row via apply_provider_sandbox.",
                **_sandbox_approval_metadata(attr),
            })

        # Include mowability rows (Category 3: mowability)
        related_mow = mowability_by_name.get(botanical_name.casefold(), [])
        for mow_idx, mow in enumerate(related_mow, start=1):
            included_mowability_count += 1
            approval_rows.append({
                "approval_id": f"PA-AUTO-{idx:04d}-MOW-{mow_idx:02d}",
                "sandbox_table": "mowability.csv",
                "provider_id": provider_id,
                "botanical_name": botanical_name,
                "common_name": common_name,
                "species_id": species_id,  # Use parent species_id (can be empty for new species)
                "approval_status": IMPORTABLE_APPROVAL_STATUS,
                "target_action": related_target_action or "record_mowability",
                "attribute_name": "",
                "attribute_value": "",
                "evidence_confidence": "Pending review",
                "source_url": mow.get("source_url", source_url),
                "supplier_status": "",
                "product_url": "",
                "mowability_score": mow.get("mowability_score", ""),
                "reviewer": "auto-approve (greedy mode)",
                "review_date": "",
                "review_notes": "Auto-approved mowability row via apply_provider_sandbox.",
                **_sandbox_approval_metadata(mow),
            })

        # Species-level approval row
        approval_rows.append({
            "approval_id": f"PA-AUTO-{idx:04d}",
            "sandbox_table": "candidate_species.csv",
            "provider_id": provider_id,
            "botanical_name": botanical_name,
            "common_name": common_name,
            "species_id": species_id,
            "approval_status": IMPORTABLE_APPROVAL_STATUS,
            "target_action": target_action,
            "attribute_name": "",
            "attribute_value": "",
            "evidence_confidence": "Pending review",
            "source_url": source_url or product_url,
            "supplier_status": "",
            "product_url": product_url or source_url,
            "mowability_score": "",
            "reviewer": "auto-approve (greedy mode)",
            "review_date": "",
            "review_notes": (
                "Auto-approved via apply_provider_sandbox. "
                f"Eligibility: {species_row.get('vancouver_eligibility_status', 'candidate')}."
            ),
            **_sandbox_approval_metadata(species_row),
        })

    approved_count = len(included_species)

    # --- 6. Write temp manifest & delegate to existing apply logic ---------------
    temp_manifest = output_dir / "_auto_approved_manifest.csv"
    _write_csv(temp_manifest, approval_rows, APPROVAL_FIELDS)

    counts = {
        "sandbox_species": len(species_rows),
        "eligible_species": approved_count,
        "excluded_species": excluded_count,
        "auto_approval_rows": len(approval_rows),
        "approval_manifest": len(approval_rows),
        # Count rows marked approved: species, supplier, attribute, and mowability.
        "approved_rows": len(
            [
                row
                for row in approval_rows
                if row.get("approval_status") == IMPORTABLE_APPROVAL_STATUS
            ]
        ),
        "supplier_included": included_supplier_count,
        "attribute_included": included_attribute_count,
        "mowability_included": included_mowability_count,
    }

    apply_result = apply_provider_approvals(
        temp_manifest,
        poc_dir,
        output_dir,
        regenerate_downstream=regenerate_downstream,
    )

    if temp_manifest.exists():
        temp_manifest.unlink()

    diagnostics.append(
        Diagnostic(
            code="provider_sandbox_auto_approved",
            message=(
                f"Auto-approved {approved_count} species "
                f"({excluded_count} excluded) with all linked supplier/"
                f"attribute/mowability rows."
            ),
            severity=Severity.INFO,
            context={
                "approved_species": approved_count,
                "excluded_species": excluded_count,
                "supplier_included": included_supplier_count,
                "attributes_included": included_attribute_count,
                "mowability_included": included_mowability_count,
                "provider_id": provider_id,
            },
        )
    )

    final_counts = {
        **counts,
        # Use apply_result's counts for downstream files
        "plant_list": apply_result.counts.get("plant_list", 0),
        "sources": apply_result.counts.get("sources", 0),
        "source_attribution": apply_result.counts.get("source_attribution", 0),
        "supplier_availability": apply_result.counts.get("supplier_availability", 0),
        "mowability": apply_result.counts.get("mowability", 0),
    }
    all_diagnostics = tuple(diagnostics) + apply_result.diagnostics

    return ProviderApprovalResult(
        str(output_dir),
        final_counts,
        all_diagnostics,
        apply_result.paths,
    )


def _extract_provider_id_from_sandbox(
    species_rows: list[dict],
    attribute_rows: list[dict],
    supplier_rows: list[dict],
    mowability_rows: list[dict],
) -> str | None:
    """Extract provider_id from any non-empty sandbox table."""
    for rows in [species_rows, attribute_rows, supplier_rows, mowability_rows]:
        for row in rows:
            pid = row.get("provider_id", "").strip()
            if pid:
                return pid
    return None
