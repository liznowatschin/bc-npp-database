"""Provider sandbox generation and review-page building."""

from __future__ import annotations

import csv
import html
import json
import shutil
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib import request
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

from .diagnostics import Diagnostic, Severity
from .providers import (
    SANDBOX_REQUIRED_COLUMNS,
    SANDBOX_REQUIRED_FILES,
    validate_provider_sandbox,
)
from .sources import ReviewStatus, load_mapping_records

PROVIDER_REGISTRY = Path("data/source_providers/provider_registry.csv")
USER_AGENT = "bc-npp-database-provider-sandbox/0.1"


@dataclass(frozen=True)
class ProviderScrapeResult:
    """Generated provider sandbox summary."""

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


@dataclass(frozen=True)
class ProviderReviewResult:
    """Generated provider review bundle summary."""

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


def scrape_provider_sandbox(
    provider_id: str,
    database_instance: str,
    output_dir: Path,
    *,
    input_dir: Path | None = None,
    live_fetch: bool = False,
    raw_dir: Path = Path("local/provider_raw"),
) -> ProviderScrapeResult:
    """Generate provider sandbox CSV artifacts from fixtures or optional live fetches."""
    output_dir.mkdir(parents=True, exist_ok=True)
    provider = _provider_record(provider_id)
    diagnostics: list[Diagnostic] = []
    pages = _load_provider_pages(provider, input_dir, live_fetch, raw_dir, diagnostics)
    parsed_records = [_parse_provider_page(provider_id, page) for page in pages]
    tables = _build_sandbox_tables(provider_id, parsed_records, diagnostics)
    paths = _sandbox_paths(output_dir)

    for name, rows in tables.items():
        _write_csv(Path(paths[name.removesuffix(".csv")]), rows, SANDBOX_REQUIRED_COLUMNS[name])
    _write_json(
        Path(paths["manifest"]),
        {
            "database_instance": database_instance,
            "provider_ids": [provider_id],
            "inventory_page_count": len(tables["inventory_pages.csv"]),
            "candidate_species_count": len(tables["candidate_species.csv"]),
            "candidate_attribute_count": len(tables["candidate_attributes.csv"]),
            "supplier_availability_count": len(tables["supplier_availability.csv"]),
            "mowability_count": len(tables["mowability.csv"]),
            "public_hygiene": {
                "raw_provider_html_tracked": False,
                "external_downloads_required": live_fetch,
                "private_data_tracked": False,
            },
            "caveat": "Provider scrape sandbox rows are observations pending review.",
        },
    )
    _write_csv(
        Path(paths["diagnostics"]),
        [diagnostic.to_dict() for diagnostic in diagnostics]
        or [
            {
                "severity": Severity.INFO.value,
                "code": "provider_sandbox_generated",
                "message": "Provider sandbox generated from fixture or fetched pages.",
            }
        ],
        SANDBOX_REQUIRED_COLUMNS["diagnostics.csv"],
    )

    validation = validate_provider_sandbox(output_dir)
    return ProviderScrapeResult(
        path=str(output_dir),
        counts=validation.counts,
        diagnostics=tuple(diagnostics) + validation.diagnostics,
        paths=paths,
    )


