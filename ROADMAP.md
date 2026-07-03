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
| P5 v1.0.0a foundation record and release | #32 | `feature/p5-v1-foundation-release` | Complete |
| P6 Vancouver plant list PoC MVP | #38 | `feature/p6-vancouver-poc-list` | Complete |
| P7 Evidence hardening | #44 | `feature/p7-evidence-hardening` | Complete |
| P8 Usability layer | #50 | `feature/p8-usability-layer` | Complete |
| P9 Plant record detail interface | #56 | `feature/p9-plant-record-detail-interface` | Complete |
| P10 v0.1.0a1 GitHub alpha release | #61 | `feature/p10-v0.1.0a1-release` | Complete |
| P11 Pollinator evidence-review module | #66 | `feature/p11-pollinator-module` | Complete |
| P12 Expand Vancouver species list | #71 | `feature/p12-expand-vancouver-species-list` | Complete |
| P13 Add Matricaria discoidea | #76 | `feature/p13-add-matricaria-discoidea` | Complete |
| P14 Fill missing common names | #81 | `feature/p14-fill-common-names` | Complete |
| P15 Source provider registry and sandbox contracts | #86 | `feature/p15-source-provider-registry` | Complete |
| P16 Provider scraping sandbox MVP | #91 | `feature/p16-provider-scraping-sandbox` | Complete |
| P17 Approved provider data integration | #97 | `feature/p17-provider-approval-integration` | Complete |
| P18 Provider data usability layer | #103 | `feature/p18-provider-usability-layer` | Complete |
| P19 Provider source sweep workflow | #109 | `feature/p19-provider-source-sweep` | Complete |
| P20 Satinflower product detail extraction | #115 | `feature/p20-satinflower-product-details` | Complete |
| P21 Downloaded provider approval runner | #118 | `feature/p21-downloaded-provider-approval-runner` | Complete |
| P22 Windows runner execution-policy shim | #123 | `feature/p22-windows-runner-shim` | Complete |
| P23 Northwest Meadowscapes source sweep | #125 | `feature/p23-nwm-source-sweep` | Complete |
| P24 West Coast Seeds source sweep | #127 | `feature/p24-west-coast-seeds-source-sweep` | Complete |
| P25 Cumulative provider approval previews | #129 | `feature/p25-cumulative-provider-approvals` | PR #130 |

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
- [x] P4.4 Docs, examples, verification, and closeout (#30)
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

Status: complete

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
- [x] P5.4 GitHub alpha release closeout (#36)
  - [x] Update roadmap and changelog with implementation state.
  - [x] Run full local acceptance.
  - [x] Open PR to `main` and record the PR number (#37).
  - [x] Comment verification on issues and close child issues only after
        checklist bodies are accurate.
  - [x] Merge only after green CI and then close the parent issue.

Phase 5 local verification passed with:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

Pull request #37 is the Phase 5 closeout PR against `main`.

Pull request #37 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #37 merged to `main` as merge commit `8c04ac9`.

## Phase 6: Vancouver Plant List PoC MVP

Parent issue: #38

Branch: `feature/p6-vancouver-poc-list`

Status: complete

Goal: produce an inspectable, public-safe, caveated Vancouver/CDF plant list PoC
from the existing 20-row workbook candidate set with stable `BCNPPD-*` IDs,
deterministic source IDs, valid source-attribution links, validation
diagnostics, and docs.

- [x] P6.1 Legacy ID migration and deterministic source registry (#39)
  - [x] Add deterministic `CDF-*` to `BCNPPD-*` ID migration helper.
  - [x] Preserve legacy IDs in PoC plant rows.
  - [x] Deduplicate workbook source names and URLs into stable `SRC-*` IDs.
  - [x] Validate generated source registry rows.
  - [x] Add focused tests.
- [x] P6.2 Vancouver PoC generator and validator APIs/CLI (#40)
  - [x] Add generator API for the Vancouver PoC plant list.
  - [x] Add validator API for generated PoC artifact directories.
  - [x] Add CLI commands for generation and validation with JSON summaries.
  - [x] Ensure hard errors are eliminated from generated PoC artifacts.
  - [x] Add CLI and validation tests.
- [x] P6.3 Tracked PoC artifacts, docs, and future P7/P8 roadmap (#41)
  - [x] Track public-safe PoC artifacts under `data/poc/vancouver`.
  - [x] Add human-readable docs page for inspecting the plant list.
  - [x] Add P7 evidence hardening and P8 usability layer to roadmap.
  - [x] Keep raw/generated/private artifacts out of git.
  - [x] Add artifact tests.
- [x] P6.4 Verification, PR, and closeout (#42)
  - [x] Update roadmap and changelog with implementation state.
  - [x] Run full local acceptance.
  - [x] Open PR to `main` and record the PR number (#43).
  - [x] Comment verification on issues and close child issues only after
        checklist bodies are accurate.
  - [x] Merge only after green CI and then close the parent issue.

Phase 6 local verification passed with:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

The tracked PoC artifact validates with:

- `bc-nppd validate-vancouver-poc-list data/poc/vancouver --json`

Pull request #43 is the Phase 6 closeout PR against `main`.

Pull request #43 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #43 merged to `main` as merge commit `f55fc1e`.

## Phase 7: Evidence Hardening

Parent issue: #44

Branch: `feature/p7-evidence-hardening`

Status: complete

Goal: review and improve evidence for the 20-species Vancouver PoC list,
promoting candidate fields to reviewed fields only where source attribution is
adequate.

- [x] P7.1 Source review and evidence-status policy (#45)
  - [x] Define P7 PoC-reviewed field boundaries.
  - [x] Treat Tier 1/2 taxonomy/native-range attribution as sufficient for
        identity/native-range display review.
  - [x] Keep Tier 3 practitioner sources as context, not reviewed score inputs.
  - [x] Preserve P6 source registry rows and add a P7 source-review layer.
- [x] P7.2 Evidence hardening generator, reports, and validator (#46)
  - [x] Add package-backed hardening generator and validator.
  - [x] Generate hardened plant list, reviewed sources, reviewed fields,
        evidence gaps, score readiness, manifest, and diagnostics.
  - [x] Add CLI commands for generation and validation.
  - [x] Validate tracked artifacts with no hard errors.
  - [x] Add focused unit and CLI tests.
- [x] P7.3 Score readiness and field-level evidence gap docs (#47)
  - [x] Record field-level gaps for horticultural, use-case, and score-related
        values.
  - [x] Mark UNI, PSI, and RVI as `not_ready` for every PoC species.
  - [x] Document that workbook suitability/toughness values are candidate
        display values, not accepted P4 score inputs.
  - [x] Add human-readable hardening docs and artifact README.
- [x] P7.4 Verification, PR, and closeout (#48)
  - [x] Update roadmap and changelog with implementation state.
  - [x] Run full local acceptance.
  - [x] Open PR to `main` and record the PR number (#49).
  - [x] Comment verification on issues and close child issues only after
        checklist bodies are accurate.
  - [x] Merge only after green CI and then close the parent issue.

Phase 7 local verification passed with:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

The tracked evidence-hardening artifact validates with:

- `bc-nppd validate-vancouver-evidence data/poc/vancouver/evidence_hardening --json`

Pull request #49 is the Phase 7 closeout PR against `main`.

Pull request #49 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #49 merged to `main` as merge commit `5c1bfeb`.

## Phase 8: Usability Layer

Parent issue: #50

Branch: `feature/p8-usability-layer`

Status: complete

Goal: add a human-friendly inspection layer for the Vancouver PoC list, with
sortable/filterable views and use-case groupings while preserving evidence
caveats.

- [x] P8.1 Static inspection table and usability artifact contract (#51)
  - [x] Define P8 public-safe artifact set and validation contract.
  - [x] Generate a static human inspection page from P7 hardening artifacts.
  - [x] Include stable species IDs, display fields, evidence status, gap counts,
        and score readiness.
  - [x] Avoid external assets, external services, and live data fetches.
  - [x] Add tests for artifact generation and validation.
- [x] P8.2 Candidate use-case views and caveat-preserving filters (#52)
  - [x] Define deterministic candidate view rules for boulevard, rain garden,
        dry sun, shade, pollinator support, and low-growing species.
  - [x] Generate view membership rows without creating final recommendations.
  - [x] Preserve P7 evidence gap and score-readiness fields in every view.
  - [x] Make deferred evidence hardening explicit for all candidate views.
  - [x] Add tests for deterministic memberships and caveats.
- [x] P8.3 CLI generator/validator, docs, and tracked public-safe artifacts (#53)
  - [x] Add package-backed usability generator and validator APIs.
  - [x] Add CLI commands for generation and validation with JSON summaries.
  - [x] Track public-safe usability artifacts under `data/poc/vancouver/usability`.
  - [x] Add Sphinx docs and artifact README for inspection.
  - [x] Keep generated build folders, raw sources, and private data ignored.
- [x] P8.4 Verification, PR, and closeout (#54)
  - [x] Update roadmap and changelog with implementation state.
  - [x] Run full local acceptance.
  - [x] Open PR to `main` and record the PR number (#55).
  - [x] Comment verification on issues and close child issues only after
        checklist bodies are accurate.
  - [x] Merge only after green CI and then close the parent issue.

Phase 8 local verification passed with:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

The tracked usability artifact validates with:

- `bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json`

Pull request #55 is the Phase 8 closeout PR against `main`.

Pull request #55 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #55 merged to `main` as merge commit `f47c612`.

## Phase 9: Plant Record Detail Interface

Parent issue: #56

Branch: `feature/p9-plant-record-detail-interface`

Status: complete

Goal: extend the static Vancouver PoC usability interface so each plant row
opens a full record detail view with all current attribute data, source
metadata, attribution rows, evidence gaps, score readiness, and caveats.

- [x] P9.1 Detail data bundle and record metadata contract (#57)
  - [x] Build embedded detail records from hardened plant rows, sources, source
        attribution, reviewed fields, evidence gaps, score readiness, and
        use-case rows.
  - [x] Preserve stable IDs, source IDs, evidence confidence, review status, and
        caveats.
  - [x] Keep detail data public-safe and dependency-free.
  - [x] Add validation checks for embedded detail records.
- [x] P9.2 Static detail panel UI and row-click behavior (#58)
  - [x] Add row click and keyboard activation to open a detail panel.
  - [x] Show all current plant attributes and metadata in structured sections.
  - [x] Include sources, attribution, reviewed fields, gaps, score readiness,
        candidate views, and caveats.
  - [x] Keep the static page self-contained with no external assets or server.
- [x] P9.3 Docs, tests, tracked artifact regeneration, and closeout (#59)
  - [x] Regenerate tracked usability artifacts.
  - [x] Update docs, README, roadmap, and changelog.
  - [x] Add tests for detail records and static HTML behavior markers.
  - [x] Run full local acceptance.
  - [x] Open PR and record the PR number (#60).
  - [x] Merge after green CI and close issues.

Phase 9 local verification passed with:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

The tracked usability artifact with embedded detail records validates with:

- `bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json`

Pull request #60 is the Phase 9 closeout PR against `main`.

Pull request #60 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #60 merged to `main` as merge commit `834cebd`.

## Phase 10: v0.1.0a1 GitHub Alpha Release

Parent issue: #61

Branch: `feature/p10-v0.1.0a1-release`

Status: complete

Goal: prepare and cut the first BC-NPPD GitHub alpha prerelease, `v0.1.0a1`,
representing the current Vancouver PoC product through Phase 9.

- [x] P10.1 Version metadata and release notes (#62)
  - [x] Bump package metadata, package `__version__`, citation version/date,
        and version assertions to `0.1.0a1`.
  - [x] Update version-bearing examples.
  - [x] Add tracked `v0.1.0a1` release notes.
  - [x] Record release scope and caveats.
- [x] P10.2 GitHub release workflow hardening (#63)
  - [x] Update release workflow permissions to allow GitHub Release creation.
  - [x] Build and twine-check dist artifacts on tag push.
  - [x] Publish a prerelease for `v*` tags and attach dist artifacts.
  - [x] Keep PyPI publishing out of scope.
- [x] P10.3 Release verification, tag, prerelease publication, and closeout (#64)
  - [x] Run full local acceptance and PoC artifact validators.
  - [x] Open release-prep PR and record the PR number (#65).
  - [x] Merge release-prep PR after green CI.
  - [x] Create and push annotated tag `v0.1.0a1` from clean `main`.
  - [x] Confirm release workflow succeeds and prerelease has wheel/sdist
        attached.
  - [x] Update roadmap/changelog/issues with release URL and close out.

Phase 10 release-prep local verification passed with:

- `python -m ruff check .`
- `python -m pytest`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- `bc-nppd validate-vancouver-poc-list data/poc/vancouver --json`
- `bc-nppd validate-vancouver-evidence data/poc/vancouver/evidence_hardening --json`
- `bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json`

Pull request #65 is the Phase 10 release-prep PR against `main`.

Pull request #65 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #65 merged to `main` as merge commit `40ed110`.

Annotated tag `v0.1.0a1` was created from clean `main` commit `7e2525d` and
pushed to origin.

Release workflow run 28560597191 passed and published the GitHub prerelease:
https://github.com/UBC-FRESH/bc-npp-database/releases/tag/v0.1.0a1

Release artifacts attached:

- `bc_npp_database-0.1.0a1-py3-none-any.whl`
- `bc_npp_database-0.1.0a1.tar.gz`

## Phase 11: Pollinator Evidence-Review Module

Parent issue: #66

Branch: `feature/p11-pollinator-module`

Status: complete

Goal: add a pollinator evidence-review module that materializes the Vancouver
PoC pollinator review queue without inventing plant-pollinator claims or
calculating PSI scores.

- [x] P11.1 Pollinator review data contract and validators (#67)
  - [x] Define pollinator review rows, evidence-gap rows, and source
        requirement rows.
  - [x] Validate species IDs, review statuses, PSI readiness, and required
        files.
  - [x] Preserve the no-invented-pollinator-claims evidence rule.
- [x] P11.2 Vancouver pollinator artifact generation and CLI (#68)
  - [x] Generate Vancouver pollinator module artifacts from the tracked
        usability layer.
  - [x] Add `bc-nppd generate-vancouver-pollinator-module`.
  - [x] Add `bc-nppd validate-vancouver-pollinator-module`.
  - [x] Track public-safe PoC pollinator module outputs.
- [x] P11.3 Docs, tests, acceptance, and closeout (#69)
  - [x] Add Sphinx and artifact README documentation.
  - [x] Add unit and CLI tests.
  - [x] Run local acceptance.
  - [x] Open PR and record the PR number (#70).
  - [x] Merge PR after green CI.

Phase 11 local verification passed with:

- `python -m ruff check .`
- `python -m pytest` (83 passed)
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- `bc-nppd validate-vancouver-pollinator-module data/poc/vancouver/pollinator_module --json`

Pull request #70 is the Phase 11 closeout PR against `main`.

Pull request #70 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #70 merged to `main` as merge commit `fd57abf`.

## Phase 12: Expand Vancouver Species List

Parent issue: #71

Branch: `feature/p12-expand-vancouver-species-list`

Status: complete

Goal: add the user-submitted species list to the Vancouver PoC artifacts unless
species are already present, preserving evidence boundaries and avoiding
invented ecological claims.

- [x] P12.1 Submitted species deduplication and audit record (#72)
  - [x] Parse submitted species names and provided common names.
  - [x] Match against existing PoC species and normalized duplicate request
        lines.
  - [x] Track `requested_species_additions.csv` with disposition and assigned
        IDs.
- [x] P12.2 Vancouver PoC artifact expansion and downstream regeneration (#73)
  - [x] Add new species as unreviewed `poc_candidate` rows.
  - [x] Add source and source-attribution traceability rows without treating
        the request as ecological evidence.
  - [x] Regenerate P7 evidence hardening, P8 usability, and P11 pollinator
        artifacts.
  - [x] Preserve `not_ready` score and PSI boundaries.
- [x] P12.3 Docs, tests, verification, and closeout (#74)
  - [x] Update docs and README counts.
  - [x] Update unit and CLI tests.
  - [x] Run local acceptance and artifact validators.
  - [x] Open PR and record the PR number (#75).
  - [x] Merge PR after green CI.

Phase 12 local verification passed with:

- `python -m ruff check .`
- `python -m pytest` (83 passed)
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- `bc-nppd validate-vancouver-poc-list data/poc/vancouver --json`
- `bc-nppd validate-vancouver-evidence data/poc/vancouver/evidence_hardening --json`
- `bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json`
- `bc-nppd validate-vancouver-pollinator-module data/poc/vancouver/pollinator_module --json`

Pull request #75 is the Phase 12 closeout PR against `main`.

Pull request #75 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #75 merged to `main` as merge commit `ab91eca`.

## Phase 13: Add Matricaria discoidea

Parent issue: #76

Branch: `feature/p13-add-matricaria-discoidea`

Status: complete

Goal: add `Matricaria discoidea` to the Vancouver PoC artifacts as an
unreviewed user-requested expansion candidate, preserving evidence boundaries
and regenerating downstream artifacts.

- [x] P13.1 Add Matricaria discoidea candidate and audit row (#77)
  - [x] Add the species as an unreviewed candidate if absent.
  - [x] Preserve common/family/trait fields as blank or pending until sourced.
  - [x] Add request audit disposition and source attribution traceability.
- [x] P13.2 Regenerate downstream Vancouver artifacts (#78)
  - [x] Regenerate P7 evidence hardening.
  - [x] Regenerate P8 usability web app artifacts.
  - [x] Regenerate P11 pollinator module artifacts.
  - [x] Preserve `not_ready` score and PSI boundaries.
- [x] P13.3 Validation, PR, and closeout (#79)
  - [x] Update tests and docs/counts.
  - [x] Run local acceptance.
  - [x] Open PR and record the PR number (#80).
  - [x] Merge PR after green CI.
  - [x] Close issues after merge.

Phase 13 local verification passed with:

- `python -m ruff check .`
- `python -m pytest` (83 passed)
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- `bc-nppd validate-vancouver-poc-list data/poc/vancouver --json`
- `bc-nppd validate-vancouver-evidence data/poc/vancouver/evidence_hardening --json`
- `bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json`
- `bc-nppd validate-vancouver-pollinator-module data/poc/vancouver/pollinator_module --json`

Pull request #80 is the Phase 13 closeout PR against `main`.

Pull request #80 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #80 merged to `main` as merge commit `1971827`.

## Phase 14: Fill Missing Common Names

Parent issue: #81

Branch: `feature/p14-fill-common-names`

Status: complete

Goal: fill blank common-name fields in the tracked Vancouver PoC product with
source-attributed, pending-review common names while preserving the distinction
between display labels and reviewed ecological evidence.

- [x] P14.1 Common-name source attribution rows (#82)
  - [x] Inventory blank common-name fields in `plant_list.csv`.
  - [x] Add deterministic `SRC-*` source records for common-name support.
  - [x] Add `Common Name` attribution rows with `Pending review` confidence.
  - [x] Keep trait, pollinator, suitability, and score evidence unchanged.
- [x] P14.2 Regenerate Vancouver artifacts and web app (#83)
  - [x] Fill common names in the tracked Vancouver PoC list.
  - [x] Regenerate P7 evidence hardening artifacts.
  - [x] Regenerate P8 usability web app artifacts.
  - [x] Regenerate P11 pollinator module artifacts.
- [x] P14.3 Validation, PR, and closeout (#84)
  - [x] Update tests for new source and attribution counts.
  - [x] Run local acceptance.
  - [x] Open PR and record the PR number (#85).
  - [x] Merge PR after green CI.
  - [x] Close issues after merge.

Phase 14 local verification passed with:

- `python -m ruff check .`
- `python -m pytest` (83 passed)
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- `bc-nppd validate-vancouver-poc-list data/poc/vancouver --json`
- `bc-nppd validate-vancouver-evidence data/poc/vancouver/evidence_hardening --json`
- `bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json`
- `bc-nppd validate-vancouver-pollinator-module data/poc/vancouver/pollinator_module --json`

Pull request #85 is the Phase 14 closeout PR against `main`.

Pull request #85 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #85 merged to `main` as merge commit `3569a49`.

## Phase 15: Source Provider Registry And Sandbox Contracts

Parent issue: #86

Branch: `feature/p15-source-provider-registry`

Status: complete

Goal: add a tracked source-provider registry and provider sandbox validation
contracts for future supplier website scraping, without live scraping or
Vancouver PoC integration in this phase.

- [x] P15.1 Provider registry and source policy (#87)
  - [x] Add deterministic `PROV-*` records for Satinflower, Northwest
        Meadowscapes, West Coast Seeds, and Premier Pacific.
  - [x] Treat provider rows as Tier 3 commercial/practitioner sources.
  - [x] Record provider-specific scope, exclusions, and scrape policy.
  - [x] Update source-policy documentation.
- [x] P15.2 Sandbox data contracts and validators (#88)
  - [x] Add sandbox contracts for inventory pages, species observations,
        attribute observations, supplier availability, mowability, manifests,
        and diagnostics.
  - [x] Add Vancouver eligibility rules for provider observations.
  - [x] Validate WCS vegetable exclusion and NWM northward suitability review.
  - [x] Validate provisional 0-5 mowability observations.
- [x] P15.3 CLI, docs, tests, and closeout (#89)
  - [x] Add `bc-nppd validate-source-providers`.
  - [x] Add `bc-nppd validate-provider-sandbox`.
  - [x] Add docs and synthetic fixture tests.
  - [x] Run local acceptance.
  - [x] Open PR and record the PR number (#90).
  - [x] Merge PR after green CI.
  - [x] Close issues after merge.

Phase 15 local verification passed with:

- `python -m ruff check .`
- `python -m pytest` (93 passed)
- `bc-nppd validate-source-providers data/source_providers/provider_registry.csv --json`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- `bc-nppd validate-vancouver-poc-list data/poc/vancouver --json`
- `bc-nppd validate-vancouver-evidence data/poc/vancouver/evidence_hardening --json`
- `bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json`
- `bc-nppd validate-vancouver-pollinator-module data/poc/vancouver/pollinator_module --json`

Pull request #90 is the Phase 15 closeout PR against `main`.

Pull request #90 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #90 merged to `main` as merge commit `2a500f8`.

## Phase 16: Provider Scraping Sandbox MVP

Parent issue: #91

Branch: `feature/p16-provider-scraping-sandbox`

Status: complete

Goal: add live-capable but CI-fixture-backed provider adapters that scrape or
parse provider inventories into reviewable sandbox CSV and static HTML outputs.

- [x] P16.1 Provider fetch policy and adapters (#92)
  - [x] Create P16 implementation planning note.
  - [x] Add fixture-backed provider adapter interfaces.
  - [x] Keep live fetches optional and ignored-output only.
- [x] P16.2 Inventory extraction and Vancouver eligibility filtering (#93)
  - [x] Fill mowability scoring planning note.
  - [x] Normalize provider observations into P15 sandbox tables.
  - [x] Apply Vancouver eligibility guardrails.
- [x] P16.3 Sandbox CSV and static review table (#94)
  - [x] Generate review CSV bundle.
  - [x] Generate static HTML review page.
  - [x] Validate generated sandbox outputs.
- [x] P16.4 Verification, docs, and closeout (#95)
  - [x] Add docs and tests.
  - [x] Run local acceptance.
  - [x] Open PR and record the PR number (#96).
  - [x] Merge PR after green CI.
  - [x] Close issues after merge.

P16 must not update `data/poc/vancouver`. Raw provider HTML, screenshots,
downloads, and scrape caches remain ignored.

Phase 16 local verification passed with:

- `python -m ruff check .`
- `python -m pytest` (100 passed)
- `bc-nppd scrape-provider-sandbox PROV-SATIN --input-dir tests/fixtures/providers --out-dir outputs/provider_sandbox/PROV-SATIN --json`
- `bc-nppd validate-provider-sandbox outputs/provider_sandbox/PROV-SATIN --json`
- `bc-nppd build-provider-review outputs/provider_sandbox/PROV-SATIN --out-dir outputs/provider_review/PROV-SATIN --json`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- `bc-nppd validate-vancouver-poc-list data/poc/vancouver --json`
- `bc-nppd validate-vancouver-evidence data/poc/vancouver/evidence_hardening --json`
- `bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json`
- `bc-nppd validate-vancouver-pollinator-module data/poc/vancouver/pollinator_module --json`

Pull request #96 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #96 merged to `main` as merge commit `98fe0bd`.

## Phase 17: Approved Provider Data Integration

Parent issue: #97

Branch: `feature/p17-provider-approval-integration`

Status: complete

Goal: import only user-approved sandbox rows into the tracked Vancouver PoC,
preserving provider provenance, review status, supplier rows, candidate
mowability, and source-attribution boundaries.

- [x] P17.1 Approval manifest and review statuses (#98)
  - [x] Add approval manifest schema, statuses, validation API, and CLI.
  - [x] Reject malformed approval rows and excluded-source values.
  - [x] Ensure rejected/deferred/review-needed rows do not import.
- [x] P17.2 Approved species and attribute import (#99)
  - [x] Add provider approval importer.
  - [x] Assign next stable `BCNPPD-*` and `CDF-*` IDs for approved new species.
  - [x] Add source records and source-attribution rows for approved observations.
- [x] P17.3 Supplier and mowability artifacts (#100)
  - [x] Write separate provider-data supplier and mowability tables.
  - [x] Preserve candidate caveats and keep mowability score readiness blocked.
  - [x] Add docs, schema contract, example manifest, and tests.
- [x] P17.4 Regeneration, validation, and closeout (#101)
  - [x] Regenerate downstream artifacts when approvals are applied.
  - [x] Run local acceptance.
  - [x] Open PR and record the PR number (#102).
  - [x] Merge PR after green CI.
  - [x] Close issues after merge.

Provider-derived data remains candidate/pending review unless separately
reviewed. Mowability does not make UNI, PSI, or RVI score readiness ready.

P17 issue records were created as parent issue #97 and child issues #98 through
#101.

Phase 17 local verification passed with:

- `python -m ruff check .`
- `python -m pytest` (106 passed)
- `bc-nppd validate-provider-approvals examples/provider_approval_manifest.csv --json`
- `bc-nppd apply-provider-approvals tests/fixtures/provider_approvals/approval_manifest.csv --poc-dir data/poc/vancouver --out-dir outputs/provider_approved_vancouver --json`
- `bc-nppd validate-provider-approvals outputs/provider_approved_vancouver/provider_data --json`
- `bc-nppd validate-vancouver-poc-list outputs/provider_approved_vancouver --json`
- `bc-nppd validate-vancouver-evidence outputs/provider_approved_vancouver/evidence_hardening --json`
- `bc-nppd validate-vancouver-usability outputs/provider_approved_vancouver/usability --json`
- `bc-nppd validate-vancouver-pollinator-module outputs/provider_approved_vancouver/pollinator_module --json`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- Existing tracked Vancouver PoC, evidence, usability, and pollinator validators.

Pull request #102 passed CI for Python 3.11 and Python 3.12 before merge.

Pull request #102 merged to `main` as merge commit `c892391`.

## Phase 18: Provider Data Usability Layer

Parent issue: #103

Branch: `feature/p18-provider-usability-layer`

Status: complete

Goal: expose approved provider-derived supplier and mowability metadata in the
static Vancouver PoC interface with filters, detail-panel provenance, and
explicit caveats.

- [x] P18.1 Demo provider approval integration for user testing (#104)
  - [x] Track a caveated demo approval manifest under `data/poc/vancouver/provider_data`.
  - [x] Apply approved demo provider rows into the tracked Vancouver PoC.
  - [x] Regenerate evidence, usability, and pollinator artifacts.
- [x] P18.2 Supplier and mowability display (#105)
  - [x] Add provider summary columns to `plant_table.csv`.
  - [x] Display supplier status and provisional mowability in the web app.
  - [x] Preserve mowability as candidate data that does not make scores ready.
- [x] P18.3 Provider provenance detail panels and filters (#106)
  - [x] Embed provider data in plant detail JSON.
  - [x] Add supplier, provider-data, mowability, and provider-review filters.
  - [x] Add provider provenance detail-panel sections.
- [x] P18.4 Docs deploy hardening, validation, and closeout (#107)
  - [x] Add GitHub Pages configuration before artifact upload.
  - [x] Run local acceptance.
  - [x] Open PR and record the PR number (#108).
  - [x] Merge PR after green CI.
  - [x] Close issues after merge.

P18 issue records were created as parent issue #103 and child issues #104
through #107.

Pull request #108 is the Phase 18 closeout PR against `main`.
It passed CI for Python 3.11 and Python 3.12 and merged to `main` as merge
commit `6280631`.
Post-merge `main` CI and Docs/Pages deploy also passed on closeout commit
`89393e4`.

Phase 18 local verification passed with:

- `python -m ruff check .`
- `python -m pytest` (106 passed)
- `bc-nppd validate-provider-approvals data/poc/vancouver/provider_data --json`
- `bc-nppd validate-vancouver-poc-list data/poc/vancouver --json`
- `bc-nppd validate-vancouver-evidence data/poc/vancouver/evidence_hardening --json`
- `bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json`
- `bc-nppd validate-vancouver-pollinator-module data/poc/vancouver/pollinator_module --json`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

## Phase 19: Provider Source Sweep Workflow

Parent issue: #109

Branch: `feature/p19-provider-source-sweep`

Status: complete

Goal: run targeted provider catalogue sweeps into ignored sandbox/review
outputs so the team can inspect the full candidate catch before approving any
provider-derived data.

- [x] P19.1 Targeted provider catalogue sweep CLI (#110)
  - [x] Add `--source-sweep` mode to provider sandbox generation.
  - [x] Add `--catalog-url` for provider-specific catalogue or collection entrypoints.
  - [x] Preserve raw fetched catalogue JSON only under ignored `local/provider_raw`.
- [x] P19.2 Satinflower seed review sandbox run (#111)
  - [x] Run Satinflower from `https://satinflower.ca/collections/seed`.
  - [x] Generate ignored sandbox outputs under `outputs/provider_sandbox_source_sweep/PROV-SATIN`.
  - [x] Generate ignored review outputs under `outputs/provider_review_source_sweep/PROV-SATIN`.
  - [x] Record catch counts: 115 candidate species, 345 attribute rows, 115 supplier rows, 0 mowability rows.
- [x] P19.3 FreshForge template, docs, validation, and closeout (#112)
  - [x] Add a dependency-free FreshForge workflow shape for provider source sweeps.
  - [x] Document the Satinflower seed sweep workflow in user-facing docs.
  - [x] Run focused Ruff, provider tests, and Sphinx docs verification.
  - [x] Open PR and record the PR number (#114).
  - [x] Merge after green CI and close issues.
- [x] P19.4 Expert provider review and approval interface (#113)
  - [x] Add a static approval-review app builder and CLI command.
  - [x] Generate `review_items.csv` and a valid `approval_manifest_draft.csv`.
  - [x] Add species-first filters, detail panel, decisions, and CSV download/copy.
  - [x] Document the review/export/validate/apply workflow.

P19 issue records were created as parent issue #109 and child issues #110
through #113.

Pull request #114 is the Phase 19 closeout PR against `main`.
It passed CI for Python 3.11 and Python 3.12 and merged to `main` as merge
commit `949c5e5`.

Phase 19 focused verification passed with:

- `python -m ruff check .`
- `python -m pytest` (110 passed)
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- `bc-nppd build-provider-approval-review outputs/provider_sandbox_source_sweep/PROV-SATIN --poc-dir data/poc/vancouver --out-dir outputs/provider_approval_review/PROV-SATIN --reviewer "expert reviewer" --json`
- `bc-nppd validate-provider-approvals outputs/provider_approval_review/PROV-SATIN/approval_manifest_draft.csv --json`

P19.4 adds a static expert approval review app generated with:

```bash
bc-nppd build-provider-approval-review outputs/provider_sandbox_source_sweep/PROV-SATIN \
  --poc-dir data/poc/vancouver \
  --out-dir outputs/provider_approval_review/PROV-SATIN \
  --reviewer "expert reviewer" \
  --json
```

The live Satinflower seed sweep was run with:

```bash
bc-nppd scrape-provider-sandbox PROV-SATIN \
  --database-instance vancouver \
  --live-fetch \
  --source-sweep \
  --catalog-url https://satinflower.ca/collections/seed \
  --max-pages 5 \
  --raw-dir local/provider_raw \
  --out-dir outputs/provider_sandbox_source_sweep/PROV-SATIN \
  --json
bc-nppd validate-provider-sandbox outputs/provider_sandbox_source_sweep/PROV-SATIN --json
bc-nppd build-provider-review outputs/provider_sandbox_source_sweep/PROV-SATIN \
  --out-dir outputs/provider_review_source_sweep/PROV-SATIN \
  --json
```

## Phase 20: Satinflower Product Detail Extraction

Parent issue: #115

Branch: `feature/p20-satinflower-product-details`

Status: complete

Goal: extract Satinflower product-page `Plant Details` and `Seed Details`
content into provider sandbox attributes so expert reviewers see the full
product evidence, not only title/type/tag metadata.

- [x] P20.1 Product body details into review attributes (#116)
  - [x] Parse Shopify `body_html` description text.
  - [x] Parse `Plant Details` table rows into candidate attributes.
  - [x] Parse `Seed Details` table rows into candidate attributes.
  - [x] Regenerate ignored Satinflower sandbox and approval-review outputs.
  - [x] Run full acceptance and open PR (#117).
  - [x] Merge after green CI and close issues.

P20 issue records were created as parent issue #115 and child issue #116.

Pull request #117 is the Phase 20 closeout PR against `main`.
It passed CI for Python 3.11 and Python 3.12 and merged to `main` as merge
commit `f334a08`.

The regenerated Satinflower seed sweep now produces 115 candidate species,
2,086 candidate attribute rows, 115 supplier rows, and 0 mowability rows. The
approval-review draft contains 2,316 rows and validates cleanly.

Phase 20 local verification passed with:

- `python -m ruff check .`
- `python -m pytest` (110 passed)
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- `bc-nppd scrape-provider-sandbox PROV-SATIN --database-instance vancouver --live-fetch --source-sweep --catalog-url https://satinflower.ca/collections/seed --max-pages 5 --raw-dir local/provider_raw --out-dir outputs/provider_sandbox_source_sweep/PROV-SATIN --json`
- `bc-nppd validate-provider-sandbox outputs/provider_sandbox_source_sweep/PROV-SATIN --json`
- `bc-nppd build-provider-approval-review outputs/provider_sandbox_source_sweep/PROV-SATIN --poc-dir data/poc/vancouver --out-dir outputs/provider_approval_review/PROV-SATIN --reviewer "expert reviewer" --json`
- `bc-nppd validate-provider-approvals outputs/provider_approval_review/PROV-SATIN/approval_manifest_draft.csv --json`

## Phase 21: Downloaded Provider Approval Runner

Parent issue: #118

Branch: `feature/p21-downloaded-provider-approval-runner`

Status: complete

Goal: provide a Liz-friendly downstream workflow after an expert downloads
`approval_manifest.csv` from the static provider review app, while preserving
the auditable validation/apply/preview boundary.

- [x] P21.1 FreshForge approval-apply workflow template (#119)
  - [x] Add dependency-free workflow shape for downloaded approval manifests.
  - [x] Validate/apply into ignored preview outputs.
  - [x] Include downstream preview validators and run summary node.
- [x] P21.2 Liz-friendly PowerShell runner (#120)
  - [x] Add `scripts/apply-downloaded-provider-approval.ps1`.
  - [x] Default to `$HOME/Downloads/approval_manifest.csv`.
  - [x] Print plain-language preview output paths.
- [x] P21.3 Docs, tests, and closeout (#121)
  - [x] Document the simple runner path and manual fallback.
  - [x] Add static tests for the workflow template, script, and docs.
  - [x] Roll approval-review batch controls and success-pattern notes into P21.
  - [x] Run focused verification and smoke test.
  - [x] Open PR (#122).
  - [x] Merge after green CI and close issues.

Pull request #122 passed CI for Python 3.11 and Python 3.12 and merged to
`main` as merge commit `8921828`.

P21 smoke verification used the downloaded manifest at
`C:/Users/now25/Downloads/approval_manifest.csv` and generated an ignored
preview under `outputs/provider_approved_vancouver`.

Smoke-test counts:

- 2,316 approved manifest rows.
- 152 preview plant-list rows.
- 149 preview source rows.
- 2,404 preview source-attribution rows.
- 115 supplier availability rows.
- 0 mowability rows.

P21 local verification passed with:

- `python -m ruff check .`
- `python -m pytest` (113 passed)
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\apply-downloaded-provider-approval.ps1`

## Phase 22: Windows Runner Execution-Policy Shim

Parent issue: #123

Branch: `feature/p22-windows-runner-shim`

Status: complete

Goal: make the downloaded provider approval runner work on Windows systems that
block direct PowerShell script execution.

- [x] Add `scripts/apply-downloaded-provider-approval.cmd`.
- [x] Forward all arguments to the PowerShell runner with `-ExecutionPolicy Bypass`.
- [x] Update docs to recommend the `.cmd` command first.
- [x] Run focused verification and `.cmd` smoke test.
- [x] Open PR (#124).
- [x] Merge after green CI and close issue.

Pull request #124 passed CI for Python 3.11 and Python 3.12 and merged to
`main` as merge commit `905d9b3`.

P22 smoke verification ran:

- `.\scripts\apply-downloaded-provider-approval.cmd`

The wrapper applied 2,316 approved rows into the ignored preview, produced 152
plant rows and 115 supplier rows, and all preview validators passed.

## Phase 23: Northwest Meadowscapes Source Sweep

Parent issue: #125

Branch: `feature/p23-nwm-source-sweep`

Status: complete

Goal: deploy the provider source-sweep and approval-review workflow on
Northwest Meadowscapes while preserving the required Vancouver/BC suitability
review boundary.

- [x] Add NWM title parsing for `Common Name Seeds (Botanical name)` products.
- [x] Skip NWM products without botanical parentheticals.
- [x] Deduplicate candidate species while preserving multiple supplier rows.
- [x] Preserve `needs_northward_review` on all NWM candidate species.
- [x] Generate ignored NWM sandbox, review, and approval-review outputs.
- [x] Validate NWM sandbox and approval draft.
- [x] Run full acceptance.
- [x] Open PR (#126).
- [x] Merge after green CI and close issue.

Pull request #126 passed CI for Python 3.11 and Python 3.12 and merged to
`main` as merge commit `048f213`.

P23 NWM source-sweep command:

- `bc-nppd scrape-provider-sandbox PROV-NWM --database-instance vancouver --live-fetch --source-sweep --catalog-url https://northwestmeadowscapes.com --max-pages 5 --raw-dir local/provider_raw --out-dir outputs/provider_sandbox_source_sweep/PROV-NWM --json`

P23 generated ignored outputs:

- `outputs/provider_sandbox_source_sweep/PROV-NWM`
- `outputs/provider_review_source_sweep/PROV-NWM`
- `outputs/provider_approval_review/PROV-NWM`

P23 current catch counts:

- 203 unique candidate species.
- 447 candidate attribute rows.
- 208 supplier availability rows.
- 0 mowability rows.
- 203 species flagged `needs_northward_review`.
- 19 existing Vancouver PoC matches.
- 184 new candidate species.
- 858 draft approval rows.

## Phase 24: West Coast Seeds Source Sweep

Parent issue: #127

Branch: `feature/p24-west-coast-seeds-source-sweep`

Status: complete

Goal: deploy the provider source-sweep and approval-review workflow on West
Coast Seeds while preserving strict review gates for commercial seed mixes,
vegetables, non-native wildflower components, and lawn material.

- [x] Add WCS source-sweep parsing for body-derived single-species products.
- [x] Add WCS blend-ingredient parsing from product descriptions.
- [x] Default WCS source sweeps to the `wildflower-seeds` and `lawn-solutions`
      Shopify collection feeds instead of the site-wide product feed.
- [x] Mark WCS candidates as `needs_review` rather than eligible by default.
- [x] Preserve WCS blend ingredients as `mix_component` supplier rows.
- [x] Generate ignored WCS sandbox, review, and approval-review outputs.
- [x] Validate WCS sandbox and approval draft.
- [x] Run full acceptance.
- [x] Open PR (#128).
- [x] Merge after green CI and close issue.

P24 local acceptance passed:

- `python -m ruff check .`
- `python -m pytest` (`117 passed`)
- `bc-nppd validate-provider-sandbox outputs/provider_sandbox_source_sweep/PROV-WCS --json`
- `bc-nppd validate-provider-approvals outputs/provider_approval_review/PROV-WCS/approval_manifest_draft.csv --json`
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

Pull request #128 passed CI for Python 3.11 and Python 3.12 and merged to
`main` as merge commit `69e39fa`.

P24 WCS source-sweep command:

- `bc-nppd scrape-provider-sandbox PROV-WCS --database-instance vancouver --live-fetch --source-sweep --max-pages 3 --raw-dir local/provider_raw --out-dir outputs/provider_sandbox_source_sweep/PROV-WCS --json`

P24 generated ignored outputs:

- `outputs/provider_sandbox_source_sweep/PROV-WCS`
- `outputs/provider_review_source_sweep/PROV-WCS`
- `outputs/provider_approval_review/PROV-WCS`

P24 current catch counts:

- 55 unique candidate species.
- 360 candidate attribute rows.
- 72 supplier availability rows.
- 0 mowability rows.
- 55 species flagged `needs_review`.
- 68 supplier rows flagged `mix_component`.
- 1 existing Vancouver PoC match.
- 54 new candidate species.
- 487 draft approval rows.

## Phase 25: Cumulative Provider Approval Previews

Parent issue: #129

Branch: `feature/p25-cumulative-provider-approvals`

Status: PR #130

Goal: fix provider approval previews so successive approved manifests can be
applied cumulatively, and prevent downloaded manifests from being copied into
the wrong provider scratch path.

Problem diagnosed: the P21 runner applied a single downloaded manifest to the
tracked `data/poc/vancouver` base every time. Earlier provider approval imports
that existed only in ignored `outputs/provider_approved_vancouver` were
therefore overwritten by the next provider preview. The runner also defaulted
`ProviderId` to `PROV-SATIN`, so a WCS approval manifest could be copied to the
Satinflower scratch path.

- [x] Infer provider ID from approval manifests before selecting scratch paths.
- [x] Add `bc-nppd apply-provider-approval-sequence` for cumulative preview
      builds from multiple approved manifests.
- [x] Preserve existing preview `provider_data` when applying a later manifest
      to a previous preview base.
- [x] Update the PowerShell runner to use the sequence command and provider
      inference.
- [x] Update docs and FreshForge workflow shape with cumulative-preview rules.
- [x] Add regression tests for provider-data carry-forward and cumulative
      sequence application.
- [x] Run full acceptance.
- [x] Open PR (#130).
- [ ] Merge after green CI and close issue.

P25 local acceptance passed:

- `python -m ruff check .`
- `python -m pytest` (`120 passed`)
- `sphinx-build -b html docs _build/html -W`
- `python -m build`
- `twine check dist/*`

P25 smoke test:

- `scripts/apply-downloaded-provider-approval.cmd -ManifestPath C:\Users\now25\Downloads\approval_manifest.csv -SkipRegeneration`
- The runner inferred `PROV-WCS`, copied the manifest to
  `outputs/provider_approval_review/PROV-WCS/approval_manifest.csv`, and
  applied the one available WCS manifest into the ignored preview.

Important product rule: a preview is cumulative only when all reviewed
manifests are supplied to the sequence command, or when previous approvals have
already been promoted into the tracked `data/poc/vancouver` base.
