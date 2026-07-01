# BC-NPPD Roadmap

This roadmap is the current project plan and issue tracker map. Keep it
synchronized with GitHub issues, planning notes, pull requests, and
`CHANGE_LOG.md`.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Bootstrap scaffold | #1 | `feature/p0-bootstrap-scaffold` | Closeout |
| P1 Workbook normalization foundation | TBD | `feature/p1-workbook-normalization` | Planned |

## Phase 0: Bootstrap Scaffold

Parent issue: #1

Branch: `feature/p0-bootstrap-scaffold`

Status: closeout

Goal: establish BC-NPPD as a public-safe, package-backed UBC-FRESH project with
strict governance, planning, docs, CI, source policy checks, and traceable
legacy artifact migration.

- [x] P0.1 Governance, public hygiene, and agent contract (#2)
  - [x] Add public governance files.
  - [x] Add roadmap and changelog with Phase 0 issue placeholders.
  - [x] Add bootstrap rationale planning note.
  - [x] Document strict issue and roadmap workflow in `AGENTS.md`.
- [x] P0.2 Python package, CLI, and minimal validation API (#3)
  - [x] Add package metadata and dependency extras.
  - [x] Add minimal package module and CLI.
  - [x] Add source policy, species ID, and evidence confidence validation.
  - [x] Add focused tests.
- [x] P0.3 Documentation, CI, Pages, and release-artifact scaffold (#4)
  - [x] Add Sphinx configuration and docs pages.
  - [x] Add CI workflow for Python 3.11 and 3.12.
  - [x] Add docs Pages workflow.
  - [x] Add release artifact workflow.
  - [x] Add tests for docs configuration import sanity.
- [ ] P0.4 Legacy artifact migration and closeout verification (#5)
  - [x] Track cleaned public-safe docs, schema seeds, and workbook snapshots.
  - [x] Keep raw PDFs, screenshots, private data, and local scratch ignored.
  - [x] Run local acceptance commands.
  - [x] Update roadmap and changelog closeout notes.
  - [x] Comment on child issues and parent issue with verification result, or
        record that GitHub issues are not created yet.
  - [x] Commit and push branch.
  - [ ] Open PR to `main`.

Phase 0 local verification passed with:

- `python -m pip install -e .[dev]`
- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

Branch push completed for `feature/p0-bootstrap-scaffold`. Pull request creation
is pending until the empty `main` baseline branch is created and set as the
repository default.

## Future Phase Candidates

Future phases should be activated only after Phase 0 closeout unless the
maintainer explicitly approves a parallel lane.

## Phase 1: Workbook Normalization Foundation

Parent issue: TBD

Branch: `feature/p1-workbook-normalization`

Status: planned

Goal: convert the latest approved workbook snapshot and schema seeds into
structured, reproducible tables with validation coverage while preserving
source uncertainty and workbook traceability.

- [ ] P1.1 Workbook inventory and normalization design (TBD)
  - [ ] Document sheet inventory for the latest tracked workbook snapshot.
  - [ ] Map workbook sheets to normalized CSV/table outputs.
  - [ ] Record field naming, ID, evidence confidence, and source attribution
        conventions.
  - [ ] Identify values that must remain `Unknown` or blank.
- [ ] P1.2 Workbook reader and CSV export prototype (TBD)
  - [ ] Add package-backed workbook reading helpers.
  - [ ] Export selected sheets into deterministic CSV outputs.
  - [ ] Keep generated outputs out of git unless explicitly approved.
  - [ ] Add tests using small synthetic workbook fixtures.
- [ ] P1.3 Expanded validation records and CLI output (TBD)
  - [ ] Replace ad hoc validation dictionaries with typed validation records.
  - [ ] Add workbook/CSV validation entry points.
  - [ ] Preserve excluded-source, duplicate-ID, and evidence-confidence checks.
  - [ ] Add CLI JSON output where useful for agents and CI.
- [ ] P1.4 Documentation and closeout (TBD)
  - [ ] Document normalization workflow and public-safe data handling.
  - [ ] Update roadmap and changelog.
  - [ ] Run local acceptance commands.
  - [ ] Comment on child issues and parent issue with verification result.
  - [ ] Commit and push branch.
  - [ ] Open PR to `main`.