def build_provider_review(sandbox_dir: Path, output_dir: Path) -> ProviderReviewResult:
    """Build a static review bundle from a validated provider sandbox directory."""
    validation = validate_provider_sandbox(sandbox_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "index": str(output_dir / "index.html"),
        "manifest": str(output_dir / "manifest.json"),
        "diagnostics": str(output_dir / "diagnostics.csv"),
    }
    for filename in SANDBOX_REQUIRED_FILES:
        source = sandbox_dir / filename
        if source.exists() and filename.endswith(".csv"):
            destination = output_dir / filename
            shutil.copyfile(source, destination)
            paths[filename.removesuffix(".csv")] = str(destination)

    species_rows = _read_csv(sandbox_dir / "candidate_species.csv")
    attribute_rows = _read_csv(sandbox_dir / "candidate_attributes.csv")
    supplier_rows = _read_csv(sandbox_dir / "supplier_availability.csv")
    mowability_rows = _read_csv(sandbox_dir / "mowability.csv")
    Path(paths["index"]).write_text(
        _render_review_html(species_rows, attribute_rows, supplier_rows, mowability_rows),
        encoding="utf-8",
    )
    _write_json(
        Path(paths["manifest"]),
        {
            "artifact_name": "Provider Review Bundle",
            "input_sandbox_dir": str(sandbox_dir),
            "candidate_species_count": len(species_rows),
            "candidate_attribute_count": len(attribute_rows),
            "supplier_availability_count": len(supplier_rows),
            "mowability_count": len(mowability_rows),
            "public_hygiene": {
                "external_assets_required": False,
                "raw_provider_html_tracked": False,
                "private_data_tracked": False,
            },
            "caveat": "Review bundle is for approval triage; it does not update the PoC.",
        },
    )
    _write_csv(
        Path(paths["diagnostics"]),
        [diagnostic.to_dict() for diagnostic in validation.diagnostics]
        or [
            {
                "severity": Severity.INFO.value,
                "code": "provider_review_generated",
                "message": "Provider review bundle generated.",
            }
        ],
        SANDBOX_REQUIRED_COLUMNS["diagnostics.csv"],
    )
    return ProviderReviewResult(
        path=str(output_dir),
        counts={
            "candidate_species": len(species_rows),
            "candidate_attributes": len(attribute_rows),
            "supplier_availability": len(supplier_rows),
            "mowability": len(mowability_rows),
        },
        diagnostics=validation.diagnostics,
        paths=paths,
    )


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...] | list[Diagnostic]) -> bool:
    """Return whether diagnostics include an error."""
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


def _provider_record(provider_id: str) -> dict[str, object]:
    for row in load_mapping_records(PROVIDER_REGISTRY):
        if row.get("provider_id") == provider_id:
            return row
    raise ValueError(f"Unknown provider ID: {provider_id}")


