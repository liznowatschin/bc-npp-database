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
