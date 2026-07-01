"""Validation helpers for BC-NPPD records and source policy."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from .config import (
    EVIDENCE_CONFIDENCE_COLUMNS,
    EVIDENCE_CONFIDENCE_VALUES,
    EXCLUDED_SOURCE_URLS,
    SPECIES_ID_COLUMNS,
)
from .diagnostics import Diagnostic, Severity


def find_excluded_sources(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    """Return rows containing explicitly excluded source URLs in any field."""
    violations: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        row_text = " ".join(str(value) for value in row.values() if value is not None)
        for url in sorted(EXCLUDED_SOURCE_URLS):
            if url in row_text:
                violations.append({"row_number": index, "excluded_url": url, "row": dict(row)})
    return violations


def find_duplicate_species_ids(rows: Iterable[Mapping[str, object]]) -> list[str]:
    """Return duplicated nonblank BC-NPPD species ID values."""
    seen: set[str] = set()
    duplicates: set[str] = set()
    for row in rows:
        species_id = _first_present_value(row, SPECIES_ID_COLUMNS)
        if species_id == "":
            continue
        if species_id in seen:
            duplicates.add(species_id)
        seen.add(species_id)
    return sorted(duplicates)


def find_invalid_evidence_confidence(
    rows: Iterable[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Return rows with unsupported evidence confidence or evidence level values."""
    invalid: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        value = _first_present_value(row, EVIDENCE_CONFIDENCE_COLUMNS)
        if value not in EVIDENCE_CONFIDENCE_VALUES:
            invalid.append({"row_number": index, "value": value, "row": dict(row)})
    return invalid


def diagnose_excluded_sources(rows: Iterable[Mapping[str, object]]) -> list[Diagnostic]:
    """Return diagnostics for rows containing explicitly excluded source URLs."""
    diagnostics: list[Diagnostic] = []
    for violation in find_excluded_sources(rows):
        diagnostics.append(
            Diagnostic(
                code="excluded_source",
                message=f"Excluded source URL found: {violation['excluded_url']}",
                severity=Severity.ERROR,
                row_number=int(violation["row_number"]),
                value=str(violation["excluded_url"]),
            )
        )
    return diagnostics


def diagnose_duplicate_species_ids(rows: Iterable[Mapping[str, object]]) -> list[Diagnostic]:
    """Return diagnostics for duplicated species IDs."""
    return [
        Diagnostic(
            code="duplicate_species_id",
            message=f"Duplicate species ID found: {species_id}",
            severity=Severity.ERROR,
            value=species_id,
        )
        for species_id in find_duplicate_species_ids(rows)
    ]


def diagnose_invalid_evidence_confidence(
    rows: Iterable[Mapping[str, object]],
) -> list[Diagnostic]:
    """Return diagnostics for unsupported evidence confidence values."""
    diagnostics: list[Diagnostic] = []
    for invalid in find_invalid_evidence_confidence(rows):
        diagnostics.append(
            Diagnostic(
                code="invalid_evidence_confidence",
                message=f"Unsupported evidence confidence value: {invalid['value']}",
                severity=Severity.ERROR,
                row_number=int(invalid["row_number"]),
                value=str(invalid["value"]),
            )
        )
    return diagnostics


def _first_present_value(row: Mapping[str, object], keys: Iterable[str]) -> str:
    for key in keys:
        if key in row:
            value = row[key]
            return "" if value is None else str(value).strip()
    return ""
