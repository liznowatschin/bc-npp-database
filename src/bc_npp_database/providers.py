"""Source-provider registry and provider sandbox validation."""

from __future__ import annotations

import csv
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .diagnostics import Diagnostic, Severity
from .sources import ReviewStatus, SourceTier, load_mapping_records, source_tier_values
from .validate import diagnose_excluded_sources

PROVIDER_ID_PATTERN = re.compile(r"^PROV-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
MOWABILITY_VALUES = {"0", "1", "2", "3", "4", "5"}
KNOWN_PROVIDER_IDS = {
    "PROV-SATIN",
    "PROV-NWM",
    "PROV-WCS",
    "PROV-PREMIER",
    "PROV-OAKSUMMIT",
}
VANCOUVER_ELIGIBILITY_STATUSES = {
    "candidate",
    "eligible",
    "excluded",
    "ineligible",
    "needs_review",
    "needs_northward_review",
}

PROVIDER_REGISTRY_FIELDS = (
    "provider_id",
    "provider_name",
    "homepage_url",
    "source_tier",
    "in_scope_notes",
    "exclusion_notes",
    "scrape_policy",
    "review_status",
    "notes",
)

SANDBOX_REQUIRED_FILES = (
    "manifest.json",
    "inventory_pages.csv",
    "candidate_species.csv",
    "candidate_attributes.csv",
    "supplier_availability.csv",
    "mowability.csv",
    "diagnostics.csv",
)

SANDBOX_REQUIRED_COLUMNS = {
    "inventory_pages.csv": (
        "provider_id",
        "page_url",
        "page_type",
        "fetch_status",
        "review_status",
    ),
    "candidate_species.csv": (
        "provider_id",
        "botanical_name",
        "candidate_status",
        "vancouver_eligibility_status",
        "source_url",
        "review_status",
    ),
    "candidate_attributes.csv": (
        "provider_id",
        "botanical_name",
        "attribute_name",
        "attribute_value",
        "evidence_confidence",
        "source_url",
        "review_status",
    ),
    "supplier_availability.csv": (
        "provider_id",
        "botanical_name",
        "supplier_status",
        "product_url",
        "review_status",
    ),
    "mowability.csv": (
        "provider_id",
        "botanical_name",
        "mowability_score",
        "source_url",
        "review_status",
    ),
    "diagnostics.csv": ("severity", "code", "message"),
}


@dataclass(frozen=True)
class SourceProviderRecord:
    """One source-provider registry row."""

    provider_id: str
    provider_name: str
    homepage_url: str
    source_tier: str
    in_scope_notes: str
    exclusion_notes: str
    scrape_policy: str
    review_status: str = ReviewStatus.PENDING.value
    notes: str = ""

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> SourceProviderRecord:
        """Build a source-provider record from CSV/JSON-friendly fields."""
        return cls(
            provider_id=_first(row, "provider_id", "Provider ID"),
            provider_name=_first(row, "provider_name", "Provider Name"),
            homepage_url=_first(row, "homepage_url", "Homepage URL", "url", "URL"),
            source_tier=_first(row, "source_tier", "Source Tier", "tier", "Tier"),
            in_scope_notes=_first(row, "in_scope_notes", "In Scope Notes"),
            exclusion_notes=_first(row, "exclusion_notes", "Exclusion Notes"),
            scrape_policy=_first(row, "scrape_policy", "Scrape Policy"),
            review_status=_first(
                row,
                "review_status",
                "Review Status",
                default=ReviewStatus.PENDING.value,
            ),
            notes=_first(row, "notes", "Notes"),
        )

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable record."""
        return {
            "provider_id": self.provider_id,
            "provider_name": self.provider_name,
            "homepage_url": self.homepage_url,
            "source_tier": self.source_tier,
            "in_scope_notes": self.in_scope_notes,
            "exclusion_notes": self.exclusion_notes,
            "scrape_policy": self.scrape_policy,
            "review_status": self.review_status,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ProviderSandboxResult:
    """Provider sandbox validation summary."""

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


def validate_source_provider_records(rows: Iterable[Mapping[str, object]]) -> list[Diagnostic]:
    """Validate source-provider registry rows."""
    diagnostics: list[Diagnostic] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        record = SourceProviderRecord.from_mapping(row)
        diagnostics.extend(_validate_provider_record(record, index))
        if record.provider_id in seen:
            diagnostics.append(
                _diagnostic(
                    "duplicate_provider_id",
                    "Duplicate provider ID.",
                    index,
                    "provider_id",
                    record.provider_id,
                )
            )
        seen.add(record.provider_id)
        diagnostics.extend(diagnose_excluded_sources([row]))
    return diagnostics


def validate_source_provider_file(path: Path) -> list[Diagnostic]:
    """Validate a source-provider registry file."""
    return validate_source_provider_records(load_mapping_records(path))


def validate_provider_sandbox(path: Path) -> ProviderSandboxResult:
    """Validate a provider sandbox directory."""
    diagnostics: list[Diagnostic] = []
    counts = {
        filename.removesuffix(".csv").removesuffix(".json"): 0
        for filename in SANDBOX_REQUIRED_FILES
    }
    paths = {
        filename.removesuffix(".csv").removesuffix(".json"): str(path / filename)
        for filename in SANDBOX_REQUIRED_FILES
    }

    for filename in SANDBOX_REQUIRED_FILES:
        if not (path / filename).exists():
            diagnostics.append(
                _diagnostic(
                    "missing_provider_sandbox_file",
                    "Missing provider sandbox file.",
                    field="path",
                    value=filename,
                )
            )
    if diagnostics:
        return ProviderSandboxResult(str(path), counts, tuple(diagnostics), paths)

    manifest = _load_json(path / "manifest.json", diagnostics)
    table_rows: dict[str, list[dict[str, str]]] = {}
    for filename in SANDBOX_REQUIRED_COLUMNS:
        rows = _load_csv(path / filename, diagnostics)
        table_rows[filename] = rows
        counts[filename.removesuffix(".csv")] = len(rows)
        diagnostics.extend(_validate_required_columns(filename, rows))

    diagnostics.extend(_validate_manifest(manifest, table_rows))
    diagnostics.extend(_validate_inventory_pages(table_rows["inventory_pages.csv"]))
    diagnostics.extend(_validate_candidate_species(table_rows["candidate_species.csv"]))
    diagnostics.extend(_validate_candidate_attributes(table_rows["candidate_attributes.csv"]))
    diagnostics.extend(_validate_supplier_rows(table_rows["supplier_availability.csv"]))
    diagnostics.extend(_validate_mowability_rows(table_rows["mowability.csv"]))
    diagnostics.extend(_validate_diagnostic_rows(table_rows["diagnostics.csv"]))

    for rows in table_rows.values():
        diagnostics.extend(diagnose_excluded_sources(rows))

    return ProviderSandboxResult(str(path), counts, tuple(diagnostics), paths)


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...] | list[Diagnostic]) -> bool:
    """Return whether diagnostics include an error."""
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


def _validate_provider_record(record: SourceProviderRecord, row_number: int) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for field, value in (
        ("provider_id", record.provider_id),
        ("provider_name", record.provider_name),
        ("homepage_url", record.homepage_url),
        ("source_tier", record.source_tier),
        ("in_scope_notes", record.in_scope_notes),
        ("exclusion_notes", record.exclusion_notes),
        ("scrape_policy", record.scrape_policy),
    ):
        if not value:
            diagnostics.append(
                _diagnostic("missing_required_field", "Missing required field.", row_number, field)
            )
    if record.provider_id and not PROVIDER_ID_PATTERN.fullmatch(record.provider_id):
        diagnostics.append(
            _diagnostic(
                "invalid_provider_id",
                "Invalid provider ID.",
                row_number,
                "provider_id",
                record.provider_id,
            )
        )
    if record.provider_id and record.provider_id not in KNOWN_PROVIDER_IDS:
        diagnostics.append(
            _diagnostic(
                "unknown_provider_id",
                "Provider ID is not in the configured P15 provider set.",
                row_number,
                "provider_id",
                record.provider_id,
                Severity.WARNING,
            )
        )
    if record.homepage_url and not _is_http_url(record.homepage_url):
        diagnostics.append(
            _diagnostic(
                "invalid_provider_url",
                "Provider URL must be HTTP(S).",
                row_number,
                "homepage_url",
                record.homepage_url,
            )
        )
    if record.source_tier and record.source_tier not in source_tier_values():
        diagnostics.append(
            _diagnostic(
                "invalid_source_tier",
                "Invalid source tier.",
                row_number,
                "source_tier",
                record.source_tier,
            )
        )
    if record.source_tier and record.source_tier != SourceTier.TIER_3.value:
        diagnostics.append(
            _diagnostic(
                "provider_not_tier_3",
                "P15 provider registry entries should be Tier 3 commercial/practitioner sources.",
                row_number,
                "source_tier",
                record.source_tier,
                Severity.WARNING,
            )
        )
    if record.review_status not in {status.value for status in ReviewStatus}:
        diagnostics.append(
            _diagnostic(
                "invalid_review_status",
                "Invalid review status.",
                row_number,
                "review_status",
                record.review_status,
            )
        )
    return diagnostics


def _validate_inventory_pages(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for index, row in enumerate(rows, start=2):
        diagnostics.extend(_validate_provider_id(row.get("provider_id", ""), index))
        diagnostics.extend(_validate_url_field(row.get("page_url", ""), index, "page_url"))
        diagnostics.extend(_validate_review_status(row.get("review_status", ""), index))
    return diagnostics


def _validate_candidate_species(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(rows, start=2):
        provider_id = row.get("provider_id", "")
        botanical_name = row.get("botanical_name", "").strip()
        key = (provider_id, botanical_name.casefold())
        if key in seen:
            diagnostics.append(
                _diagnostic(
                    "duplicate_candidate_species",
                    "Duplicate provider species candidate.",
                    index,
                    "botanical_name",
                    botanical_name,
                )
            )
        seen.add(key)
        diagnostics.extend(_validate_provider_id(provider_id, index))
        diagnostics.extend(_validate_url_field(row.get("source_url", ""), index, "source_url"))
        diagnostics.extend(_validate_review_status(row.get("review_status", ""), index))
        status = row.get("vancouver_eligibility_status", "").strip()
        if status and status not in VANCOUVER_ELIGIBILITY_STATUSES:
            diagnostics.append(
                _diagnostic(
                    "invalid_vancouver_eligibility_status",
                    "Invalid Vancouver eligibility status.",
                    index,
                    "vancouver_eligibility_status",
                    status,
                )
            )
        is_excluded = row.get("candidate_status") == "excluded" or status in {
            "excluded",
            "ineligible",
        }
        if provider_id == "PROV-WCS" and _is_vegetable_row(row) and not is_excluded:
            diagnostics.append(
                _diagnostic(
                    "wcs_vegetable_excluded",
                    "WCS vegetable rows must be excluded from Vancouver candidates.",
                    index,
                    "product_category",
                    row.get("product_category", ""),
                )
            )
        if provider_id == "PROV-NWM" and status == "eligible":
            diagnostics.append(
                _diagnostic(
                    "nwm_requires_northward_review",
                    "NWM rows require Vancouver/BC review before direct eligibility.",
                    index,
                    "vancouver_eligibility_status",
                    status,
                    Severity.WARNING,
                )
            )
    return diagnostics


def _validate_candidate_attributes(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for index, row in enumerate(rows, start=2):
        diagnostics.extend(_validate_provider_id(row.get("provider_id", ""), index))
        diagnostics.extend(_validate_url_field(row.get("source_url", ""), index, "source_url"))
        diagnostics.extend(_validate_review_status(row.get("review_status", ""), index))
        if not row.get("attribute_name", "").strip():
            diagnostics.append(
                _diagnostic(
                    "missing_required_field", "Missing required field.", index, "attribute_name"
                )
            )
        if not row.get("attribute_value", "").strip():
            diagnostics.append(
                _diagnostic(
                    "missing_required_field", "Missing required field.", index, "attribute_value"
                )
            )
    return diagnostics


def _validate_supplier_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for index, row in enumerate(rows, start=2):
        diagnostics.extend(_validate_provider_id(row.get("provider_id", ""), index))
        diagnostics.extend(_validate_url_field(row.get("product_url", ""), index, "product_url"))
        diagnostics.extend(_validate_review_status(row.get("review_status", ""), index))
    return diagnostics


def _validate_mowability_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for index, row in enumerate(rows, start=2):
        diagnostics.extend(_validate_provider_id(row.get("provider_id", ""), index))
        diagnostics.extend(_validate_url_field(row.get("source_url", ""), index, "source_url"))
        diagnostics.extend(_validate_review_status(row.get("review_status", ""), index))
        score = row.get("mowability_score", "").strip()
        if score and score not in MOWABILITY_VALUES:
            diagnostics.append(
                _diagnostic(
                    "invalid_mowability_score",
                    "Mowability score must be 0-5.",
                    index,
                    "mowability_score",
                    score,
                )
            )
    return diagnostics


def _validate_manifest(
    manifest: dict[str, Any], rows: dict[str, list[dict[str, str]]]
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if not manifest:
        diagnostics.append(
            _diagnostic(
                "invalid_provider_sandbox_manifest",
                "Provider sandbox manifest is missing or invalid.",
            )
        )
        return diagnostics
    if manifest.get("database_instance") != "vancouver":
        diagnostics.append(
            _diagnostic(
                "invalid_database_instance",
                "P15 sandbox validation expects the Vancouver database instance.",
                field="database_instance",
                value=str(manifest.get("database_instance", "")),
            )
        )
    hygiene = manifest.get("public_hygiene", {})
    if not isinstance(hygiene, dict) or hygiene.get("raw_provider_html_tracked") is not False:
        diagnostics.append(
            _diagnostic(
                "invalid_provider_public_hygiene",
                "Provider sandbox must not track raw provider HTML.",
                field="public_hygiene",
            )
        )
    expected_counts = {
        "inventory_page_count": len(rows.get("inventory_pages.csv", [])),
        "candidate_species_count": len(rows.get("candidate_species.csv", [])),
        "candidate_attribute_count": len(rows.get("candidate_attributes.csv", [])),
        "supplier_availability_count": len(rows.get("supplier_availability.csv", [])),
        "mowability_count": len(rows.get("mowability.csv", [])),
    }
    for field, expected in expected_counts.items():
        if field in manifest and manifest.get(field) != expected:
            diagnostics.append(
                _diagnostic(
                    "provider_manifest_count_mismatch",
                    "Provider sandbox manifest count mismatch.",
                    field=field,
                    value=str(manifest.get(field)),
                )
            )
    return diagnostics


def _validate_diagnostic_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for index, row in enumerate(rows, start=2):
        severity = row.get("severity", "")
        if severity and severity not in {item.value for item in Severity}:
            diagnostics.append(
                _diagnostic(
                    "invalid_diagnostic_severity",
                    "Invalid diagnostic severity.",
                    index,
                    "severity",
                    severity,
                )
            )
    return diagnostics


def _validate_required_columns(filename: str, rows: list[dict[str, str]]) -> list[Diagnostic]:
    if not rows:
        return []
    present = set(rows[0])
    return [
        _diagnostic(
            "missing_provider_sandbox_column",
            "Missing provider sandbox column.",
            field=filename,
            value=column,
        )
        for column in SANDBOX_REQUIRED_COLUMNS[filename]
        if column not in present
    ]


def _validate_provider_id(provider_id: str, row_number: int) -> list[Diagnostic]:
    if not provider_id:
        return [
            _diagnostic(
                "missing_required_field", "Missing required field.", row_number, "provider_id"
            )
        ]
    if not PROVIDER_ID_PATTERN.fullmatch(provider_id):
        return [
            _diagnostic(
                "invalid_provider_id",
                "Invalid provider ID.",
                row_number,
                "provider_id",
                provider_id,
            )
        ]
    return []


def _validate_url_field(value: str, row_number: int, field: str) -> list[Diagnostic]:
    if not value:
        return [_diagnostic("missing_required_field", "Missing required field.", row_number, field)]
    if not _is_http_url(value):
        return [
            _diagnostic(
                "invalid_provider_url", "Provider URL must be HTTP(S).", row_number, field, value
            )
        ]
    return []


def _validate_review_status(value: str, row_number: int) -> list[Diagnostic]:
    if not value:
        return [
            _diagnostic(
                "missing_required_field", "Missing required field.", row_number, "review_status"
            )
        ]
    if value not in {status.value for status in ReviewStatus}:
        return [
            _diagnostic(
                "invalid_review_status",
                "Invalid review status.",
                row_number,
                "review_status",
                value,
            )
        ]
    return []


def _load_csv(path: Path, diagnostics: list[Diagnostic]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    except OSError as exc:
        diagnostics.append(
            _diagnostic(
                "provider_sandbox_csv_unreadable",
                "Provider sandbox CSV unreadable.",
                field="path",
                value=f"{path}: {exc}",
            )
        )
        return []


def _load_json(path: Path, diagnostics: list[Diagnostic]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        diagnostics.append(
            _diagnostic(
                "provider_sandbox_json_unreadable",
                "Provider sandbox JSON unreadable.",
                field="path",
                value=f"{path}: {exc}",
            )
        )
        return {}
    return payload if isinstance(payload, dict) else {}


def _first(row: Mapping[str, object], *names: str, default: str = "") -> str:
    for name in names:
        if name in row and row[name] is not None:
            return str(row[name]).strip()
    return default


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_vegetable_row(row: Mapping[str, str]) -> bool:
    text = " ".join(
        row.get(field, "") for field in ("product_category", "product_scope", "category", "notes")
    ).casefold()
    return "vegetable" in text


def _diagnostic(
    code: str,
    message: str,
    row_number: int | None = None,
    field: str | None = None,
    value: str | None = None,
    severity: Severity = Severity.ERROR,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        message=message,
        severity=severity,
        row_number=row_number,
        field=field,
        value=value,
    )
