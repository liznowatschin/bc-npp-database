"""E-Flora BC attribute boost sandbox generation."""

from __future__ import annotations

import csv
import html
import json
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib import parse, request
from urllib.robotparser import RobotFileParser

from .config import EVIDENCE_CONFIDENCE_VALUES
from .diagnostics import Diagnostic, Severity
from .sources import (
    SourceAttributionRecord,
    validate_source_attribution_records,
)
from .validate import diagnose_excluded_sources

EFLORA_BASE_URL = "https://linnet.geog.ubc.ca/Atlas/Atlas.aspx"
EFLORA_SOURCE_ID = "SRC-9001"
EFLORA_SOURCE_NAME = "E-Flora BC"
EFLORA_SOURCE_TIER = "Tier 2"
EFLORA_USER_AGENT = "bc-npp-database-eflora-boost/0.1"

BOOST_REQUIRED_FILES = (
    "resolved_species.csv",
    "candidate_attributes.csv",
    "source_attribution.csv",
    "synonyms.csv",
    "diagnostics.csv",
    "manifest.json",
)

RESOLVED_FIELDS = (
    "species_id",
    "input_botanical_name",
    "resolved_botanical_name",
    "atlas_url",
    "match_status",
    "review_status",
    "source_id",
    "source_tier",
    "citation",
    "external_id",
    "access_date",
)

ATTRIBUTE_FIELDS = (
    "species_id",
    "input_botanical_name",
    "resolved_botanical_name",
    "attribute_name",
    "attribute_value",
    "evidence_confidence",
    "source_id",
    "source_url",
    "external_id",
    "review_status",
    "notes",
)

SYNONYM_FIELDS = (
    "species_id",
    "resolved_botanical_name",
    "synonym",
    "source_id",
    "source_url",
    "review_status",
)

DIAGNOSTIC_FIELDS = ("severity", "code", "message", "field", "value")


@dataclass(frozen=True)
class EFloraResolveResult:
    """One E-Flora species resolution summary."""

    species_name: str
    atlas_url: str
    match_status: str
    diagnostics: tuple[Diagnostic, ...]
    source_text: str = ""

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "species_name": self.species_name,
            "atlas_url": self.atlas_url,
            "match_status": self.match_status,
            "source_text_available": bool(self.source_text),
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


@dataclass(frozen=True)
class EFloraBoostResult:
    """Generated E-Flora boost sandbox summary."""

    path: str
    counts: dict[str, int]
    diagnostics: tuple[Diagnostic, ...]
    paths: dict[str, str]

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "counts": self.counts,
            "paths": self.paths,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


@dataclass(frozen=True)
class EFloraPreviewResult:
    """Review-gated E-Flora preview application summary."""

    path: str
    counts: dict[str, int]
    diagnostics: tuple[Diagnostic, ...]
    paths: dict[str, str]

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "counts": self.counts,
            "paths": self.paths,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


def eflora_atlas_url(species_name: str) -> str:
    """Return the deterministic E-Flora atlas URL for a botanical name."""
    normalized = normalize_botanical_name(species_name)
    return f"{EFLORA_BASE_URL}?sciname={parse.quote_plus(normalized)}"


def normalize_botanical_name(species_name: str) -> str:
    """Normalize whitespace and botanical capitalization for URL/query use."""
    parts = species_name.replace(".", "").split()
    if not parts:
        return ""
    rank_markers = {"ssp", "subsp", "var", "x"}
    normalized: list[str] = []
    for index, part in enumerate(parts):
        if index == 0:
            normalized.append(part[:1].upper() + part[1:].lower())
        elif part.casefold() in rank_markers:
            normalized.append(part.casefold())
        else:
            normalized.append(part.lower())
    return " ".join(normalized)


def eflora_external_id(species_name: str) -> str:
    """Return a source external ID for an E-Flora atlas record."""
    token = re.sub(r"[^a-z0-9]+", "_", normalize_botanical_name(species_name).casefold()).strip(
        "_"
    )
    return f"eflora:atlas:{token}"


