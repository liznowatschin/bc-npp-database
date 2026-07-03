"""Static expert review app for provider sandbox approval manifests."""

# ruff: noqa: E501

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from .diagnostics import Diagnostic, Severity
from .provider_approvals import APPROVAL_FIELDS, validate_provider_approvals
from .providers import validate_provider_sandbox

REVIEW_ITEM_FIELDS = (
    "provider_id",
    "botanical_name",
    "common_name",
    "species_id",
    "existing_status",
    "default_target_action",
    "default_approval_status",
    "taxonomy_flag",
    "source_review_flag",
    "attribute_count",
    "supplier_count",
    "mowability_count",
    "supplier_statuses",
    "source_url",
    "review_notes",
)


@dataclass(frozen=True)
class ProviderApprovalReviewResult:
    """Generated provider approval review app summary."""

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


def build_provider_approval_review(
    sandbox_dir: Path,
    poc_dir: Path,
    output_dir: Path,
    *,
    reviewer: str = "",
) -> ProviderApprovalReviewResult:
    """Build a static expert approval-review app from provider sandbox outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    sandbox_validation = validate_provider_sandbox(sandbox_dir)
    diagnostics: list[Diagnostic] = list(sandbox_validation.diagnostics)

    species_rows = _read_csv(sandbox_dir / "candidate_species.csv")
    attribute_rows = _read_csv(sandbox_dir / "candidate_attributes.csv")
    supplier_rows = _read_csv(sandbox_dir / "supplier_availability.csv")
    mowability_rows = _read_csv(sandbox_dir / "mowability.csv")
    plant_rows = _read_csv(poc_dir / "plant_list.csv")

    groups = _group_review_records(species_rows, attribute_rows, supplier_rows, mowability_rows)
    existing_by_name = {
        row.get("Botanical Name", "").casefold(): row for row in plant_rows if row.get("Botanical Name")
    }
    review_items = [_review_item(group, existing_by_name) for group in groups]
    approval_rows = _draft_approval_rows(groups, existing_by_name, reviewer=reviewer)

    paths = {
        "index": str(output_dir / "index.html"),
        "review_items": str(output_dir / "review_items.csv"),
        "approval_manifest_draft": str(output_dir / "approval_manifest_draft.csv"),
        "manifest": str(output_dir / "manifest.json"),
        "diagnostics": str(output_dir / "diagnostics.csv"),
    }
    _write_csv(output_dir / "review_items.csv", review_items, REVIEW_ITEM_FIELDS)
    _write_csv(output_dir / "approval_manifest_draft.csv", approval_rows, APPROVAL_FIELDS)
    manifest = {
        "artifact_name": "Provider Approval Review App",
        "input_sandbox_dir": str(sandbox_dir),
        "poc_dir": str(poc_dir),
        "review_item_count": len(review_items),
        "approval_manifest_draft_count": len(approval_rows),
        "existing_species_match_count": sum(
            1 for item in review_items if item["existing_status"] == "existing"
        ),
        "new_species_candidate_count": sum(
            1 for item in review_items if item["existing_status"] == "new"
        ),
        "reviewer": reviewer,
        "public_hygiene": {
            "raw_provider_html_tracked": False,
            "external_assets_required": False,
            "private_data_tracked": False,
        },
        "caveat": (
            "This local static review app creates approval manifests for expert "
            "review. It does not update the Vancouver PoC by itself."
        ),
    }
    _write_json(output_dir / "manifest.json", manifest)
    _write_csv(
        output_dir / "diagnostics.csv",
        [diagnostic.to_dict() for diagnostic in diagnostics]
        or [
            {
                "severity": Severity.INFO.value,
                "code": "provider_approval_review_generated",
                "message": "Provider approval review app generated.",
            }
        ],
        ("severity", "code", "message", "row_number", "field", "value"),
    )
    validation = validate_provider_approvals(output_dir / "approval_manifest_draft.csv")
    diagnostics.extend(validation.diagnostics)
    Path(paths["index"]).write_text(
        _render_review_app(review_items, approval_rows, manifest),
        encoding="utf-8",
    )
    return ProviderApprovalReviewResult(
        path=str(output_dir),
        counts={
            "review_items": len(review_items),
            "approval_manifest_draft": len(approval_rows),
            "existing_species_matches": manifest["existing_species_match_count"],
            "new_species_candidates": manifest["new_species_candidate_count"],
        },
        diagnostics=tuple(diagnostics),
        paths=paths,
    )


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...] | list[Diagnostic]) -> bool:
    """Return whether diagnostics include an error."""
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


def _group_review_records(
    species_rows: list[dict[str, str]],
    attribute_rows: list[dict[str, str]],
    supplier_rows: list[dict[str, str]],
    mowability_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for row in species_rows:
        name = row.get("botanical_name", "").strip()
        if not name:
            continue
        key = name.casefold()
        groups.setdefault(
            key,
            {
                "species": row,
                "attributes": [],
                "suppliers": [],
                "mowability": [],
            },
        )
    for table_name, rows, group_key in (
        ("candidate_attributes.csv", attribute_rows, "attributes"),
        ("supplier_availability.csv", supplier_rows, "suppliers"),
        ("mowability.csv", mowability_rows, "mowability"),
    ):
        for row in rows:
            name = row.get("botanical_name", "").strip()
            if not name:
                continue
            key = name.casefold()
            groups.setdefault(
                key,
                {
                    "species": _species_stub(row),
                    "attributes": [],
                    "suppliers": [],
                    "mowability": [],
                },
            )
            row = {**row, "_sandbox_table": table_name}
            groups[key][group_key].append(row)
    return [groups[key] for key in sorted(groups)]


def _species_stub(row: dict[str, str]) -> dict[str, str]:
    return {
        "provider_id": row.get("provider_id", ""),
        "botanical_name": row.get("botanical_name", ""),
        "common_name": row.get("common_name", ""),
        "source_url": row.get("source_url", "") or row.get("product_url", ""),
        "vancouver_eligibility_status": "needs_review",
    }


def _review_item(
    group: dict[str, Any],
    existing_by_name: dict[str, dict[str, str]],
) -> dict[str, str]:
    species = group["species"]
    name = species.get("botanical_name", "")
    existing = existing_by_name.get(name.casefold())
    source_url = species.get("source_url", "")
    taxonomy_flag = _taxonomy_flag(name, existing)
    source_review_flag = "yes" if not source_url else "no"
    default_status = "needs_taxonomy_review" if taxonomy_flag == "yes" else "deferred"
    if source_review_flag == "yes":
        default_status = "needs_source_review"
    supplier_statuses = sorted(
        {row.get("supplier_status", "") for row in group["suppliers"] if row.get("supplier_status")}
    )
    return {
        "provider_id": species.get("provider_id", ""),
        "botanical_name": name,
        "common_name": species.get("common_name", ""),
        "species_id": existing.get("Species ID", "") if existing else "",
        "existing_status": "existing" if existing else "new",
        "default_target_action": "update_existing" if existing else "add_species",
        "default_approval_status": default_status,
        "taxonomy_flag": taxonomy_flag,
        "source_review_flag": source_review_flag,
        "attribute_count": str(len(group["attributes"])),
        "supplier_count": str(len(group["suppliers"])),
        "mowability_count": str(len(group["mowability"])),
        "supplier_statuses": ";".join(supplier_statuses),
        "source_url": source_url,
        "review_notes": _default_review_notes(taxonomy_flag, source_review_flag),
    }


def _draft_approval_rows(
    groups: list[dict[str, Any]],
    existing_by_name: dict[str, dict[str, str]],
    *,
    reviewer: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    review_date = date.today().isoformat()
    for group in groups:
        species = group["species"]
        name = species.get("botanical_name", "")
        existing = existing_by_name.get(name.casefold())
        species_id = existing.get("Species ID", "") if existing else ""
        target_action = "update_existing" if existing else "add_species"
        default_status = "needs_taxonomy_review" if _taxonomy_flag(name, existing) == "yes" else "deferred"
        rows.append(
            _approval_row(
                len(rows) + 1,
                species,
                "candidate_species.csv",
                default_status,
                target_action,
                species_id,
                reviewer,
                review_date,
                "Draft species-level decision; export from the static app after expert review.",
            )
        )
        for supplier in group["suppliers"]:
            rows.append(
                _approval_row(
                    len(rows) + 1,
                    supplier,
                    "supplier_availability.csv",
                    "deferred",
                    "record_supplier" if existing else "add_species",
                    species_id,
                    reviewer,
                    review_date,
                    "Draft supplier row; approve only with the species decision.",
                )
            )
        for attribute in group["attributes"]:
            rows.append(
                _approval_row(
                    len(rows) + 1,
                    attribute,
                    "candidate_attributes.csv",
                    "deferred",
                    target_action,
                    species_id,
                    reviewer,
                    review_date,
                    "Attribute rows default to deferred pending row-level review.",
                )
            )
        for mowability in group["mowability"]:
            rows.append(
                _approval_row(
                    len(rows) + 1,
                    mowability,
                    "mowability.csv",
                    "deferred",
                    "record_mowability" if existing else "add_species",
                    species_id,
                    reviewer,
                    review_date,
                    "Mowability rows default to deferred because this score is provisional.",
                )
            )
    return rows


def _approval_row(
    index: int,
    row: dict[str, str],
    sandbox_table: str,
    status: str,
    target_action: str,
    species_id: str,
    reviewer: str,
    review_date: str,
    notes: str,
) -> dict[str, str]:
    return {
        "approval_id": f"PA-DRAFT-{index:04d}",
        "sandbox_table": sandbox_table,
        "provider_id": row.get("provider_id", ""),
        "botanical_name": row.get("botanical_name", ""),
        "common_name": row.get("common_name", ""),
        "species_id": species_id,
        "approval_status": status,
        "target_action": target_action,
        "attribute_name": row.get("attribute_name", ""),
        "attribute_value": row.get("attribute_value", ""),
        "evidence_confidence": row.get("evidence_confidence", "") or "Pending review",
        "source_url": row.get("source_url", "") or row.get("product_url", ""),
        "supplier_status": row.get("supplier_status", ""),
        "product_url": row.get("product_url", "") or row.get("source_url", ""),
        "mowability_score": row.get("mowability_score", ""),
        "reviewer": reviewer,
        "review_date": review_date,
        "review_notes": notes,
    }


def _taxonomy_flag(botanical_name: str, existing: dict[str, str] | None) -> str:
    name = botanical_name.casefold()
    if existing:
        return "no"
    if re.search(r"\b(ssp|subsp|var|x)\b", name):
        return "yes"
    if len(botanical_name.split()) > 2:
        return "yes"
    return "no"


def _default_review_notes(taxonomy_flag: str, source_review_flag: str) -> str:
    notes = []
    if taxonomy_flag == "yes":
        notes.append("Taxonomy review recommended before approval.")
    if source_review_flag == "yes":
        notes.append("Source URL review required before approval.")
    return " ".join(notes)


def _render_review_app(
    review_items: list[dict[str, str]],
    approval_rows: list[dict[str, str]],
    manifest: dict[str, Any],
) -> str:
    payload = json.dumps(
        {
            "reviewItems": review_items,
            "approvalRows": approval_rows,
            "manifest": manifest,
            "approvalFields": list(APPROVAL_FIELDS),
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BC-NPPD Provider Approval Review</title>
  <style>
    :root {{ color-scheme: light; --ink: #17212b; --muted: #5b6774; --line: #d7dee8; --soft: #f5f7fa; --accent: #146c72; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font: 14px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: #fff; }}
    header {{ padding: 18px 22px; border-bottom: 1px solid var(--line); background: #f8fafc; }}
    h1 {{ margin: 0 0 4px; font-size: 22px; }}
    h2 {{ margin: 0 0 10px; font-size: 16px; }}
    button, select, input {{ font: inherit; }}
    button {{ border: 1px solid var(--line); background: #fff; border-radius: 6px; padding: 7px 10px; cursor: pointer; }}
    button.primary {{ background: var(--accent); border-color: var(--accent); color: white; }}
    a {{ color: #0f5f66; }}
    .muted {{ color: var(--muted); }}
    .shell {{ display: grid; grid-template-columns: minmax(360px, 44%) 1fr; min-height: calc(100vh - 82px); }}
    .left, .right {{ padding: 16px; overflow: auto; }}
    .left {{ border-right: 1px solid var(--line); }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 12px; }}
    .toolbar input[type="search"] {{ flex: 1 1 220px; padding: 8px; border: 1px solid var(--line); border-radius: 6px; }}
    .filters {{ display: flex; flex-wrap: wrap; gap: 8px 12px; margin-bottom: 12px; color: var(--muted); }}
    .card {{ width: 100%; text-align: left; margin: 0 0 8px; padding: 10px; border: 1px solid var(--line); border-radius: 6px; background: #fff; }}
    .card.active {{ border-color: var(--accent); box-shadow: inset 3px 0 0 var(--accent); }}
    .card-title {{ display: flex; justify-content: space-between; gap: 10px; font-weight: 700; }}
    .badges {{ display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }}
    .badge {{ border: 1px solid var(--line); border-radius: 999px; padding: 2px 7px; color: var(--muted); background: var(--soft); font-size: 12px; }}
    .detail-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 14px; }}
    .panel {{ border: 1px solid var(--line); border-radius: 6px; padding: 12px; background: #fff; }}
    .panel.full {{ grid-column: 1 / -1; }}
    label.stack {{ display: grid; gap: 4px; margin-bottom: 10px; }}
    select, input[type="text"], textarea {{ width: 100%; border: 1px solid var(--line); border-radius: 6px; padding: 8px; background: #fff; }}
    textarea {{ min-height: 72px; resize: vertical; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 8px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 6px; text-align: left; vertical-align: top; }}
    th {{ background: var(--soft); }}
    pre {{ white-space: pre-wrap; max-height: 240px; overflow: auto; background: #111827; color: #f9fafb; padding: 10px; border-radius: 6px; }}
    @media (max-width: 900px) {{ .shell {{ grid-template-columns: 1fr; }} .left {{ border-right: 0; border-bottom: 1px solid var(--line); }} }}
  </style>
</head>
<body>
  <header>
    <h1>Provider Approval Review</h1>
    <div class="muted">Species-first expert review for provider sandbox observations. Exported approval manifests must be validated before import.</div>
  </header>
  <main class="shell">
    <section class="left">
      <div class="toolbar">
        <input id="search" type="search" placeholder="Search botanical or common name">
        <button id="sort-name">A-Z</button>
      </div>
      <div class="filters">
        <label><input type="checkbox" id="filter-existing"> Existing PoC</label>
        <label><input type="checkbox" id="filter-new"> New candidates</label>
        <label><input type="checkbox" id="filter-taxonomy"> Taxonomy review</label>
        <label><input type="checkbox" id="filter-source"> Source review</label>
        <label><input type="checkbox" id="filter-unavailable"> Unavailable supplier</label>
      </div>
      <div id="summary" class="muted"></div>
      <div id="list"></div>
    </section>
    <section class="right">
      <div id="detail"></div>
      <section class="panel full">
        <h2>Export Approval Manifest</h2>
        <p class="muted">The app does not write to disk. Download or copy the CSV, then validate it with <code>bc-nppd validate-provider-approvals</code>.</p>
        <div class="toolbar">
          <button class="primary" id="download">Download approval_manifest.csv</button>
          <button id="copy">Copy CSV</button>
        </div>
        <pre id="csv-preview"></pre>
      </section>
    </section>
  </main>
  <script id="payload" type="application/json">{payload}</script>
  <script>
    const payload = JSON.parse(document.getElementById('payload').textContent);
    const state = new Map(payload.reviewItems.map(item => [item.botanical_name, {{
      status: item.default_approval_status,
      target: item.default_target_action,
      includeAttributes: false,
      includeSupplier: true,
      includeMowability: false,
      notes: item.review_notes || ''
    }}]));
    let activeName = payload.reviewItems[0]?.botanical_name || '';
    const bySpecies = new Map();
    for (const row of payload.approvalRows) {{
      const list = bySpecies.get(row.botanical_name) || [];
      list.push(row);
      bySpecies.set(row.botanical_name, list);
    }}

    function filteredItems() {{
      const q = document.getElementById('search').value.trim().toLowerCase();
      return payload.reviewItems.filter(item => {{
        if (q && !(`${{item.botanical_name}} ${{item.common_name}}`.toLowerCase().includes(q))) return false;
        if (document.getElementById('filter-existing').checked && item.existing_status !== 'existing') return false;
        if (document.getElementById('filter-new').checked && item.existing_status !== 'new') return false;
        if (document.getElementById('filter-taxonomy').checked && item.taxonomy_flag !== 'yes') return false;
        if (document.getElementById('filter-source').checked && item.source_review_flag !== 'yes') return false;
        if (document.getElementById('filter-unavailable').checked && !item.supplier_statuses.includes('unavailable')) return false;
        return true;
      }}).sort((a, b) => a.botanical_name.localeCompare(b.botanical_name));
    }}

    function renderList() {{
      const items = filteredItems();
      document.getElementById('summary').textContent = `${{items.length}} visible of ${{payload.reviewItems.length}} species candidates`;
      document.getElementById('list').innerHTML = items.map(item => `
        <button class="card ${{item.botanical_name === activeName ? 'active' : ''}}" data-name="${{escapeAttr(item.botanical_name)}}">
          <div class="card-title"><span>${{escapeHtml(item.botanical_name)}}</span><span>${{escapeHtml(state.get(item.botanical_name).status)}}</span></div>
          <div class="muted">${{escapeHtml(item.common_name || '')}}</div>
          <div class="badges">
            <span class="badge">${{item.existing_status}}</span>
            <span class="badge">${{item.supplier_count}} supplier</span>
            <span class="badge">${{item.attribute_count}} attributes</span>
            ${{item.taxonomy_flag === 'yes' ? '<span class="badge">taxonomy review</span>' : ''}}
          </div>
        </button>`).join('');
      document.querySelectorAll('.card').forEach(button => button.addEventListener('click', () => {{
        activeName = button.dataset.name;
        render();
      }}));
    }}

    function renderDetail() {{
      const item = payload.reviewItems.find(candidate => candidate.botanical_name === activeName) || payload.reviewItems[0];
      if (!item) {{
        document.getElementById('detail').innerHTML = '<section class="panel"><h2>No rows</h2></section>';
        return;
      }}
      const decision = state.get(item.botanical_name);
      const rows = bySpecies.get(item.botanical_name) || [];
      const attrs = rows.filter(row => row.sandbox_table === 'candidate_attributes.csv');
      const suppliers = rows.filter(row => row.sandbox_table === 'supplier_availability.csv');
      const mowability = rows.filter(row => row.sandbox_table === 'mowability.csv');
      document.getElementById('detail').innerHTML = `
        <section class="panel full">
          <h2>${{escapeHtml(item.botanical_name)}}</h2>
          <p class="muted">${{escapeHtml(item.common_name || '')}}</p>
          <div class="detail-grid">
            <div><strong>PoC match</strong><br>${{escapeHtml(item.existing_status)}} ${{item.species_id ? '(' + escapeHtml(item.species_id) + ')' : ''}}</div>
            <div><strong>Provider</strong><br>${{escapeHtml(item.provider_id)}}</div>
            <div><strong>Taxonomy flag</strong><br>${{escapeHtml(item.taxonomy_flag)}}</div>
            <div><strong>Supplier status</strong><br>${{escapeHtml(item.supplier_statuses || 'none')}}</div>
          </div>
          <p><a href="${{escapeAttr(item.source_url)}}" target="_blank" rel="noopener">Provider source</a></p>
        </section>
        <section class="panel">
          <h2>Decision</h2>
          <label class="stack">Approval status
            <select id="decision-status">
              ${{['approved','rejected','deferred','needs_source_review','needs_taxonomy_review'].map(value => `<option value="${{value}}" ${{decision.status === value ? 'selected' : ''}}>${{value}}</option>`).join('')}}
            </select>
          </label>
          <label class="stack">Target action
            <select id="decision-target">
              ${{['update_existing','add_species','record_supplier','record_mowability'].map(value => `<option value="${{value}}" ${{decision.target === value ? 'selected' : ''}}>${{value}}</option>`).join('')}}
            </select>
          </label>
          <label><input type="checkbox" id="include-supplier" ${{decision.includeSupplier ? 'checked' : ''}}> Include supplier rows when approved</label><br>
          <label><input type="checkbox" id="include-attrs" ${{decision.includeAttributes ? 'checked' : ''}}> Include attribute rows when approved</label><br>
          <label><input type="checkbox" id="include-mow" ${{decision.includeMowability ? 'checked' : ''}}> Include mowability rows when approved</label>
          <label class="stack">Reviewer notes
            <textarea id="decision-notes">${{escapeHtml(decision.notes)}}</textarea>
          </label>
        </section>
        <section class="panel">
          <h2>Linked Rows</h2>
          <p>${{attrs.length}} attributes, ${{suppliers.length}} supplier rows, ${{mowability.length}} mowability rows.</p>
          ${{tableHtml('Supplier', suppliers, ['supplier_status','product_url'])}}
          ${{tableHtml('Attributes', attrs, ['attribute_name','attribute_value'])}}
          ${{tableHtml('Mowability', mowability, ['mowability_score','source_url'])}}
        </section>`;
      bindDecision(item.botanical_name);
    }}

    function bindDecision(name) {{
      const decision = state.get(name);
      document.getElementById('decision-status').addEventListener('change', event => {{ decision.status = event.target.value; render(); }});
      document.getElementById('decision-target').addEventListener('change', event => {{ decision.target = event.target.value; updatePreview(); renderList(); }});
      document.getElementById('include-supplier').addEventListener('change', event => {{ decision.includeSupplier = event.target.checked; updatePreview(); }});
      document.getElementById('include-attrs').addEventListener('change', event => {{ decision.includeAttributes = event.target.checked; updatePreview(); }});
      document.getElementById('include-mow').addEventListener('change', event => {{ decision.includeMowability = event.target.checked; updatePreview(); }});
      document.getElementById('decision-notes').addEventListener('input', event => {{ decision.notes = event.target.value; updatePreview(); }});
    }}

    function approvalRowsForExport() {{
      return payload.approvalRows.map(row => {{
        const decision = state.get(row.botanical_name);
        const next = {{...row}};
        const isSpecies = row.sandbox_table === 'candidate_species.csv';
        const isSupplier = row.sandbox_table === 'supplier_availability.csv';
        const isAttr = row.sandbox_table === 'candidate_attributes.csv';
        const isMow = row.sandbox_table === 'mowability.csv';
        next.review_notes = decision.notes || row.review_notes;
        if (decision.status === 'approved') {{
          if (isSpecies || (isSupplier && decision.includeSupplier) || (isAttr && decision.includeAttributes) || (isMow && decision.includeMowability)) {{
            next.approval_status = 'approved';
          }} else {{
            next.approval_status = 'deferred';
          }}
        }} else {{
          next.approval_status = decision.status;
        }}
        if (isSpecies || isAttr) next.target_action = decision.target;
        if (isSupplier && !next.species_id) next.target_action = 'add_species';
        if (isMow && !next.species_id) next.target_action = 'add_species';
        return next;
      }});
    }}

    function csvText() {{
      const rows = approvalRowsForExport();
      return [payload.approvalFields.join(','), ...rows.map(row => payload.approvalFields.map(field => csvCell(row[field] || '')).join(','))].join('\\n') + '\\n';
    }}

    function updatePreview() {{
      document.getElementById('csv-preview').textContent = csvText().slice(0, 8000);
    }}

    function tableHtml(title, rows, fields) {{
      if (!rows.length) return '';
      return `<h3>${{title}}</h3><table><thead><tr>${{fields.map(field => `<th>${{field}}</th>`).join('')}}</tr></thead><tbody>${{rows.map(row => `<tr>${{fields.map(field => `<td>${{field.endsWith('url') ? linkCell(row[field]) : escapeHtml(row[field] || '')}}</td>`).join('')}}</tr>`).join('')}}</tbody></table>`;
    }}
    function linkCell(value) {{ return value ? `<a href="${{escapeAttr(value)}}" target="_blank" rel="noopener">${{escapeHtml(value)}}</a>` : ''; }}
    function csvCell(value) {{ const text = String(value); return /[",\\n]/.test(text) ? `"${{text.replaceAll('"', '""')}}"` : text; }}
    function escapeHtml(value) {{ return String(value ?? '').replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;', \"'\":'&#39;'}}[char])); }}
    function escapeAttr(value) {{ return escapeHtml(value); }}
    function render() {{ renderList(); renderDetail(); updatePreview(); }}
    document.getElementById('search').addEventListener('input', renderList);
    document.querySelectorAll('.filters input').forEach(input => input.addEventListener('change', renderList));
    document.getElementById('sort-name').addEventListener('click', renderList);
    document.getElementById('download').addEventListener('click', () => {{
      const blob = new Blob([csvText()], {{type: 'text/csv'}});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'approval_manifest.csv';
      a.click();
      URL.revokeObjectURL(url);
    }});
    document.getElementById('copy').addEventListener('click', async () => {{
      await navigator.clipboard.writeText(csvText());
    }});
    render();
  </script>
</body>
</html>
"""


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {**payload, "generated_at": datetime.now(UTC).isoformat()}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
