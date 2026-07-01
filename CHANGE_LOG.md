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