def resolve_eflora_species(
    species_name: str,
    *,
    input_dir: Path | None = None,
    live_fetch: bool = False,
    raw_dir: Path = Path("local/eflora_raw"),
) -> EFloraResolveResult:
    """Resolve one species to an E-Flora atlas page."""
    normalized = normalize_botanical_name(species_name)
    atlas_url = eflora_atlas_url(normalized)
    diagnostics: list[Diagnostic] = []
    source_text = ""
    if input_dir is not None:
        fixture = input_dir / f"{_species_slug(normalized)}.html"
        if fixture.exists():
            source_text = fixture.read_text(encoding="utf-8")
        else:
            diagnostics.append(
                _diagnostic(
                    "eflora_fixture_missing",
                    "E-Flora fixture page is missing.",
                    field="species_name",
                    value=normalized,
                )
            )
    elif live_fetch:
        if not _robots_allows(atlas_url):
            diagnostics.append(
                _diagnostic(
                    "eflora_robots_disallowed",
                    "E-Flora robots.txt does not allow the configured atlas URL.",
                    field="atlas_url",
                    value=atlas_url,
                )
            )
        else:
            try:
                source_text = _fetch_url(atlas_url)
            except OSError as exc:
                diagnostics.append(
                    _diagnostic(
                        "eflora_fetch_failed",
                        "E-Flora atlas fetch failed.",
                        field="atlas_url",
                        value=f"{atlas_url}: {exc}",
                    )
                )
            else:
                raw_dir.mkdir(parents=True, exist_ok=True)
                (raw_dir / f"{_species_slug(normalized)}.html").write_text(
                    source_text,
                    encoding="utf-8",
                )
    else:
        diagnostics.append(
            _diagnostic(
                "eflora_input_required",
                "E-Flora resolution requires --input-dir or --live-fetch.",
                field="species_name",
                value=normalized,
            )
        )

    match_status = (
        "exact" if source_text and _page_mentions_species(source_text, normalized) else ""
    )
    if source_text and not match_status:
        match_status = "needs_taxonomy_review"
        diagnostics.append(
            _diagnostic(
                "eflora_species_match_ambiguous",
                "E-Flora page did not clearly match the requested species.",
                Severity.WARNING,
                field="species_name",
                value=normalized,
            )
        )
    return EFloraResolveResult(
        species_name=normalized,
        atlas_url=atlas_url,
        match_status=match_status,
        diagnostics=tuple(diagnostics),
        source_text=source_text,
    )


def build_eflora_boost(
    species_csv: Path,
    out_dir: Path,
    *,
    input_dir: Path | None = None,
    live_fetch: bool = False,
    raw_dir: Path = Path("local/eflora_raw"),
    access_date: str | None = None,
) -> EFloraBoostResult:
    """Build a review-gated E-Flora candidate attribute boost sandbox."""
    out_dir.mkdir(parents=True, exist_ok=True)
    access_date = access_date or date.today().isoformat()
    diagnostics: list[Diagnostic] = []
    resolved_rows: list[dict[str, str]] = []
    attribute_rows: list[dict[str, str]] = []
    attribution_rows: list[dict[str, str]] = []
    synonym_rows: list[dict[str, str]] = []

    for species_row in _read_csv(species_csv):
        species_id = _first(species_row, "Species ID", "species_id")
        input_name = _first(species_row, "Botanical Name", "botanical_name", "species_name")
        if not input_name:
            diagnostics.append(
                _diagnostic(
                    "eflora_missing_species_name",
                    "Input species row is missing a botanical name.",
                    field="botanical_name",
                )
            )
            continue
        resolved = resolve_eflora_species(
            input_name,
            input_dir=input_dir,
            live_fetch=live_fetch,
            raw_dir=raw_dir,
        )
        diagnostics.extend(resolved.diagnostics)
        if not resolved.source_text:
            continue
        parsed = parse_eflora_atlas_page(
            resolved.source_text,
            input_name=input_name,
            species_id=species_id,
            atlas_url=resolved.atlas_url,
            access_date=access_date,
        )
        diagnostics.extend(parsed["diagnostics"])
        resolved_rows.append(parsed["resolved"])
        attribute_rows.extend(parsed["attributes"])
        attribution_rows.extend(parsed["attributions"])
        synonym_rows.extend(parsed["synonyms"])

    paths = _boost_paths(out_dir)
    _write_csv(Path(paths["resolved_species"]), resolved_rows, RESOLVED_FIELDS)
    _write_csv(Path(paths["candidate_attributes"]), attribute_rows, ATTRIBUTE_FIELDS)
    _write_csv(
        Path(paths["source_attribution"]),
        attribution_rows,
        tuple(SourceAttributionRecord("", "", "").to_dict()),
    )
    _write_csv(Path(paths["synonyms"]), synonym_rows, SYNONYM_FIELDS)
    _write_csv(
        Path(paths["diagnostics"]),
        [diagnostic.to_dict() for diagnostic in diagnostics]
        or [
            {
                "severity": Severity.INFO.value,
                "code": "eflora_boost_generated",
                "message": "E-Flora boost sandbox generated.",
            }
        ],
        DIAGNOSTIC_FIELDS,
    )
    _write_json(
        Path(paths["manifest"]),
        {
            "artifact_name": "E-Flora Attribute Boost Sandbox",
            "input_species_csv": str(species_csv),
            "source_name": EFLORA_SOURCE_NAME,
            "source_tier": EFLORA_SOURCE_TIER,
            "resolved_species_count": len(resolved_rows),
            "candidate_attribute_count": len(attribute_rows),
            "source_attribution_count": len(attribution_rows),
            "synonym_count": len(synonym_rows),
            "access_date": access_date,
            "public_hygiene": {
                "raw_eflora_html_tracked": False,
                "external_downloads_required": live_fetch,
                "private_data_tracked": False,
            },
            "caveat": "E-Flora boost rows are candidate attributes pending BC-NPPD review.",
        },
    )
    validation = validate_eflora_boost(out_dir)
    return EFloraBoostResult(
        path=str(out_dir),
        counts=validation.counts,
        diagnostics=tuple(diagnostics) + validation.diagnostics,
        paths=paths,
    )


