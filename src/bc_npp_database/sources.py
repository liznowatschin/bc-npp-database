"""Source, evidence, and attribution records for BC-NPPD."""

from __future__ import annotations

import csv
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from .config import EVIDENCE_CONFIDENCE_VALUES, EXCLUDED_SOURCE_URLS
from .diagnostics import Diagnostic, Severity

SOURCE_ID_PATTERN = re.compile(r"^(?:SRC|REF)-\d{4}$")
SPECIES_ID_PATTERN = re.compile(r"^BCNPPD-\d{4}$")
EXTERNAL_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*(?::[A-Za-z0-9._-]+)+$")


class SourceTier(StrEnum):
    """Configured source tiers for source/reference records."""

    TIER_1 = "Tier 1"
    TIER_2 = "Tier 2"
    TIER_3 = "Tier 3"


class ReviewStatus(StrEnum):
    """Review state for source, manifest, and extracted evidence records."""

    PENDING = "pending_review"
    ACCEPTED = "accepted"
    MANUALLY_CORRECTED = "manually_corrected"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class MaterializationStatus(StrEnum):
    """Acquisition/materialization state for external source artifacts."""

    NOT_MATERIALIZED = "not_materialized"
    PLANNED = "planned"
    RESOLVED = "resolved"
    MATERIALIZED = "materialized"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


def source_tier_values() -> set[str]:
    """Return configured source tier values."""
    return {tier.value for tier in SourceTier}


def review_status_values() -> set[str]:
    """Return configured review status values."""
    return {status.value for status in ReviewStatus}


def materialization_status_values() -> set[str]:
    """Return configured materialization status values."""
    return {status.value for status in MaterializationStatus}


