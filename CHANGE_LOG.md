# Change Log

This file records the dated project narrative for BC-NPPD. Keep it synchronized
with `ROADMAP.md`, planning notes, issue comments, and pull requests.

## 2026-07-01

- Started Phase 0 bootstrap scaffold for the BC Native Plant & Pollinator
  Database.
- Adopted the canonical project identity: BC-NPPD, Python package
  `bc_npp_database`, and CLI command `bc-nppd`.
- Established UBC-FRESH-style governance, source hygiene, evidence rules,
  roadmap workflow, and verification expectations.
- Migrated public-safe seed docs, schema concepts, and workbook snapshot
  provenance from the legacy project bundles.
- Preserved the excluded-source rule for the City of Vancouver Green Rainwater
  Infrastructure Planting Guidelines PDF.
- Added GitHub issue and pull request templates so the UBC-FRESH phase/task
  workflow is easier to follow once the repository is connected to GitHub.
- Added the planned Phase 1 workbook normalization foundation roadmap.
- Installed a local Python 3.12 toolchain, created `.venv`, installed
  `.[dev]`, and completed Phase 0 local acceptance verification with Ruff,
  pytest, Sphinx, build, and twine checks passing.
- Committed and pushed the Phase 0 bootstrap branch
  `feature/p0-bootstrap-scaffold`.
- Backfilled Phase 0 GitHub issue records: parent issue #1 and child task
  issues #2 through #5.
- Created the empty `main` baseline branch, set it as the repository default,
  rebased the Phase 0 branch onto that baseline, and opened pull request #6 for
  Phase 0 closeout.
- Verified that pull request #6 passed CI for Python 3.11 and 3.12 before
  merge.
- Started Phase 1 seed archive inventory and normalization contracts under
  parent issue #7 with child issues #8 through #12.
- Extracted seed archives into ignored `local/seed/` and added public-safe
  planning notes for seed inventory, workbook normalization, source attribution,
  canonical schema direction, scoring framework direction, and v1.0.0a scope.
- Added read-only workbook inventory and validation helpers, structured
  diagnostics, seed archive inventory helpers, and CLI commands for workbook
  inspection.
- Completed Phase 1 local acceptance verification with Ruff, pytest, Sphinx,
  build, and twine checks passing.
- Opened pull request #13 for Phase 1 closeout.
- Verified that pull request #13 passed CI for Python 3.11 and 3.12 before
  merge.
- Started Phase 2 planning on `feature/p2-evidence-source-attribution` by
  documenting optional ecosystem integration hooks for FreshForge, FEMIC BC Data
  Catalogue workflows, and fresh-hectaresbc raster context search.
- Kept FreshForge, FEMIC, and fresh-hectaresbc out of core dependencies while
  recording future optional adapter and workflow-node directions.
- Added figrecover to the P2 integration planning layer as an optional
  media-derived evidence adapter with explicit review gates, provenance fields,
  and public-data hygiene boundaries.
- Inspected the ignored local `tmp/LMH77.pdf` source with PyMuPDF, confirmed it
  is born-digital and text-extractable, recorded key metadata and initial
  `Achillea millefolium`/yarrow page hits, and added an LMH77 extraction plan.
- Created Phase 2 GitHub issue records: parent issue #14 and child issues #15
  through #18.
- Began implementing the Phase 2 source/evidence model with typed source,
  attribution, materialization, and media-extraction records plus validation
  and CLI surfaces.
- Added `src/bc_npp_database/sources.py`, source record and attribution CLI
  validators, Sphinx source-attribution docs, and synthetic tests for source
  tiers, reference IDs, external IDs, completeness, excluded-source scanning,
  and review gates.
- Completed Phase 2 implementation local acceptance verification with Ruff,
  pytest, Sphinx, build, and twine checks passing.
- Opened pull request #19 for Phase 2 closeout.
- Verified that pull request #19 passed CI for Python 3.11 and 3.12 before
  merge.
- Merged pull request #19 to `main` as merge commit `b22ee57`.
- Started Phase 3 canonical data pipeline on
  `feature/p3-canonical-data-pipeline`.
- Created Phase 3 GitHub issue records: parent issue #20 and child issues #21
  through #24.
- Expanded the Phase 3 roadmap into UBC-FRESH-grade implementation subtasks for
  canonical records, workbook import, deterministic export, optional FreshForge
  workflow shape, docs, verification, and closeout.
- Added `src/bc_npp_database/canonical.py` with canonical schema helpers,
  species, lookup, bloom-calendar, import-result, and export-result records.
- Added read-only canonical workbook import for approved sheets, alias-aware
  legacy workbook headers, source-attribution validation through the P2 model,
  structured diagnostics, and deterministic CSV export.
- Added `bc-nppd import-canonical-workbook` and
  `bc-nppd export-canonical-workbook` CLI commands with JSON summaries.
- Packaged canonical schema CSVs as package data so schema-backed APIs work from
  built wheels as well as the source checkout.
- Added canonical pipeline docs, planning updates, and a planning-only
  FreshForge workflow shape without adding FreshForge as a dependency.
- Completed Phase 3 implementation local acceptance verification with Ruff,
  pytest, Sphinx, build, and twine checks passing.
- Opened pull request #25 for Phase 3 closeout.