def parse_eflora_atlas_page(
    page_html: str,
    *,
    input_name: str,
    species_id: str,
    atlas_url: str,
    access_date: str,
) -> dict[str, Any]:
    """Parse one E-Flora atlas page into boost rows."""
    text = _plain_text(page_html)
    resolved_name = _extract_resolved_name(text) or normalize_botanical_name(input_name)
    citation = _citation(resolved_name, access_date)
    external_id = eflora_external_id(resolved_name)
    resolved = {
        "species_id": species_id,
        "input_botanical_name": normalize_botanical_name(input_name),
        "resolved_botanical_name": resolved_name,
        "atlas_url": atlas_url,
        "match_status": (
            "exact"
            if resolved_name.casefold() == normalize_botanical_name(input_name).casefold()
            else "needs_taxonomy_review"
        ),
        "review_status": "pending_review",
        "source_id": EFLORA_SOURCE_ID,
        "source_tier": EFLORA_SOURCE_TIER,
        "citation": citation,
        "external_id": external_id,
        "access_date": access_date,
    }
    diagnostics: list[Diagnostic] = []
    attributes: list[tuple[str, str]] = []

    family = _extract_family(text)
    if family:
        attributes.append(("family", family))
    common_name = _extract_common_name(text, resolved_name)
    if common_name:
        attributes.append(("common_name", common_name))
    habitat = _extract_section(
        text,
        ("Habitat / Range", "Habitat and Range"),
        ("Ecology", "Status Information", "Synonyms"),
    )
    if habitat:
        attributes.append(("habitat_range", habitat))
    else:
        diagnostics.append(_missing_section("habitat_range", resolved_name))
    for name, value in _extract_status_attributes(text).items():
        attributes.append((name, value))
    for name, value in _extract_ecology_attributes(text).items():
        attributes.append((name, value))
    bloom = _extract_label_value(text, "Blooming Period")
    if bloom:
        attributes.append(("blooming_period", bloom))

    attribute_rows = [
        {
            "species_id": species_id,
            "input_botanical_name": normalize_botanical_name(input_name),
            "resolved_botanical_name": resolved_name,
            "attribute_name": name,
            "attribute_value": value,
            "evidence_confidence": "Pending review",
            "source_id": EFLORA_SOURCE_ID,
            "source_url": atlas_url,
            "external_id": external_id,
            "review_status": "pending_review",
            "notes": "Candidate E-Flora boost value; review required before promotion.",
        }
        for name, value in attributes
        if value
    ]
    attribution_rows = [
        SourceAttributionRecord(
            source_id=EFLORA_SOURCE_ID,
            species_id=species_id,
            claim_field=row["attribute_name"],
            claim_value=row["attribute_value"],
            claim_scope="species",
            evidence_confidence="Pending review",
            external_id=external_id,
            review_status="pending_review",
            notes=row["notes"],
        ).to_dict()
        for row in attribute_rows
    ]
    synonym_rows = [
        {
            "species_id": species_id,
            "resolved_botanical_name": resolved_name,
            "synonym": synonym,
            "source_id": EFLORA_SOURCE_ID,
            "source_url": atlas_url,
            "review_status": "pending_review",
        }
        for synonym in _extract_synonyms(text)
    ]
    return {
        "resolved": resolved,
        "attributes": attribute_rows,
        "attributions": attribution_rows,
        "synonyms": synonym_rows,
        "diagnostics": diagnostics,
    }


