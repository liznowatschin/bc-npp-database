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
- Verified that pull request #25 passed CI for Python 3.11 and 3.12 before
  merge.
- Merged pull request #25 to `main` as merge commit `9444d91`.
- Started Phase 4 scoring framework on `feature/p4-scoring-framework`.
- Created Phase 4 GitHub issue records: parent issue #26 and child issues #27
  through #30.
- Expanded the Phase 4 roadmap into UBC-FRESH-grade implementation subtasks for
  score vocabulary, provisional weighting, reviewed score inputs, diagnostics,
  CLI/reporting, docs, verification, and closeout.
- Added `src/bc_npp_database/scoring.py` with score-family vocabulary, weight
  records, score input records, result records, run summaries, validation, and
  provisional weighted-average scoring.
- Added `bc-nppd validate-score-inputs` and `bc-nppd calculate-scores` CLI
  commands with JSON diagnostics and result summaries.
- Added scoring framework docs, data-standard updates, planning updates, and a
  planning-only FreshForge scoring workflow shape without adding FreshForge as a
  dependency.
- Completed Phase 4 implementation local acceptance verification with Ruff,
  pytest, Sphinx, build, and twine checks passing.
- Opened pull request #31 for Phase 4 closeout.
- Verified that pull request #31 passed CI for Python 3.11 and 3.12 before
  merge.
- Merged pull request #31 to `main` as merge commit `6c2f679`.
- Started Phase 5 v1.0.0a foundation record and release scaffold on
  `feature/p5-v1-foundation-release`.
- Created Phase 5 GitHub issue records: parent issue #32 and child issues #33
  through #36.
- Expanded the Phase 5 roadmap into UBC-FRESH-grade implementation subtasks for
  schema freeze, release checklist artifacts, one reviewed
  `Achillea millefolium` foundation record, docs, dry-run workflows,
  verification, and closeout.
- Added public-safe v1.0.0a foundation artifacts under
  `data/foundation/v1.0.0a/`, including a schema freeze manifest, one
  `Achillea millefolium` species record, source records, source-attribution
  rows, score-input rows, and a release checklist.
- Added `src/bc_npp_database/foundation.py` and `bc-nppd validate-foundation`
  to validate required foundation files, cross-file species/source links,
  public-hygiene flags, source-attribution records, and score-input records.
- Added foundation release docs, release-checklist updates, v1.0.0a planning
  updates, and a planning-only release dry-run workflow that does not create a
  tag or publish artifacts.
- Completed Phase 5 implementation local acceptance verification with Ruff,
  pytest, Sphinx, build, and twine checks passing.
- Opened pull request #37 for Phase 5 closeout.
- Verified that pull request #37 passed CI for Python 3.11 and 3.12 before
  merge.
- Merged pull request #37 to `main` as merge commit `8c04ac9`.
- Started Phase 6 Vancouver plant list PoC MVP on
  `feature/p6-vancouver-poc-list`.
- Created Phase 6 GitHub issue records: parent issue #38 and child issues #39
  through #42.
- Planned the shortest path to a useful PoC: convert the existing 20 workbook
  candidates into a caveated Vancouver/CDF plant list with stable `BCNPPD-*`
  IDs, deterministic `SRC-*` sources, source-attribution links, validation
  diagnostics, tracked artifacts, and docs.
- Added planned Phase 7 evidence hardening and Phase 8 usability layer roadmap
  entries so post-PoC work is explicit.
- Added `src/bc_npp_database/vancouver_poc.py` with deterministic legacy ID
  migration, source-registry generation, source-attribution repair, PoC artifact
  writing, and artifact validation.
- Added `bc-nppd generate-vancouver-poc-list` and
  `bc-nppd validate-vancouver-poc-list`.
- Added tracked Vancouver PoC artifacts under `data/poc/vancouver/`: a 20-row
  plant list, 24 source records, 41 source-attribution rows, manifest, README,
  and diagnostics.
