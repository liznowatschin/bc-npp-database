"""Static usability artifacts for the Vancouver plant list PoC."""

from __future__ import annotations

import csv
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .diagnostics import Diagnostic, Severity
from .evidence_hardening import (
    has_error_diagnostics as has_hardening_error_diagnostics,
)
from .evidence_hardening import (
    validate_vancouver_evidence_hardening,
)
from .sources import SPECIES_ID_PATTERN
from .vancouver_poc import DIAGNOSTIC_FIELDS

USABILITY_REQUIRED_FILES = (
    "index.html",
    "plant_table.csv",
    "use_case_views.csv",
    "view_summary.csv",
    "manifest.json",
    "diagnostics.csv",
)

PLANT_TABLE_FIELDS = (
    "Species ID",
    "Botanical Name",
    "Common Name",
    "Family",
    "Native Status",
    "Life Cycle",
    "Sun",
    "Soil Moisture",
    "Urban Toughness",
    "reviewed_field_count",
    "gap_count",
    "score_readiness",
    "Primary References",
    "candidate_views",
    "poc_caveat",
)

USE_CASE_FIELDS = (
    "use_case",
    "species_id",
    "botanical_name",
    "common_name",
    "candidate_status",
    "candidate_reason",
    "evidence_caveat",
    "gap_count",
    "score_readiness",
)

VIEW_SUMMARY_FIELDS = (
    "use_case",
    "label",
    "candidate_count",
    "status",
    "rule_summary",
    "caveat",
)

USE_CASE_ORDER = (
    "boulevard",
    "rain_garden",
    "dry_sun",
    "shade",
    "pollinator_support",
    "low_growing",
)

USE_CASE_LABELS = {
    "boulevard": "Boulevard",
    "rain_garden": "Rain Garden",
    "dry_sun": "Dry Sun",
    "shade": "Shade",
    "pollinator_support": "Pollinator Review",
    "low_growing": "Low Growing",
}

USABILITY_CAVEAT = (
    "P8 usability views are candidate inspection aids. They preserve P7 evidence "
    "gaps and score-readiness blocks and are not final planting recommendations."
)


@dataclass(frozen=True)
class UsabilityResult:
    """Generated or validated usability artifact summary."""

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


def generate_vancouver_usability(
    hardening_dir: Path,
    output_dir: Path,
) -> UsabilityResult:
    """Generate static P8 usability artifacts from P7 hardening outputs."""
    hardening_validation = validate_vancouver_evidence_hardening(hardening_dir)
    if has_hardening_error_diagnostics(hardening_validation.diagnostics):
        return UsabilityResult(
            path=str(output_dir),
            counts=_empty_counts(),
            diagnostics=hardening_validation.diagnostics,
            paths={},
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    hardened_rows = _load_csv(hardening_dir / "hardened_plant_list.csv", [])
    view_rows = _build_use_case_rows(hardened_rows)
    view_summary_rows = _build_view_summary(view_rows)
    table_rows = _build_table_rows(hardened_rows, view_rows)
    diagnostics = (
        Diagnostic(
            code="usability_candidate_view_caveat",
            message=USABILITY_CAVEAT,
            severity=Severity.WARNING,
            context={"species_count": len(table_rows)},
        ),
    )

    paths = _paths(output_dir)
    _write_csv(Path(paths["plant_table"]), table_rows, PLANT_TABLE_FIELDS)
    _write_csv(Path(paths["use_case_views"]), view_rows, USE_CASE_FIELDS)
    _write_csv(Path(paths["view_summary"]), view_summary_rows, VIEW_SUMMARY_FIELDS)
    _write_csv(Path(paths["diagnostics"]), [d.to_dict() for d in diagnostics], DIAGNOSTIC_FIELDS)
    _write_json(
        Path(paths["manifest"]),
        {
            "artifact_name": "Vancouver Usability Layer",
            "input_hardening_dir": str(hardening_dir),
            "status": "p8_static_usability_poc",
            "plant_count": len(table_rows),
            "use_case_membership_count": len(view_rows),
            "view_count": len(view_summary_rows),
            "public_hygiene": {
                "raw_sources_tracked": False,
                "external_downloads_required": False,
                "private_data_tracked": False,
                "external_assets_required": False,
            },
            "caveat": USABILITY_CAVEAT,
        },
    )
    Path(paths["index"]).write_text(
        _render_html(table_rows, view_summary_rows),
        encoding="utf-8",
    )
    return validate_vancouver_usability(output_dir)


def validate_vancouver_usability(path: Path) -> UsabilityResult:
    """Validate generated P8 Vancouver usability artifacts."""
    diagnostics: list[Diagnostic] = []
    counts = _empty_counts()
    for filename in USABILITY_REQUIRED_FILES:
        if not (path / filename).exists():
            diagnostics.append(_diagnostic("missing_usability_file", field="path", value=filename))
    if diagnostics:
        return UsabilityResult(str(path), counts, tuple(diagnostics), {})

    table_rows = _load_csv(path / "plant_table.csv", diagnostics)
    view_rows = _load_csv(path / "use_case_views.csv", diagnostics)
    summary_rows = _load_csv(path / "view_summary.csv", diagnostics)
    diagnostic_rows = _load_csv(path / "diagnostics.csv", diagnostics)
    manifest = _load_json(path / "manifest.json", diagnostics)
    html_text = _load_text(path / "index.html", diagnostics)

    counts.update(
        {
            "plant_table": len(table_rows),
            "use_case_views": len(view_rows),
            "view_summary": len(summary_rows),
        }
    )
    species_ids = {row.get("Species ID", "") for row in table_rows}
    diagnostics.extend(_validate_table_rows(table_rows))
    diagnostics.extend(_validate_view_rows(view_rows, species_ids))
    diagnostics.extend(_validate_summary_rows(summary_rows))
    diagnostics.extend(_validate_manifest(manifest, counts))
    diagnostics.extend(_validate_html(html_text, counts))
    diagnostics.extend(_validate_diagnostic_rows(diagnostic_rows))

    return UsabilityResult(str(path), counts, tuple(diagnostics), _paths(path))


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...]) -> bool:
    """Return whether diagnostics contain at least one error."""
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