def validate_eflora_boost(path: Path) -> EFloraBoostResult:
    """Validate an E-Flora boost sandbox directory."""
    diagnostics: list[Diagnostic] = []
    paths = _boost_paths(path)
    counts = {key: 0 for key in paths}
    for filename in BOOST_REQUIRED_FILES:
        if not (path / filename).exists():
            diagnostics.append(
                _diagnostic(
                    "eflora_missing_boost_file",
                    "Missing E-Flora boost file.",
                    field="path",
                    value=filename,
                )
            )
    if diagnostics:
        return EFloraBoostResult(str(path), counts, tuple(diagnostics), paths)

    resolved_rows = _read_csv(path / "resolved_species.csv")
    attribute_rows = _read_csv(path / "candidate_attributes.csv")
    attribution_rows = _read_csv(path / "source_attribution.csv")
    synonym_rows = _read_csv(path / "synonyms.csv")
    diagnostic_rows = _read_csv(path / "diagnostics.csv")
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    counts.update(
        {
            "resolved_species": len(resolved_rows),
            "candidate_attributes": len(attribute_rows),
            "source_attribution": len(attribution_rows),
            "synonyms": len(synonym_rows),
            "diagnostics": len(diagnostic_rows),
        }
    )
    diagnostics.extend(_validate_required_fields(resolved_rows, RESOLVED_FIELDS, "resolved"))
    diagnostics.extend(_validate_required_fields(attribute_rows, ATTRIBUTE_FIELDS, "attribute"))
    diagnostics.extend(validate_source_attribution_records(attribution_rows))
    diagnostics.extend(diagnose_excluded_sources(resolved_rows + attribute_rows + synonym_rows))
    diagnostics.extend(_validate_manifest_counts(manifest, counts))
    for row_number, row in enumerate(attribute_rows, start=2):
        if row.get("evidence_confidence", "") not in EVIDENCE_CONFIDENCE_VALUES:
            diagnostics.append(
                _diagnostic(
                    "eflora_invalid_evidence_confidence",
                    "Invalid evidence confidence.",
                    row_number=row_number,
                    field="evidence_confidence",
                    value=row.get("evidence_confidence"),
                )
            )
    for index, row in enumerate(diagnostic_rows, start=2):
        if row.get("severity") == Severity.ERROR.value:
            diagnostics.append(
                _diagnostic(
                    "eflora_boost_diagnostics_contain_error",
                    "E-Flora boost diagnostics contain an error.",
                    row_number=index,
                    field="code",
                    value=row.get("code"),
                )
            )
    return EFloraBoostResult(str(path), counts, tuple(diagnostics), paths)


def apply_eflora_boost(boost_dir: Path, poc_dir: Path, out_dir: Path) -> EFloraPreviewResult:
    """Apply E-Flora boost rows into an ignored preview output."""
    validation = validate_eflora_boost(boost_dir)
    diagnostics = list(validation.diagnostics)
    if has_error_diagnostics(diagnostics):
        return EFloraPreviewResult(str(out_dir), {}, tuple(diagnostics), _preview_paths(out_dir))
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(poc_dir, out_dir)
    boost_preview_dir = out_dir / "eflora_boost"
    boost_preview_dir.mkdir(parents=True, exist_ok=True)
    for filename in BOOST_REQUIRED_FILES:
        shutil.copyfile(boost_dir / filename, boost_preview_dir / filename)

    plant_path = out_dir / "plant_list.csv"
    plant_rows = _read_csv(plant_path)
    attribute_rows = _read_csv(boost_dir / "candidate_attributes.csv")
    by_species = {
        (row.get("Species ID") or row.get("species_id") or ""): row for row in plant_rows
    }
    applied = 0
    skipped = 0
    for attr in attribute_rows:
        plant = by_species.get(attr.get("species_id", ""))
        target = _plant_field(attr.get("attribute_name", ""))
        if not plant or not target:
            skipped += 1
            continue
        current = plant.get(target, "").strip()
        if current and current not in {"Unknown", "Pending review"}:
            skipped += 1
            continue
        plant[target] = attr.get("attribute_value", "")
        plant["evidence_status"] = "candidate_eflora_boost_preview"
        applied += 1
    _write_csv(plant_path, plant_rows, tuple(plant_rows[0]) if plant_rows else ())

    counts = {
        "plant_rows": len(plant_rows),
        "boost_attributes": len(attribute_rows),
        "applied_preview_values": applied,
        "skipped_existing_values": skipped,
    }
    paths = _preview_paths(out_dir)
    _write_json(
        out_dir / "eflora_boost_preview_manifest.json",
        {
            "artifact_name": "E-Flora Boost Preview",
            "boost_dir": str(boost_dir),
            "poc_dir": str(poc_dir),
            "counts": counts,
            "caveat": "Preview only; E-Flora boost values remain candidate pending review.",
        },
    )
    return EFloraPreviewResult(str(out_dir), counts, tuple(diagnostics), paths)


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...] | list[Diagnostic]) -> bool:
    """Return whether diagnostics include an error."""
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