- Added Vancouver PoC docs and tests covering ID migration, source linking,
  artifact validation, CLI generation, and tracked artifact integrity.
- Completed Phase 6 implementation local acceptance verification with Ruff,
  pytest, Sphinx, build, and twine checks passing.
- Opened pull request #43 for Phase 6 closeout.
- Verified that pull request #43 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #43 to `main` as merge commit `f55fc1e`.
- Started Phase 7 evidence hardening on `feature/p7-evidence-hardening`.
- Created Phase 7 GitHub issue records: parent issue #44 and child issues #45
  through #48.
- Expanded the Phase 7 roadmap into UBC-FRESH-grade implementation subtasks for
  source review policy, field-level evidence promotion, evidence gap reporting,
  score readiness, docs, verification, and closeout.
- Added `src/bc_npp_database/evidence_hardening.py` with P7 hardening
  generation and validation for the tracked Vancouver PoC artifacts.
- Added `bc-nppd harden-vancouver-evidence` and
  `bc-nppd validate-vancouver-evidence` CLI commands.
- Added tracked evidence-hardening artifacts under
  `data/poc/vancouver/evidence_hardening/`: hardened plant list, reviewed
  sources, reviewed fields, evidence gaps, score-readiness rows, manifest,
  README, and diagnostics.
- Kept UNI, PSI, and RVI readiness at `not_ready` for all 20 PoC species because
  workbook suitability/toughness values are candidate display values, not
  accepted P4 score inputs.
- Completed Phase 7 implementation local acceptance verification with Ruff,
  pytest, Sphinx, build, and twine checks passing.
- Opened pull request #49 for Phase 7 closeout.
- Verified that pull request #49 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #49 to `main` as merge commit `5c1bfeb`.
- Started Phase 8 usability layer on `feature/p8-usability-layer`.
- Created Phase 8 GitHub issue records: parent issue #50 and child issues #51
  through #54.
- Expanded the Phase 8 roadmap into UBC-FRESH-grade implementation subtasks for
  static inspection artifacts, caveat-preserving candidate use-case views, CLI
  generation/validation, docs, verification, and closeout.
- Added `src/bc_npp_database/usability.py` with P8 static usability generation
  and validation for the tracked Vancouver evidence-hardening artifacts.
- Added `bc-nppd generate-vancouver-usability` and
  `bc-nppd validate-vancouver-usability` CLI commands.
- Added tracked usability artifacts under `data/poc/vancouver/usability/`: a
  self-contained static HTML inspection page, plant table, use-case membership
  rows, view summary, manifest, README, and diagnostics.
- Kept P8 use-case views caveated: boulevard, rain garden, dry sun, and shade
  are candidate filters; pollinator support is a review queue; low-growing is
  marked insufficient data because height/spread fields are not reviewed yet.
- Completed Phase 8 implementation local acceptance verification with Ruff,
  pytest, Sphinx, build, and twine checks passing.
- Opened pull request #55 for Phase 8 closeout.
- Verified that pull request #55 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #55 to `main` as merge commit `f47c612`.
- Started Phase 9 plant record detail interface on
  `feature/p9-plant-record-detail-interface`.
- Created Phase 9 GitHub issue records: parent issue #56 and child issues #57
  through #59.
- Planned P9 as a static usability enhancement: each plant row should open a
  full detail view with current attributes, source metadata, attribution,
  evidence gaps, score readiness, candidate views, and caveats.
- Extended `src/bc_npp_database/usability.py` to embed per-species detail
  records in `index.html` from tracked P6/P7/P8 artifacts.
- Added row click and keyboard activation in the static PoC interface so users
  can inspect identity fields, candidate attributes, reviewed fields, evidence
  gaps, score-readiness rows, sources, attribution, use-case memberships, and
  caveats for each plant.
- Completed Phase 9 implementation local acceptance verification with Ruff,
  pytest, Sphinx, build, and twine checks passing.
- Opened pull request #60 for Phase 9 closeout.