def _build_table_rows(
    hardened_rows: list[dict[str, str]],
    view_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    views_by_species: dict[str, list[str]] = {}
    for row in view_rows:
        if row.get("candidate_status") == "candidate":
            views_by_species.setdefault(row.get("species_id", ""), []).append(row["use_case"])

    table_rows: list[dict[str, str]] = []
    for row in hardened_rows:
        species_id = row.get("Species ID", "")
        table_rows.append(
            {
                field: row.get(field, "")
                for field in PLANT_TABLE_FIELDS
                if field not in {"candidate_views"}
            }
            | {
                "candidate_views": ";".join(
                    USE_CASE_LABELS[view]
                    for view in USE_CASE_ORDER
                    if view in views_by_species.get(species_id, [])
                )
            }
        )
    return table_rows


def _build_use_case_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    view_rows: list[dict[str, str]] = []
    for row in rows:
        matches = _candidate_use_cases(row)
        for use_case in USE_CASE_ORDER:
            if use_case in matches:
                view_rows.append(_view_row(row, use_case, "candidate", matches[use_case]))
            elif use_case == "pollinator_support":
                view_rows.append(
                    _view_row(
                        row,
                        use_case,
                        "review_queue",
                        (
                            "Native PoC species should receive pollinator evidence review; "
                            "this is not a PSI score."
                        ),
                    )
                )
    return view_rows


def _candidate_use_cases(row: dict[str, str]) -> dict[str, str]:
    sun = row.get("Sun", "").casefold()
    moisture = row.get("Soil Moisture", "").casefold()
    toughness = _as_int(row.get("Urban Toughness", ""))
    matches: dict[str, str] = {}
    if toughness is not None and toughness >= 4 and "sun" in sun:
        matches["boulevard"] = (
            "Candidate because urban toughness is at least 4 and sun exposure includes sun."
        )
    if any(token in moisture for token in ("moist", "wet", "winter wet", "vernal")):
        matches["rain_garden"] = (
            "Candidate because soil moisture text includes moist, wet, or seasonal wetness."
        )
    if "sun" in sun and "dry" in moisture:
        matches["dry_sun"] = (
            "Candidate because sun exposure includes sun and soil moisture includes dry."
        )
    if "shade" in sun:
        matches["shade"] = "Candidate because sun exposure includes shade."
    return matches


def _view_row(
    row: dict[str, str],
    use_case: str,
    status: str,
    reason: str,
) -> dict[str, str]:
    return {
        "use_case": use_case,
        "species_id": row.get("Species ID", ""),
        "botanical_name": row.get("Botanical Name", ""),
        "common_name": row.get("Common Name", ""),
        "candidate_status": status,
        "candidate_reason": reason,
        "evidence_caveat": (
            "Candidate view uses P6/P7 display fields; field-level use-case "
            "evidence remains in the P7 gap report."
        ),
        "gap_count": row.get("gap_count", ""),
        "score_readiness": row.get("score_readiness", ""),
    }


def _build_view_summary(view_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    summary: list[dict[str, str]] = []
    for use_case in USE_CASE_ORDER:
        candidate_count = sum(
            1
            for row in view_rows
            if row.get("use_case") == use_case and row.get("candidate_status") == "candidate"
        )
        if use_case == "low_growing":
            status = "insufficient_data"
            rule = "No height or spread field exists in the current PoC artifact."
            caveat = "Do not infer low-growing suitability until stature data is reviewed."
        elif use_case == "pollinator_support":
            review_count = sum(1 for row in view_rows if row.get("use_case") == use_case)
            candidate_count = review_count
            status = "review_queue"
            rule = f"{review_count} native PoC species queued for pollinator evidence review."
            caveat = "Not a PSI score and not a reviewed pollinator-support ranking."
        else:
            status = "candidate_view"
            rule = _rule_summary(use_case)
            caveat = "Candidate filter based on display fields with P7 evidence gaps preserved."
        summary.append(
            {
                "use_case": use_case,
                "label": USE_CASE_LABELS[use_case],
                "candidate_count": str(candidate_count),
                "status": status,
                "rule_summary": rule,
                "caveat": caveat,
            }
        )
    return summary


def _rule_summary(use_case: str) -> str:
    return {
        "boulevard": "Urban Toughness >= 4 and sun exposure includes sun.",
        "rain_garden": "Soil moisture includes moist, wet, winter wet, or vernal wetness.",
        "dry_sun": "Sun exposure includes sun and soil moisture includes dry.",
        "shade": "Sun exposure includes shade.",
    }[use_case]


def _render_html(
    table_rows: list[dict[str, str]],
    view_summary_rows: list[dict[str, str]],
) -> str:
    buttons = "\n".join(
        f'<button type="button" data-view="{html.escape(row["use_case"])}">'
        f'{html.escape(row["label"])} <span>{html.escape(row["candidate_count"])}</span></button>'
        for row in view_summary_rows
    )
    summary_items = "\n".join(
        "<li>"
        f"<strong>{html.escape(row['label'])}</strong>: "
        f"{html.escape(row['candidate_count'])} candidates. "
        f"{html.escape(row['caveat'])}"
        "</li>"
        for row in view_summary_rows
    )
    body_rows = "\n".join(_render_table_row(row) for row in table_rows)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Vancouver Plant List PoC</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1d2522;
      --muted: #59645f;
      --line: #d7ddd9;
      --surface: #f7f9f6;
      --accent: #1f7a5a;
      --accent-2: #2f5f9f;
      --warn: #9d6b1f;
      --white: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--surface);
      line-height: 1.45;
    }}
    header, main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    header {{ border-bottom: 1px solid var(--line); }}
    h1 {{ margin: 0 0 8px; font-size: 2rem; letter-spacing: 0; }}
    h2 {{ margin: 24px 0 12px; font-size: 1.1rem; letter-spacing: 0; }}
    p {{ max-width: 880px; color: var(--muted); }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      padding: 16px 0;
    }}
    input {{
      min-width: min(100%, 320px);
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      font: inherit;
    }}
    button {{
      min-height: 38px;
      border: 1px solid var(--line);
      background: var(--white);
      color: var(--ink);
      border-radius: 6px;
      padding: 8px 10px;
      font: inherit;
      cursor: pointer;
    }}
    button.active {{ border-color: var(--accent); box-shadow: inset 0 -3px 0 var(--accent); }}
    button span {{ color: var(--muted); }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 8px;
      padding: 0;
      list-style: none;
    }}
    .summary li {{
      background: var(--white);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
    }}
    .table-wrap {{ overflow-x: auto; background: var(--white); border: 1px solid var(--line); }}
    table {{ width: 100%; border-collapse: collapse; min-width: 980px; }}
    th, td {{
      padding: 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{ background: #eef3ef; position: sticky; top: 0; z-index: 1; }}
    .status {{
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      background: #e8f2ee;
      color: var(--accent);
      white-space: nowrap;
    }}
    .not-ready {{ color: var(--warn); }}
    .views {{ color: var(--accent-2); }}
    .hidden {{ display: none; }}
  </style>
</head>
<body>
  <header>
    <h1>Vancouver Plant List PoC</h1>
    <p>{html.escape(USABILITY_CAVEAT)}</p>
  </header>
  <main>
    <section>
      <h2>Candidate Views</h2>
      <ul class="summary">
        {summary_items}
      </ul>
    </section>
    <section>
      <h2>Plant Table</h2>
      <div class="toolbar">
        <input id="search" type="search" aria-label="Search plants"
               placeholder="Search species, family, use case">
        <button type="button" data-view="all" class="active">
          All <span>{len(table_rows)}</span>
        </button>
        {buttons}
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Botanical Name</th>
              <th>Common Name</th>
              <th>Sun</th>
              <th>Moisture</th>
              <th>Views</th>
              <th>Evidence</th>
              <th>Scores</th>
            </tr>
          </thead>
          <tbody>
            {body_rows}
          </tbody>
        </table>
      </div>
    </section>
  </main>
  <script>
    const search = document.querySelector("#search");
    const buttons = [...document.querySelectorAll("button[data-view]")];
    const rows = [...document.querySelectorAll("tbody tr")];
    let activeView = "all";
    function applyFilters() {{
      const query = search.value.trim().toLowerCase();
      for (const row of rows) {{
        const matchesQuery = !query || row.textContent.toLowerCase().includes(query);
        const views = row.dataset.views.split(";");
        const matchesView = activeView === "all" || views.includes(activeView);
        row.classList.toggle("hidden", !(matchesQuery && matchesView));
      }}
    }}
    for (const button of buttons) {{
      button.addEventListener("click", () => {{
        activeView = button.dataset.view;
        buttons.forEach((candidate) => candidate.classList.toggle("active", candidate === button));
        applyFilters();
      }});
    }}
    search.addEventListener("input", applyFilters);
  </script>
</body>
</html>
"""


def _render_table_row(row: dict[str, str]) -> str:
    view_slugs = [
        slug
        for slug, label in USE_CASE_LABELS.items()
        if label in row.get("candidate_views", "").split(";")
    ]
    views = row.get("candidate_views", "") or "None"
    evidence = f"{row.get('reviewed_field_count', '0')} reviewed / {row.get('gap_count', '0')} gaps"
    return (
        f'<tr data-views="{html.escape(";".join(view_slugs))}">'
        f"<td>{html.escape(row.get('Species ID', ''))}</td>"
        f"<td><em>{html.escape(row.get('Botanical Name', ''))}</em><br>"
        f"{html.escape(row.get('Family', ''))}</td>"
        f"<td>{html.escape(row.get('Common Name', ''))}</td>"
        f"<td>{html.escape(row.get('Sun', ''))}</td>"
        f"<td>{html.escape(row.get('Soil Moisture', ''))}</td>"
        f'<td class="views">{html.escape(views)}</td>'
        f'<td><span class="status">{html.escape(evidence)}</span></td>'
        f'<td class="not-ready">{html.escape(row.get("score_readiness", ""))}</td>'
        "</tr>"
    )


def _validate_table_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        species_id = row.get("Species ID", "")
        if not SPECIES_ID_PATTERN.fullmatch(species_id):
            diagnostics.append(
                _diagnostic("invalid_species_id", row_number, "Species ID", species_id)
            )
        if row.get("score_readiness") != "not_ready":
            diagnostics.append(
                _diagnostic("invalid_score_readiness", row_number, "score_readiness")
            )
        if not row.get("poc_caveat"):
            diagnostics.append(_diagnostic("missing_poc_caveat", row_number, "poc_caveat"))
    return diagnostics


def _validate_view_rows(
    rows: list[dict[str, str]],
    species_ids: set[str],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    allowed_statuses = {"candidate", "review_queue"}
    for row_number, row in enumerate(rows, start=2):
        if row.get("use_case") not in USE_CASE_ORDER:
            diagnostics.append(_diagnostic("invalid_use_case", row_number, "use_case"))
        if row.get("species_id") not in species_ids:
            diagnostics.append(_diagnostic("unknown_species_id", row_number, "species_id"))
        if row.get("candidate_status") not in allowed_statuses:
            diagnostics.append(
                _diagnostic("invalid_candidate_status", row_number, "candidate_status")
            )
        if row.get("score_readiness") != "not_ready":
            diagnostics.append(
                _diagnostic("invalid_score_readiness", row_number, "score_readiness")
            )
        if not row.get("evidence_caveat"):
            diagnostics.append(
                _diagnostic("missing_evidence_caveat", row_number, "evidence_caveat")
            )
    return diagnostics


def _validate_summary_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    seen = {row.get("use_case") for row in rows}
    if seen != set(USE_CASE_ORDER):
        diagnostics.append(_diagnostic("missing_use_case_summary", field="use_case"))
    for row_number, row in enumerate(rows, start=2):
        if row.get("use_case") == "low_growing" and row.get("status") != "insufficient_data":
            diagnostics.append(_diagnostic("invalid_low_growing_status", row_number, "status"))
        if not row.get("caveat"):
            diagnostics.append(_diagnostic("missing_summary_caveat", row_number, "caveat"))
    return diagnostics


def _validate_manifest(manifest: dict[str, Any], counts: dict[str, int]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    expected = {
        "plant_count": counts["plant_table"],
        "use_case_membership_count": counts["use_case_views"],
        "view_count": counts["view_summary"],
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            diagnostics.append(
                _diagnostic("manifest_count_mismatch", field=key, value=str(manifest.get(key)))
            )
    hygiene = manifest.get("public_hygiene", {})
    if not isinstance(hygiene, dict):
        diagnostics.append(_diagnostic("invalid_public_hygiene", field="public_hygiene"))
    elif any(hygiene.get(key) is not False for key in hygiene):
        diagnostics.append(_diagnostic("public_hygiene_not_false", field="public_hygiene"))
    return diagnostics


def _validate_html(html_text: str, counts: dict[str, int]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if "<table" not in html_text or "data-view" not in html_text:
        diagnostics.append(_diagnostic("invalid_static_html", field="index.html"))
    if html_text.count("<tr data-views=") != counts["plant_table"]:
        diagnostics.append(_diagnostic("html_row_count_mismatch", field="index.html"))
    if "http://" in html_text or "https://" in html_text:
        diagnostics.append(_diagnostic("external_asset_reference", field="index.html"))
    return diagnostics


def _validate_diagnostic_rows(rows: list[dict[str, str]]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for row_number, row in enumerate(rows, start=2):
        if row.get("severity") == Severity.ERROR.value:
            diagnostics.append(
                _diagnostic(
                    "usability_diagnostics_contain_error",
                    row_number,
                    "severity",
                    row.get("code"),
                )
            )
    return diagnostics


def _empty_counts() -> dict[str, int]:
    return {"plant_table": 0, "use_case_views": 0, "view_summary": 0}


def _paths(path: Path) -> dict[str, str]:
    return {
        "index": str(path / "index.html"),
        "plant_table": str(path / "plant_table.csv"),
        "use_case_views": str(path / "use_case_views.csv"),
        "view_summary": str(path / "view_summary.csv"),
        "manifest": str(path / "manifest.json"),
        "diagnostics": str(path / "diagnostics.csv"),
    }


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
        diagnostics.append(
            _diagnostic("usability_csv_unreadable", field="path", value=f"{path}: {exc}")
        )
        return []


def _load_json(path: Path, diagnostics: list[Diagnostic]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        diagnostics.append(
            _diagnostic("usability_json_unreadable", field="path", value=f"{path}: {exc}")
        )
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_text(path: Path, diagnostics: list[Diagnostic]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        diagnostics.append(
            _diagnostic("usability_html_unreadable", field="path", value=f"{path}: {exc}")
        )
        return ""


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


def _as_int(value: str) -> int | None:
    try:
        return int(str(value).strip())
    except ValueError:
        return None


def _clean(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return str(value).strip()
