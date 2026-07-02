# BC-NPPD Roadmap

This roadmap is the current project plan and issue tracker map. Keep it
synchronized with GitHub issues, planning notes, pull requests, and
`CHANGE_LOG.md`.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Bootstrap scaffold | #1 | `feature/p0-bootstrap-scaffold` | Complete |
| P1 Seed archive inventory and normalization contracts | #7 | `feature/p1-seed-inventory-normalization` | Complete |
| P2 Evidence and source attribution model | #14 | `feature/p2-evidence-source-attribution` | Complete |
| P3 Canonical data pipeline | #20 | `feature/p3-canonical-data-pipeline` | Complete |
| P4 Scoring framework | #26 | `feature/p4-scoring-framework` | Complete |
| P5 v1.0.0a foundation record and release | #32 | `feature/p5-v1-foundation-release` | Active |

## Phase 0: Bootstrap Scaffold

Parent issue: #1

Branch: `feature/p0-bootstrap-scaffold`

Status: complete

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
- [x] P0.4 Legacy artifact migration and closeout verification (#5)
  - [x] Track cleaned public-safe docs, schema seeds, and workbook snapshots.
  - [x] Keep raw PDFs, screenshots, private data, and local scratch ignored.
  - [x] Run local acceptance commands.
  - [x] Update roadmap and changelog closeout notes.
  - [x] Comment on child issues and parent issue with verification result, or
        record that GitHub issues are not created yet.
  - [x] Commit and push branch.
  - [x] Open PR to `main` (#6).

Phase 0 local verification passed with:

- `python -m pip install -e .[dev]`
- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

Branch push completed for `feature/p0-bootstrap-scaffold`. Pull request #6 is
the Phase 0 closeout PR against `main`.

## Future Phase Candidates

Future phases should be activated only after Phase 0 closeout unless the
maintainer explicitly approves a parallel lane.

Potential post-foundation phase:

- P6 External ecosystem and media adapters: optional FreshForge, FEMIC BCDC,
  fresh-hectaresbc, and figrecover integrations for source resolution, AOI
  materialization, raster context search, media-derived evidence recovery, and
  reviewed diagnostics.

## Phase 1: Seed Archive Inventory And Normalization Contracts

Parent issue: #7

Branch: `feature/p1-seed-inventory-normalization`

Status: complete

Goal: unpack seed archives into ignored local space, document source/provenance
inventory, define workbook normalization contracts, and add package-backed
workbook inspection plus validation diagnostics without promoting unchecked raw
artifacts into the public repository.

- [x] P1.1 Seed archive unpack and inventory (#8)
  - [x] Extract seed archives to ignored `local/seed/`.
  - [x] Inventory docs, schemas, workbooks, raw PDFs/screenshots, and legacy code.
  - [x] Record tracked, ignored, deferred, and candidate derivative dispositions.
  - [x] Confirm raw source artifacts remain ignored.
- [x] P1.2 Workbook inventory and normalization contract (#9)
  - [x] Inventory latest tracked workbook snapshot.
  - [x] Map workbook sheets to intended canonical tables.
  - [x] Record naming, ID, evidence confidence, and source attribution conventions.
  - [x] Identify values that must remain `Unknown` or blank.
- [x] P1.3 Workbook reader and synthetic fixtures (#10)
  - [x] Add package-backed workbook inspection helpers.
  - [x] Add synthetic workbook fixture builders for tests.
  - [x] Avoid CI dependence on legacy workbook contents.
  - [x] Document malformed workbook behavior.
- [x] P1.4 Validation records and CLI (#11)
  - [x] Replace loose validation dictionaries with typed diagnostic records.
  - [x] Preserve excluded-source, duplicate-ID, and evidence-confidence checks.
  - [x] Add workbook validation entry points.
  - [x] Add text and JSON CLI output where useful.
- [x] P1.5 Docs, issues, and closeout (#12)
  - [x] Document normalization workflow and public-safe data handling.
  - [x] Update roadmap and changelog.
  - [x] Run local acceptance commands.
  - [x] Comment on child issues and parent issue with verification result.
  - [x] Commit and push branch.
  - [x] Open PR to `main` (#13).

Phase 1 local verification passed with:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

Pull request #13 is the Phase 1 closeout PR against `main`.

## Phase 2: Evidence And Source Attribution Model

Parent issue: #14

Branch: `feature/p2-evidence-source-attribution`

Status: complete

Goal: define durable source, evidence, reference ID, and attribution records
that support auditable ecological claims.

- [x] P2.1 Source tier and reference ID contract (#15)
- [x] P2.2 Source attribution table, materialization, media-extraction manifest,
      and validation model (#16)
- [x] P2.3 Excluded-source, source-completeness, and external-ID enforcement (#17)
- [x] P2.4 Integration-hook docs, examples, and closeout (#18)

Phase 2 local verification passed with:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

Pull request #19 is the Phase 2 closeout PR against `main`.

Pull request #19 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #19 merged to `main` as merge commit `b22ee57`.

## Phase 3: Canonical Data Pipeline

Parent issue: #20

Branch: `feature/p3-canonical-data-pipeline`

Status: complete

Goal: convert approved workbook and schema inputs into deterministic canonical
tables and import/export APIs while keeping generated outputs out of git unless
explicitly approved.

- [x] P3.1 Canonical table dataclasses and schema helpers (#21)
  - [x] Add canonical dataclasses and result containers.
  - [x] Load schema seed column definitions with stable order.
  - [x] Normalize workbook header aliases such as `Species_ID` to `Species ID`.
  - [x] Validate required canonical fields and ID conventions.
  - [x] Add focused unit tests.
- [x] P3.2 Workbook-to-table import pipeline and manifest joins (#22)
  - [x] Implement read-only workbook import for approved sheets.
  - [x] Preserve source attribution rows through P2 validators.
  - [x] Import bloom calendar rows without scoring or ecological inference.
  - [x] Emit diagnostics for malformed rows, excluded sources, and invalid
        confidence values.
  - [x] Add synthetic workbook tests.
- [x] P3.3 Deterministic CSV export and optional FreshForge workflow shape (#23)
  - [x] Export deterministic CSV tables to caller-provided output directories.
  - [x] Include diagnostics export when diagnostics are present.
  - [x] Add CLI JSON summaries for canonical import and export.
  - [x] Document optional FreshForge workflow shape without adding a dependency.
  - [x] Add export and CLI tests.
- [x] P3.4 Docs, examples, verification, and closeout (#24)
  - [x] Update Sphinx docs and planning notes.
  - [x] Update roadmap and changelog with implementation state.
  - [x] Run full local acceptance.
  - [x] Open PR to `main` and record the PR number (#25).
  - [x] Comment verification on issues and close child issues only after
        checklist bodies are accurate.

Phase 3 local verification passed with:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

Pull request #25 is the Phase 3 closeout PR against `main`.

Pull request #25 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #25 merged to `main` as merge commit `9444d91`.

## Phase 4: Scoring Framework

Parent issue: #26

Branch: `feature/p4-scoring-framework`

Status: complete

Goal: document and implement evidence-aware UNI, PSI, and RVI score framework
placeholders without inventing unsupported ecological values.

- [x] P4.1 Score vocabulary and weighting direction (#27)
  - [x] Define UNI, PSI, and RVI score-family vocabulary.
  - [x] Define provisional weight records and validation rules.
  - [x] Keep score inputs separate from evidence confidence and source
        attribution.
  - [x] Document that weights are provisional until reviewed.
  - [x] Add focused tests.
- [x] P4.2 Evidence-aware score input and calculation records (#28)
  - [x] Add score input records with species ID, metric, value, weight
        reference, evidence confidence, source ID, and review status.
  - [x] Add score result and run-summary records.
  - [x] Calculate scores only from explicit reviewed numeric inputs.
  - [x] Emit diagnostics for excluded or invalid inputs.
  - [x] Add calculation tests.
- [x] P4.3 Score diagnostics, reviewed context/media hooks, and CLI/reporting
      surfaces (#29)
  - [x] Validate source IDs, species IDs, evidence confidence, numeric ranges,
        weights, and review gates.
  - [x] Keep external context/media hooks as provenance fields only.
  - [x] Add CLI commands for score-input validation and score calculation.
  - [x] Add JSON report summaries.
  - [x] Add CLI tests.
- [ ] P4.4 Docs, examples, verification, and closeout (#30)
  - [x] Update Sphinx docs and planning notes.
  - [x] Update roadmap and changelog with implementation state.
  - [x] Run full local acceptance.
  - [x] Open PR to `main` and record the PR number (#31).
  - [x] Comment verification on issues and close child issues only after
        checklist bodies are accurate.

Phase 4 local verification passed with:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

Pull request #31 is the Phase 4 closeout PR against `main`.

Pull request #31 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #31 merged to `main` as merge commit `6c2f679`.

## Phase 5: v1.0.0a Foundation Record And Release

Parent issue: #32

Branch: `feature/p5-v1-foundation-release`

Status: active

Goal: produce a reviewed v1.0.0a foundation release with frozen schema
direction, one gold-standard `Achillea millefolium` record, docs, verification,
and GitHub release artifacts.

- [x] P5.1 Foundation schema freeze and release checklist (#33)
  - [x] Add foundation schema freeze manifest.
  - [x] Record schema, lookup, source, canonical, and scoring contracts included
        in the foundation.
  - [x] Add release checklist artifacts without tagging a release.
  - [x] Validate public hygiene and generated-output boundaries.
  - [x] Add focused tests.
- [x] P5.2 Gold-standard `Achillea millefolium` record workflow (#34)
  - [x] Add a reviewed example `Achillea millefolium` species record.
  - [x] Add source-attribution sidecar rows with reviewed source IDs and
        evidence confidence.
  - [x] Add score-input sidecar rows that exercise P4 without inventing
        unsupported values.
  - [x] Add package validators for foundation artifacts.
  - [x] Add tests that validate the foundation record and sidecars.
- [x] P5.3 Public docs, dry-run workflow examples, and integration-hook
      hardening (#35)
  - [x] Add foundation release Sphinx docs.
  - [x] Add dry-run workflow examples for canonical import, scoring, and
        release preparation.
  - [x] Clarify optional integration hooks remain deferred and dependency-free.
  - [x] Update planning notes and release checklist docs.
  - [x] Add docs tests or import sanity where useful.
- [ ] P5.4 GitHub alpha release closeout (#36)
  - [x] Update roadmap and changelog with implementation state.
  - [x] Run full local acceptance.
  - [x] Open PR to `main` and record the PR number (#37).
  - [ ] Comment verification on issues and close child issues only after
        checklist bodies are accurate.
  - [ ] Merge only after green CI and then close the parent issue.

Phase 5 local verification passed with:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

Pull request #37 is the Phase 5 closeout PR against `main`.
