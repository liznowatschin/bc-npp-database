# Vancouver Usability Layer

This directory contains the Phase 8 static usability layer for the Vancouver
plant list proof of concept.

Open `index.html` directly in a browser to inspect the 20-species PoC list with
search and candidate use-case filters. No local server, external assets, or
external data calls are required.

## Files

- `index.html`: self-contained static inspection page.
- `plant_table.csv`: display table derived from the P7 hardening layer.
- `use_case_views.csv`: candidate and review-queue membership rows.
- `view_summary.csv`: candidate counts, rules, status, and caveats for each
  view.
- `manifest.json`: row counts, provenance, status, and public-hygiene flags.
- `diagnostics.csv`: non-error caveats for the usability layer.

## View Boundaries

The boulevard, rain garden, dry sun, and shade views are candidate filters from
current display fields. They are not final planting recommendations.

The pollinator view is a review queue, not a Pollinator Support Index score.
The low-growing view is marked `insufficient_data` because the PoC artifact does
not yet include reviewed height or spread fields.

All rows preserve evidence gaps and `not_ready` score readiness from P7.

## CLI

Regenerate:

```shell
bc-nppd generate-vancouver-usability data/poc/vancouver/evidence_hardening --out-dir data/poc/vancouver/usability --json
```

Validate:

```shell
bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json
```