@dataclass(frozen=True)
class SourceRecord:
    """One citable source/reference record."""

    source_id: str
    source_name: str
    source_tier: str
    citation: str = ""
    url: str = ""
    external_id: str = ""
    review_status: str = ReviewStatus.PENDING.value
    notes: str = ""

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> SourceRecord:
        """Build a source record from common CSV/JSON field names."""
        return cls(
            source_id=_first(row, "source_id", "Source ID", "Reference ID", "reference_id"),
            source_name=_first(row, "source_name", "Source Name", "title", "Title", "name", "Name"),
            source_tier=_first(row, "source_tier", "Source Tier", "tier", "Tier"),
            citation=_first(row, "citation", "Citation"),
            url=_first(row, "url", "URL", "source_url", "Source URL"),
            external_id=_first(row, "external_id", "External ID", "external_source_id"),
            review_status=_first(
                row,
                "review_status",
                "Review Status",
                "source_status",
                default=ReviewStatus.PENDING.value,
            ),
            notes=_first(row, "notes", "Notes"),
        )

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable record dictionary."""
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_tier": self.source_tier,
            "citation": self.citation,
            "url": self.url,
            "external_id": self.external_id,
            "review_status": self.review_status,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class SourceAttributionRecord:
    """One source attribution row supporting a claim or field."""

    source_id: str
    claim_field: str
    evidence_confidence: str
    species_id: str = ""
    claim_value: str = ""
    claim_scope: str = "species"
    external_id: str = ""
    review_status: str = ReviewStatus.PENDING.value
    notes: str = ""

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> SourceAttributionRecord:
        """Build an attribution record from common CSV/JSON field names."""
        return cls(
            source_id=_first(row, "source_id", "Source ID", "Reference ID", "reference_id"),
            species_id=_first(row, "species_id", "Species ID", "Species_ID"),
            claim_field=_first(
                row,
                "claim_field",
                "Claim Field",
                "field_supported",
                "Field Supported",
                "field",
                "Field",
            ),
            claim_value=_first(row, "claim_value", "Claim Value", "value", "Value"),
            claim_scope=_first(row, "claim_scope", "Claim Scope", default="species"),
            evidence_confidence=_first(
                row,
                "evidence_confidence",
                "Evidence Confidence",
                "Evidence_Confidence",
                "Evidence Level",
                "Evidence_Level",
            ),
            external_id=_first(row, "external_id", "External ID", "external_source_id"),
            review_status=_first(
                row,
                "review_status",
                "Review Status",
                default=ReviewStatus.PENDING.value,
            ),
            notes=_first(row, "notes", "Notes"),
        )

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable record dictionary."""
        return {
            "source_id": self.source_id,
            "species_id": self.species_id,
            "claim_field": self.claim_field,
            "claim_value": self.claim_value,
            "claim_scope": self.claim_scope,
            "evidence_confidence": self.evidence_confidence,
            "external_id": self.external_id,
            "review_status": self.review_status,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class MaterializationManifest:
    """One external source resolution or acquisition manifest record."""

    manifest_id: str
    source_id: str
    artifact_type: str
    status: str = MaterializationStatus.PLANNED.value
    artifact_path: str = ""
    external_id: str = ""
    review_status: str = ReviewStatus.PENDING.value
    notes: str = ""

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> MaterializationManifest:
        """Build a materialization manifest from common field names."""
        return cls(
            manifest_id=_first(row, "manifest_id", "Manifest ID"),
            source_id=_first(row, "source_id", "Source ID", "Reference ID", "reference_id"),
            artifact_type=_first(row, "artifact_type", "Artifact Type"),
            status=_first(
                row,
                "status",
                "Status",
                "materialization_status",
                default=MaterializationStatus.PLANNED.value,
            ),
            artifact_path=_first(row, "artifact_path", "Artifact Path", "path", "Path"),
            external_id=_first(row, "external_id", "External ID", "external_source_id"),
            review_status=_first(
                row,
                "review_status",
                "Review Status",
                default=ReviewStatus.PENDING.value,
            ),
            notes=_first(row, "notes", "Notes"),
        )

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable record dictionary."""
        return {
            "manifest_id": self.manifest_id,
            "source_id": self.source_id,
            "artifact_type": self.artifact_type,
            "status": self.status,
            "artifact_path": self.artifact_path,
            "external_id": self.external_id,
            "review_status": self.review_status,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class MediaExtractionManifest:
    """One review-gated media-derived extraction manifest record."""

    extraction_id: str
    source_id: str
    source_document_id: str
    page_number: str = ""
    figure_or_table_id: str = ""
    crop_or_image_id: str = ""
    extraction_method: str = ""
    tool_version: str = ""
    review_status: str = ReviewStatus.PENDING.value
    accepted_table_path: str = ""
    external_id: str = ""
    notes: str = ""

    @classmethod
    def from_mapping(cls, row: Mapping[str, object]) -> MediaExtractionManifest:
        """Build a media extraction manifest from common field names."""
        return cls(
            extraction_id=_first(row, "extraction_id", "Extraction ID"),
            source_id=_first(row, "source_id", "Source ID", "Reference ID", "reference_id"),
            source_document_id=_first(row, "source_document_id", "Source Document ID"),
            page_number=_first(row, "page_number", "Page", "Page Number"),
            figure_or_table_id=_first(row, "figure_or_table_id", "Figure ID", "Table ID"),
            crop_or_image_id=_first(row, "crop_or_image_id", "Crop ID", "Image ID"),
            extraction_method=_first(row, "extraction_method", "Extraction Method"),
            tool_version=_first(row, "tool_version", "Tool Version"),
            review_status=_first(
                row,
                "review_status",
                "Review Status",
                default=ReviewStatus.PENDING.value,
            ),
            accepted_table_path=_first(row, "accepted_table_path", "Accepted Table Path"),
            external_id=_first(row, "external_id", "External ID", "external_source_id"),
            notes=_first(row, "notes", "Notes"),
        )

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable record dictionary."""
        return {
            "extraction_id": self.extraction_id,
            "source_id": self.source_id,
            "source_document_id": self.source_document_id,
            "page_number": self.page_number,
            "figure_or_table_id": self.figure_or_table_id,
            "crop_or_image_id": self.crop_or_image_id,
            "extraction_method": self.extraction_method,
            "tool_version": self.tool_version,
            "review_status": self.review_status,
            "accepted_table_path": self.accepted_table_path,
            "external_id": self.external_id,
            "notes": self.notes,
        }


def load_mapping_records(path: Path) -> list[dict[str, object]]:
    """Load CSV, JSON, or JSON Lines mapping records from a file."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    if suffix == ".jsonl":
        records: list[dict[str, object]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                payload = json.loads(line)
                if not isinstance(payload, dict):
                    raise ValueError("JSON Lines records must be objects.")
                records.append(payload)
        return records
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            candidate = payload.get("records", payload.get("sources", payload.get("attributions")))
            if isinstance(candidate, list):
                payload = candidate
            else:
                payload = [payload]
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise ValueError("JSON source validation input must be an object or a list of objects.")
        return list(payload)
    raise ValueError(f"Unsupported source validation input format: {path.suffix}")


def validate_source_records(rows: Iterable[Mapping[str, object]]) -> list[Diagnostic]:
    """Validate source/reference rows."""
    diagnostics: list[Diagnostic] = []
    for index, row in enumerate(rows, start=1):
        record = SourceRecord.from_mapping(row)
        diagnostics.extend(_validate_source_record(record, index))
        diagnostics.extend(_diagnose_excluded_in_mapping(row, index))
    return diagnostics


def validate_source_attribution_records(rows: Iterable[Mapping[str, object]]) -> list[Diagnostic]:
    """Validate source-attribution rows."""
    diagnostics: list[Diagnostic] = []
    for index, row in enumerate(rows, start=1):
        record = SourceAttributionRecord.from_mapping(row)
        diagnostics.extend(_validate_attribution_record(record, index))
        diagnostics.extend(_diagnose_excluded_in_mapping(row, index))
    return diagnostics


def validate_materialization_manifests(rows: Iterable[Mapping[str, object]]) -> list[Diagnostic]:
    """Validate materialization manifest rows."""
    diagnostics: list[Diagnostic] = []
    for index, row in enumerate(rows, start=1):
        record = MaterializationManifest.from_mapping(row)
        diagnostics.extend(_validate_materialization_manifest(record, index))
        diagnostics.extend(_diagnose_excluded_in_mapping(row, index))
    return diagnostics


def validate_media_extraction_manifests(rows: Iterable[Mapping[str, object]]) -> list[Diagnostic]:
    """Validate media-extraction manifest rows."""
    diagnostics: list[Diagnostic] = []
    for index, row in enumerate(rows, start=1):
        record = MediaExtractionManifest.from_mapping(row)
        diagnostics.extend(_validate_media_manifest(record, index))
        diagnostics.extend(_diagnose_excluded_in_mapping(row, index))
    return diagnostics


def is_review_accepted(status: str) -> bool:
    """Return whether a review status can be used as accepted candidate evidence."""
    return status.strip() in {ReviewStatus.ACCEPTED.value, ReviewStatus.MANUALLY_CORRECTED.value}


def _validate_source_record(record: SourceRecord, row_number: int) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    diagnostics.extend(_required(record.source_id, "source_id", row_number))
    diagnostics.extend(_required(record.source_name, "source_name", row_number))
    diagnostics.extend(_required(record.source_tier, "source_tier", row_number))
    if record.source_id and not SOURCE_ID_PATTERN.fullmatch(record.source_id):
        diagnostics.append(
            _diagnostic(
                "invalid_source_id",
                "Invalid source/reference ID.",
                row_number,
                "source_id",
                record.source_id,
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
    if not record.citation and not record.url:
        diagnostics.append(
            _diagnostic(
                "missing_citation_or_url",
                "Source records require citation or URL.",
                row_number,
            )
        )
    if record.external_id:
        diagnostics.extend(_validate_external_id(record.external_id, row_number))
    if record.review_status not in review_status_values():
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


def _validate_attribution_record(
    record: SourceAttributionRecord, row_number: int
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    diagnostics.extend(_required(record.source_id, "source_id", row_number))
    diagnostics.extend(_required(record.claim_field, "claim_field", row_number))
    diagnostics.extend(_required(record.evidence_confidence, "evidence_confidence", row_number))
    if record.source_id and not SOURCE_ID_PATTERN.fullmatch(record.source_id):
        diagnostics.append(
            _diagnostic(
                "invalid_source_id",
                "Invalid source/reference ID.",
                row_number,
                "source_id",
                record.source_id,
            )
        )
    if record.claim_scope.strip().casefold() == "species":
        diagnostics.extend(_required(record.species_id, "species_id", row_number))
    if record.species_id and not SPECIES_ID_PATTERN.fullmatch(record.species_id):
        diagnostics.append(
            _diagnostic(
                "invalid_species_id",
                "Invalid BC-NPPD species ID.",
                row_number,
                "species_id",
                record.species_id,
            )
        )
    if record.evidence_confidence not in EVIDENCE_CONFIDENCE_VALUES:
        diagnostics.append(
            _diagnostic(
                "invalid_evidence_confidence",
                "Invalid evidence confidence.",
                row_number,
                "evidence_confidence",
                record.evidence_confidence,
            )
        )
    if record.external_id:
        diagnostics.extend(_validate_external_id(record.external_id, row_number))
    if record.review_status not in review_status_values():
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


def _validate_materialization_manifest(
    record: MaterializationManifest, row_number: int
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    diagnostics.extend(_required(record.manifest_id, "manifest_id", row_number))
    diagnostics.extend(_required(record.source_id, "source_id", row_number))
    diagnostics.extend(_required(record.artifact_type, "artifact_type", row_number))
    if record.source_id and not SOURCE_ID_PATTERN.fullmatch(record.source_id):
        diagnostics.append(
            _diagnostic(
                "invalid_source_id",
                "Invalid source/reference ID.",
                row_number,
                "source_id",
                record.source_id,
            )
        )
    if record.status not in materialization_status_values():
        diagnostics.append(
            _diagnostic(
                "invalid_materialization_status",
                "Invalid materialization status.",
                row_number,
                "status",
                record.status,
            )
        )
    if record.external_id:
        diagnostics.extend(_validate_external_id(record.external_id, row_number))
    if record.review_status not in review_status_values():
        diagnostics.append(
            _diagnostic(
                "invalid_review_status",
                "Invalid review status.",
                row_number,
                "review_status",
                record.review_status,
            )
        )
    if (
        record.status == MaterializationStatus.ACCEPTED.value
        and not is_review_accepted(record.review_status)
    ):
        diagnostics.append(
            _diagnostic(
                "unreviewed_materialization",
                "Accepted materialization requires accepted or manually corrected review status.",
                row_number,
                "review_status",
                record.review_status,
            )
        )
    return diagnostics


def _validate_media_manifest(record: MediaExtractionManifest, row_number: int) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    diagnostics.extend(_required(record.extraction_id, "extraction_id", row_number))
    diagnostics.extend(_required(record.source_id, "source_id", row_number))
    diagnostics.extend(_required(record.source_document_id, "source_document_id", row_number))
    if record.source_id and not SOURCE_ID_PATTERN.fullmatch(record.source_id):
        diagnostics.append(
            _diagnostic(
                "invalid_source_id",
                "Invalid source/reference ID.",
                row_number,
                "source_id",
                record.source_id,
            )
        )
    if record.review_status not in review_status_values():
        diagnostics.append(
            _diagnostic(
                "invalid_review_status",
                "Invalid review status.",
                row_number,
                "review_status",
                record.review_status,
            )
        )
    if record.external_id:
        diagnostics.extend(_validate_external_id(record.external_id, row_number))
    if record.accepted_table_path and not is_review_accepted(record.review_status):
        diagnostics.append(
            _diagnostic(
                "unreviewed_media_extraction",
                "Accepted media table path requires accepted or manually corrected review status.",
                row_number,
                "review_status",
                record.review_status,
            )
        )
    return diagnostics


def _validate_external_id(value: str, row_number: int) -> list[Diagnostic]:
    if not EXTERNAL_ID_PATTERN.fullmatch(value):
        return [
            _diagnostic(
                "invalid_external_id",
                "External IDs must be namespaced, e.g. bcdc:package:<id>.",
                row_number,
                "external_id",
                value,
            )
        ]
    return []


def _required(value: str, field: str, row_number: int) -> list[Diagnostic]:
    if value:
        return []
    return [
        _diagnostic(
            "missing_required_field",
            f"Missing required field: {field}.",
            row_number,
            field,
        )
    ]


def _diagnose_excluded_in_mapping(row: Mapping[str, object], row_number: int) -> list[Diagnostic]:
    row_text = " ".join(_flatten_values(row))
    diagnostics: list[Diagnostic] = []
    for url in sorted(EXCLUDED_SOURCE_URLS):
        if url in row_text:
            diagnostics.append(
                _diagnostic(
                    "excluded_source",
                    f"Excluded source URL found: {url}",
                    row_number,
                    value=url,
                )
            )
    return diagnostics


def _flatten_values(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        flattened: list[str] = []
        for nested in value.values():
            flattened.extend(_flatten_values(nested))
        return flattened
    if isinstance(value, (list, tuple, set)):
        flattened = []
        for nested in value:
            flattened.extend(_flatten_values(nested))
        return flattened
    return [str(value)]


def _diagnostic(
    code: str,
    message: str,
    row_number: int,
    field: str | None = None,
    value: str | None = None,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        message=message,
        severity=Severity.ERROR,
        row_number=row_number,
        field=field,
        value=value,
    )


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