def _load_provider_pages(
    provider: dict[str, object],
    input_dir: Path | None,
    live_fetch: bool,
    raw_dir: Path,
    diagnostics: list[Diagnostic],
) -> list[dict[str, str]]:
    provider_id = str(provider["provider_id"])
    if input_dir:
        fixture_dir = input_dir / provider_id if (input_dir / provider_id).exists() else input_dir
        pages = []
        for path in sorted(fixture_dir.glob("*.html")):
            pages.append(
                {
                    "url": str(provider["homepage_url"]),
                    "fixture_path": str(path),
                    "html": path.read_text(encoding="utf-8"),
                    "fetch_status": "fixture",
                }
            )
        if not pages:
            diagnostics.append(
                _diagnostic(
                    "provider_fixture_missing",
                    f"No fixture HTML files found for {provider_id}.",
                    field="input_dir",
                    value=str(input_dir),
                )
            )
        return pages

    if not live_fetch:
        diagnostics.append(
            _diagnostic(
                "provider_input_required",
                "Provider scraping requires --input-dir or --live-fetch.",
                field="input_dir",
            )
        )
        return []

    url = str(provider["homepage_url"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    if not _robots_allows(url):
        diagnostics.append(
            _diagnostic(
                "provider_robots_disallowed",
                "Provider robots.txt does not allow the configured user agent.",
                field="homepage_url",
                value=url,
            )
        )
        return []
    text = _fetch_url(url)
    raw_path = raw_dir / provider_id / "homepage.html"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(text, encoding="utf-8")
    return [{"url": url, "html": text, "fetch_status": "fetched"}]


def _parse_provider_page(provider_id: str, page: dict[str, str]) -> dict[str, object]:
    parser = _ProviderSpeciesParser(provider_id, page["url"])
    parser.feed(page["html"])
    return {
        "provider_id": provider_id,
        "page_url": page["url"],
        "fetch_status": page["fetch_status"],
        "records": parser.records,
    }


def _build_sandbox_tables(
    provider_id: str,
    parsed_pages: list[dict[str, object]],
    diagnostics: list[Diagnostic],
) -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {
        "inventory_pages.csv": [],
        "candidate_species.csv": [],
        "candidate_attributes.csv": [],
        "supplier_availability.csv": [],
        "mowability.csv": [],
    }
    for page in parsed_pages:
        tables["inventory_pages.csv"].append(
            {
                "provider_id": provider_id,
                "page_url": str(page["page_url"]),
                "page_type": "fixture" if page["fetch_status"] == "fixture" else "homepage",
                "fetch_status": str(page["fetch_status"]),
                "review_status": ReviewStatus.PENDING.value,
            }
        )
        records = page["records"]
        if not isinstance(records, list) or not records:
            diagnostics.append(
                _diagnostic(
                    "provider_page_no_species_records",
                    "Provider page did not contain fixture species records.",
                    Severity.WARNING,
                    field="page_url",
                    value=str(page["page_url"]),
                )
            )
            continue
        for record in records:
            if not isinstance(record, dict):
                continue
            _append_species_tables(tables, provider_id, str(page["page_url"]), record)
    tables["diagnostics.csv"] = [
        diagnostic.to_dict() for diagnostic in diagnostics if diagnostic.severity != Severity.ERROR
    ]
    return tables


def _append_species_tables(
    tables: dict[str, list[dict[str, str]]],
    provider_id: str,
    fallback_url: str,
    record: dict[str, str],
) -> None:
    botanical_name = record.get("botanical_name", "")
    source_url = record.get("source_url") or fallback_url
    category = record.get("product_category", "")
    eligibility = _vancouver_eligibility(provider_id, record)
    candidate_status = "excluded" if eligibility in {"excluded", "ineligible"} else "candidate"
    tables["candidate_species.csv"].append(
        {
            "provider_id": provider_id,
            "botanical_name": botanical_name,
            "common_name": record.get("common_name", ""),
            "candidate_status": candidate_status,
            "vancouver_eligibility_status": eligibility,
            "source_url": source_url,
            "review_status": ReviewStatus.PENDING.value,
            "product_category": category,
            "candidate_reason": _candidate_reason(provider_id, eligibility, record),
            "notes": record.get("notes", ""),
        }
    )
    for attribute_name, attribute_value in _attribute_records(record):
        tables["candidate_attributes.csv"].append(
            {
                "provider_id": provider_id,
                "botanical_name": botanical_name,
                "attribute_name": attribute_name,
                "attribute_value": attribute_value,
                "evidence_confidence": "Pending review",
                "source_url": source_url,
                "review_status": ReviewStatus.PENDING.value,
            }
        )
    tables["supplier_availability.csv"].append(
        {
            "provider_id": provider_id,
            "botanical_name": botanical_name,
            "supplier_status": record.get("supplier_status", "unknown"),
            "product_url": source_url,
            "review_status": ReviewStatus.PENDING.value,
        }
    )
    mowability_score = _mowability_score(record)
    if mowability_score:
        tables["mowability.csv"].append(
            {
                "provider_id": provider_id,
                "botanical_name": botanical_name,
                "mowability_score": mowability_score,
                "source_url": source_url,
                "review_status": ReviewStatus.PENDING.value,
                "notes": "Provisional provider observation; not a score-ready input.",
            }
        )


def _attribute_records(record: dict[str, str]) -> list[tuple[str, str]]:
    attributes: list[tuple[str, str]] = []
    for key, value in record.items():
        if key.startswith("attribute_") and value:
            attributes.append((key.removeprefix("attribute_").replace("_", " "), value))
    return attributes


def _vancouver_eligibility(provider_id: str, record: dict[str, str]) -> str:
    category = record.get("product_category", "").casefold()
    if provider_id == "PROV-WCS" and "vegetable" in category:
        return "excluded"
    if provider_id == "PROV-NWM":
        return "needs_northward_review"
    return record.get("vancouver_eligibility_status") or "candidate"


def _candidate_reason(provider_id: str, eligibility: str, record: dict[str, str]) -> str:
    if eligibility == "excluded":
        return "Excluded by provider-specific P16 guardrail."
    if provider_id == "PROV-NWM":
        return "Requires Vancouver/BC suitability review before eligibility."
    if record.get("candidate_reason"):
        return record["candidate_reason"]
    return "Provider observation for review sandbox."


def _mowability_score(record: dict[str, str]) -> str:
    explicit = record.get("mowability_score", "").strip()
    if explicit:
        return explicit
    text = " ".join(
        record.get(key, "")
        for key in ("notes", "attribute_habit", "attribute_use", "product_category")
    ).casefold()
    if "eco-lawn" in text or "lawn replacement" in text or "mowable" in text:
        return "4"
    if "establishment mowing" in text or "high cut" in text:
        return "3"
    return ""


def _sandbox_paths(output_dir: Path) -> dict[str, str]:
    return {
        "manifest": str(output_dir / "manifest.json"),
        "inventory_pages": str(output_dir / "inventory_pages.csv"),
        "candidate_species": str(output_dir / "candidate_species.csv"),
        "candidate_attributes": str(output_dir / "candidate_attributes.csv"),
        "supplier_availability": str(output_dir / "supplier_availability.csv"),
        "mowability": str(output_dir / "mowability.csv"),
        "diagnostics": str(output_dir / "diagnostics.csv"),
    }


def _render_review_html(
    species_rows: list[dict[str, str]],
    attribute_rows: list[dict[str, str]],
    supplier_rows: list[dict[str, str]],
    mowability_rows: list[dict[str, str]],
) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(row.get('provider_id', ''))}</td>"
        f"<td>{html.escape(row.get('botanical_name', ''))}</td>"
        f"<td>{html.escape(row.get('common_name', ''))}</td>"
        f"<td>{html.escape(row.get('vancouver_eligibility_status', ''))}</td>"
        "<td>"
        f"{html.escape(_source_count(row, attribute_rows, supplier_rows, mowability_rows))}"
        "</td>"
        "</tr>"
        for row in species_rows
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>BC-NPPD Provider Review</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #1f2933; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #d9e2ec; padding: 0.5rem; text-align: left; }}
    th {{ background: #f0f4f8; }}
  </style>
</head>
<body>
  <h1>Provider Review Sandbox</h1>
  <p>
    Candidate provider observations for approval triage. These rows do not
    update the Vancouver PoC.
  </p>
  <table>
    <thead>
      <tr>
        <th>Provider</th><th>Botanical name</th><th>Common name</th>
        <th>Eligibility</th><th>Linked rows</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
"""


def _source_count(
    row: dict[str, str],
    attribute_rows: list[dict[str, str]],
    supplier_rows: list[dict[str, str]],
    mowability_rows: list[dict[str, str]],
) -> str:
    species = row.get("botanical_name", "")
    count = sum(1 for item in attribute_rows if item.get("botanical_name") == species)
    count += sum(1 for item in supplier_rows if item.get("botanical_name") == species)
    count += sum(1 for item in mowability_rows if item.get("botanical_name") == species)
    return str(count)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write_csv(
    path: Path,
    rows: list[dict[str, object]],
    required_fields: tuple[str, ...],
) -> None:
    fieldnames = list(required_fields)
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


def _fetch_url(url: str) -> str:
    req = request.Request(url, headers={"User-Agent": USER_AGENT})
    with request.urlopen(req, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def _robots_allows(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
    except OSError:
        return False
    return parser.can_fetch(USER_AGENT, url)


def _diagnostic(
    code: str,
    message: str,
    severity: Severity = Severity.ERROR,
    field: str | None = None,
    value: str | None = None,
) -> Diagnostic:
    return Diagnostic(code=code, message=message, severity=severity, field=field, value=value)


class _ProviderSpeciesParser(HTMLParser):
    def __init__(self, provider_id: str, page_url: str) -> None:
        super().__init__()
        self.provider_id = provider_id
        self.page_url = page_url
        self.records: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if "data-bcnppd-species" not in data:
            return
        record: dict[str, str] = {}
        for key, value in data.items():
            if key.startswith("data-"):
                field = key.removeprefix("data-").replace("-", "_")
                if field != "bcnppd_species":
                    record[field] = value.strip()
        record.setdefault("source_url", self.page_url)
        self.records.append(record)