def _extract_resolved_name(text: str) -> str:
    match = re.search(
        r"\b([A-Z][a-z-]+\s+[a-z][a-z-]+(?:\s+(?:ssp|subsp|var)\s+[a-z][a-z-]+)?)\b",
        text,
    )
    return normalize_botanical_name(match.group(1)) if match else ""


def _extract_common_name(text: str, resolved_name: str) -> str:
    pattern = re.escape(resolved_name) + r".{0,120}?\n\s*([a-z][A-Za-z' -]+(?:\([^)]*\))?)"
    match = re.search(pattern, text)
    if match:
        return _clean(match.group(1))
    return ""


def _extract_family(text: str) -> str:
    match = re.search(r"\b([A-Z][A-Za-z]+aceae)\s+\([^)]*family\)", text)
    return match.group(1) if match else ""


def _extract_status_attributes(text: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    origin = re.search(r"\b(Native|Exotic)\s*S[0-9NA?]+", text)
    if origin:
        attrs["origin_status"] = origin.group(1)
    bc_list = re.search(r"\b(Red|Blue|Yellow|Exotic)\s*Not Listed", text)
    if bc_list:
        attrs["bc_list_status"] = bc_list.group(1)
    provincial = re.search(r"\b(Native|Exotic)?\s*(S[0-9NA?]+)\s*\([0-9]{4}\)", text)
    if provincial:
        attrs["provincial_status"] = provincial.group(2)
    return attrs


def _extract_ecology_attributes(text: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    elevation = _three_number_metric(text, "Elevation")
    if elevation:
        attrs["elevation_metres_min_avg_max"] = elevation
    smr = _three_number_metric(text, "Soil Moisture Regime")
    if smr:
        attrs["soil_moisture_regime_min_avg_max"] = smr
    nutrient = re.search(r"Modal Nutrient Regime\s+Class\s+([A-Z])", text)
    if nutrient:
        attrs["modal_nutrient_regime_class"] = nutrient.group(1)
    bec = re.search(r"Modal BEC Zone Class\s+([A-Z]+)", text)
    if bec:
        attrs["modal_bec_zone_class"] = bec.group(1)
    all_bec = re.search(r"All\s+BEC Zones.*?recorded in:?\s*([A-Z0-9(), ]+)", text)
    if all_bec:
        attrs["bec_zones_recorded"] = _clean(all_bec.group(1))
    return attrs


def _three_number_metric(text: str, label: str) -> str:
    match = re.search(re.escape(label) + r".{0,180}?(-?\d+)\s+(-?\d+)\s+(-?\d+)", text, re.S)
    return " / ".join(match.groups()) if match else ""


def _extract_label_value(text: str, label: str) -> str:
    match = re.search(re.escape(label) + r":?\s+([A-Za-z][A-Za-z -]+)", text)
    return _clean(match.group(1)) if match else ""


def _extract_section(text: str, starts: tuple[str, ...], stops: tuple[str, ...]) -> str:
    for start in starts:
        start_index = text.find(start)
        if start_index == -1:
            continue
        section = text[start_index + len(start) :]
        stop_indexes = [section.find(stop) for stop in stops if section.find(stop) != -1]
        if stop_indexes:
            section = section[: min(stop_indexes)]
        section = re.sub(r"Source:.*", "", section)
        return _clean(section)
    return ""


def _extract_synonyms(text: str) -> list[str]:
    section = _extract_section(
        text,
        ("Synonyms and Alternate Names", "Synonyms"),
        ("Taxonomic", "Additional", "References", "Recommended citation", "©"),
    )
    if not section:
        return []
    candidates = re.findall(
        r"\b[A-Z][a-z-]+\s+[a-z][a-z-]+(?:\s+(?:ssp|subsp|var)\s+[a-z][a-z-]+)?\b",
        section,
    )
    return sorted({_clean(candidate) for candidate in candidates})


def _page_mentions_species(page_html: str, species_name: str) -> bool:
    return normalize_botanical_name(species_name).casefold() in _plain_text(page_html).casefold()


def _citation(species_name: str, access_date: str) -> str:
    return (
        f"Klinkenberg, Brian. (Editor) 2023. E-Flora BC: Electronic Atlas of the "
        f"Flora of British Columbia. Atlas page for {species_name}. "
        f"Lab for Advanced Spatial Analysis, Department of Geography, University "
        f"of British Columbia, Vancouver. Accessed {access_date}."
    )


def _boost_paths(path: Path) -> dict[str, str]:
    return {
        filename.removesuffix(".csv").removesuffix(".json"): str(path / filename)
        for filename in BOOST_REQUIRED_FILES
    }


def _preview_paths(path: Path) -> dict[str, str]:
    return {
        "plant_list": str(path / "plant_list.csv"),
        "eflora_boost": str(path / "eflora_boost"),
        "manifest": str(path / "eflora_boost_preview_manifest.json"),
    }


def _validate_required_fields(
    rows: list[dict[str, str]],
    fields: tuple[str, ...],
    label: str,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        for field in fields:
            if field in {"species_id"}:
                continue
            if not row.get(field, "").strip():
                diagnostics.append(
                    _diagnostic(
                        f"eflora_missing_{label}_field",
                        "E-Flora boost row is missing a required field.",
                        row_number=row_number,
                        field=field,
                    )
                )
    return diagnostics


def _validate_manifest_counts(manifest: dict[str, Any], counts: dict[str, int]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    expected = {
        "resolved_species_count": counts["resolved_species"],
        "candidate_attribute_count": counts["candidate_attributes"],
        "source_attribution_count": counts["source_attribution"],
        "synonym_count": counts["synonyms"],
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            diagnostics.append(
                _diagnostic(
                    "eflora_manifest_count_mismatch",
                    "E-Flora boost manifest count does not match table row count.",
                    field=key,
                    value=str(manifest.get(key)),
                )
            )
    hygiene = manifest.get("public_hygiene", {})
    if not isinstance(hygiene, dict) or hygiene.get("raw_eflora_html_tracked") is not False:
        diagnostics.append(
            _diagnostic(
                "eflora_invalid_public_hygiene",
                "E-Flora boost manifest must record raw E-Flora HTML as untracked.",
                field="public_hygiene",
            )
        )
    return diagnostics


def _plant_field(attribute_name: str) -> str:
    return {
        "family": "Family",
        "common_name": "Common Name",
        "origin_status": "Native Status",
        "soil_moisture_regime_min_avg_max": "Soil Moisture",
    }.get(attribute_name, "")


def _plain_text(page_html: str) -> str:
    value = re.sub(r"<(br|/p|/h[1-6]|/div|/li|/tr)[^>]*>", "\n", page_html, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return "\n".join(_clean(line) for line in value.splitlines() if _clean(line))


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write_csv(path: Path, rows: list[dict[str, object]], fields: tuple[str, ...]) -> None:
    fieldnames = list(fields)
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        if row.get(key):
            return row[key].strip()
    return ""


def _species_slug(species_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", normalize_botanical_name(species_name).casefold()).strip(
        "_"
    )


def _fetch_url(url: str) -> str:
    req = request.Request(url, headers={"User-Agent": EFLORA_USER_AGENT})
    with request.urlopen(req, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def _robots_allows(url: str) -> bool:
    parsed = parse.urlparse(url)
    robots_url = parse.urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except OSError:
        return False
    return parser.can_fetch(EFLORA_USER_AGENT, url)


def _missing_section(field: str, species_name: str) -> Diagnostic:
    return _diagnostic(
        "eflora_missing_section",
        "E-Flora atlas page did not include a target section.",
        Severity.WARNING,
        field=field,
        value=species_name,
    )


def _diagnostic(
    code: str,
    message: str,
    severity: Severity = Severity.ERROR,
    row_number: int | None = None,
    field: str | None = None,
    value: str | None = None,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        message=message,
        severity=severity,
        row_number=row_number,
        field=field,
        value=value,
    )
