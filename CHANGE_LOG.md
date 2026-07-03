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
- Verified that pull request #60 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #60 to `main` as merge commit `834cebd`.
- Started Phase 10 `v0.1.0a1` GitHub alpha release on
  `feature/p10-v0.1.0a1-release`.
- Created Phase 10 GitHub issue records: parent issue #61 and child issues #62
  through #64.
- Bumped package, citation, examples, and version assertions from `0.1.0a0` to
  `0.1.0a1`.
- Added tracked release notes for `v0.1.0a1` covering the Vancouver PoC product,
  evidence hardening, static usability interface, plant record details, and
  caveats.
- Updated the release workflow so `v*` tags build wheel/sdist artifacts and
  publish a GitHub prerelease with `dist/*` attached.
- Completed Phase 10 release-prep local acceptance verification with Ruff,
  pytest, Sphinx, build, twine, and PoC artifact validators passing.
- Opened pull request #65 for Phase 10 release prep.
- Verified that pull request #65 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #65 to `main` as merge commit `40ed110`.
- Created and pushed annotated tag `v0.1.0a1` from clean `main` commit
  `7e2525d`.
- Verified release workflow run 28560597191 passed and published the GitHub
  prerelease with both wheel and source distribution artifacts attached:
  https://github.com/UBC-FRESH/bc-npp-database/releases/tag/v0.1.0a1
- Closed Phase 10 as complete.
- Started Phase 11 pollinator evidence-review module on
  `feature/p11-pollinator-module`.
- Created Phase 11 GitHub issue records: parent issue #66 and child issues
  #67 through #69.
- Added a pollinator module that materializes the Vancouver PoC pollinator
  review queue as explicit review rows, source requirements, and evidence gaps
  while keeping PSI `not_ready`.
- Added tracked Vancouver pollinator module artifacts under
  `data/poc/vancouver/pollinator_module/`.
- Added pollinator module docs, tests, generation CLI, and validation CLI.
- Completed Phase 11 local acceptance verification with Ruff, pytest, Sphinx,
  build, twine, and the pollinator module validator passing.
- Opened pull request #70 for Phase 11 closeout.
- Verified that pull request #70 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #70 to `main` as merge commit `fd57abf`.
- Closed Phase 11 as complete.
- Started Phase 12 Vancouver species-list expansion on
  `feature/p12-expand-vancouver-species-list`.
- Created Phase 12 GitHub issue records: parent issue #71 and child issues
  #72 through #74.
- Added 32 unreviewed user-submitted expansion candidates to the tracked
  Vancouver PoC list, increasing the current product artifact from 20 to 52
  species.
- Added `requested_species_additions.csv` to record submitted names,
  deduplication disposition, assigned IDs, and caveats.
- Added a Tier 3 traceability source and pending-review attribution rows for
  the expansion candidates without treating the request as ecological evidence.
- Regenerated the evidence-hardening, usability, and pollinator module
  artifacts for the 52-species tracked PoC.
- Completed Phase 12 local acceptance verification with Ruff, pytest, Sphinx,
  build, twine, and all Vancouver PoC artifact validators passing.
- Opened pull request #75 for Phase 12 closeout.
- Verified that pull request #75 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #75 to `main` as merge commit `ab91eca`.
- Closed Phase 12 as complete.
- Started Phase 13 `Matricaria discoidea` addition on
  `feature/p13-add-matricaria-discoidea`.
- Created Phase 13 GitHub issue records: parent issue #76 and child issues
  #77 through #79.
- Added `Matricaria discoidea` as unreviewed candidate `BCNPPD-0053`, increasing
  the tracked Vancouver PoC product from 52 to 53 species.
- Regenerated the evidence-hardening, usability, and pollinator module
  artifacts for the 53-species tracked PoC while keeping scores and PSI
  `not_ready`.
- Completed Phase 13 local acceptance verification with Ruff, pytest, Sphinx,
  build, twine, and all Vancouver PoC artifact validators passing.
- Opened pull request #80 for Phase 13 closeout.
- Verified that pull request #80 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #80 to `main` as merge commit `1971827`.
- Closed Phase 13 as complete.
- Started Phase 14 missing common-name fill on
  `feature/p14-fill-common-names`.
- Created Phase 14 GitHub issue records: parent issue #81 and child issues
  #82 through #84.
- Filled 10 blank common-name fields in the tracked Vancouver PoC list using
  pending-review common-name source support.
- Added 10 E-Flora BC source records and 10 `Common Name` source-attribution
  rows, increasing the tracked PoC source registry from 25 to 35 records and
  attribution table from 74 to 84 rows.
- Regenerated the evidence-hardening, usability, and pollinator module
  artifacts while keeping ecological evidence, scores, and PSI `not_ready`.
- Completed Phase 14 local acceptance verification with Ruff, pytest, Sphinx,
  build, twine, and all Vancouver PoC artifact validators passing.
- Opened pull request #85 for Phase 14 closeout.
- Verified that pull request #85 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #85 to `main` as merge commit `3569a49`.
- Closed Phase 14 as complete.
- Started Phase 15 source-provider registry and sandbox contracts on
  `feature/p15-source-provider-registry`.
- Created Phase 15 GitHub issue records: parent issue #86 and child issues
  #87 through #89.
- Planned Phase 16 provider scraping sandbox, Phase 17 approved provider data
  integration, and Phase 18 provider data usability as future UBC-FRESH phases.
- Added a tracked provider registry for Satinflower, Northwest Meadowscapes,
  West Coast Seeds, and Premier Pacific as Tier 3 provider sources.
- Added provider sandbox contracts and Vancouver eligibility rules for future
  candidate species observations, attribute observations, supplier rows, and
  provisional mowability observations.
- Added provider registry and sandbox validation APIs, CLI commands, docs, and
  synthetic fixture tests without adding live scraping.
- Completed Phase 15 local acceptance verification with Ruff, pytest, provider
  registry validation, Sphinx, build, twine, and all Vancouver validators
  passing.
- Opened pull request #90 for Phase 15 closeout.
- Verified that pull request #90 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #90 to `main` as merge commit `2a500f8`.
- Closed Phase 15 as complete.
- Started Phase 16 provider scraping sandbox MVP on
  `feature/p16-provider-scraping-sandbox`.
- Created Phase 16 GitHub issue records: parent issue #91 and child issues
  #92 through #95.
- Added planning notes for provisional mowability scoring and the P16 provider
  scraping sandbox implementation path before adding scraper code.
- Added fixture-backed provider sandbox generation for all four configured
  providers, with optional live-fetch plumbing that writes raw HTML only to
  ignored local storage.
- Added provider review bundle generation with static HTML and copied review
  CSVs for user approval.
- Added `bc-nppd scrape-provider-sandbox` and `bc-nppd build-provider-review`
  CLI commands.
- Added synthetic provider fixture HTML and tests for WCS vegetable exclusion,
  NWM northward review, supplier rows, and provisional mowability rows.
- Completed Phase 16 local acceptance verification with Ruff, pytest, provider
  sandbox CLI checks, Sphinx, build, twine, and all Vancouver validators
  passing.
- Opened pull request #96 for Phase 16 closeout.
- Verified that pull request #96 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #96 to `main` as merge commit `98fe0bd`.
- Closed Phase 16 as complete.
- Started Phase 17 approved provider data integration on
  `feature/p17-provider-approval-integration`.
- Created Phase 17 GitHub issue records: parent issue #97 and child issues
  #98 through #101.
- Added provider approval manifest validation and application surfaces so only
  rows marked `approved` can enter Vancouver PoC outputs.
- Added separate provider-data supplier and provisional mowability artifacts,
  keeping mowability caveated and blocked from UNI, PSI, and RVI readiness.
- Added `bc-nppd validate-provider-approvals` and
  `bc-nppd apply-provider-approvals` CLI commands.
- Added provider approval schema docs, an example approval manifest, synthetic
  approval fixtures, and P17 tests.
- Completed Phase 17 local acceptance verification with Ruff, pytest, provider
  approval CLI checks, regenerated ignored provider-approved Vancouver outputs,
  Sphinx, build, twine, and tracked Vancouver validators passing.
- Opened pull request #102 for Phase 17 closeout.
- Verified that pull request #102 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #102 to `main` as merge commit `c892391`.
- Closed Phase 17 as complete.
- Started Phase 18 provider data usability layer on
  `feature/p18-provider-usability-layer`.
- Created Phase 18 GitHub issue records: parent issue #103 and child issues
  #104 through #107.
- Applied a tracked, caveated demo provider approval manifest to the Vancouver
  PoC, increasing the current user-test product to 54 species while excluding
  the rejected vegetable demo row.
- Added tracked provider-data supplier, mowability, provider attribution,
  manifest, and diagnostics artifacts under `data/poc/vancouver/provider_data`.
- Extended the static usability web app with provider summary columns, supplier
  and mowability filters, provider-review filters, and provider provenance
  detail-panel sections.
- Hardened the Docs workflow by adding GitHub Pages configuration before
  artifact upload.
- Completed Phase 18 local acceptance verification with Ruff, pytest, provider
  approval validation, tracked Vancouver validators, Sphinx, build, and twine
  passing.
- Opened pull request #108 for Phase 18 closeout.
- Verified that pull request #108 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #108 to `main` as merge commit `6280631`.
- Verified post-merge `main` CI and Docs/Pages deploy passed on closeout commit
  `89393e4`.
- Closed Phase 18 as complete.
- Started Phase 19 provider source sweep workflow on
  `feature/p19-provider-source-sweep`.
- Created Phase 19 GitHub issue records: parent issue #109 and child issues
  #110 through #112.
- Added targeted provider source-sweep support to `bc-nppd
  scrape-provider-sandbox` with `--source-sweep` and `--catalog-url`.
- Added a dependency-free FreshForge workflow shape for provider source sweeps.
- Documented the Satinflower seed collection sweep in the provider sandbox docs.
- Ran the Satinflower seed collection sweep from
  `https://satinflower.ca/collections/seed` into ignored local/output
  directories.
- The Satinflower seed sweep caught 115 candidate species, 345 attribute rows,
  115 supplier availability rows, and 0 mowability rows for review.
- Completed focused Phase 19 verification with Ruff, provider tests, and
  Sphinx docs passing.
- Created Phase 19 child issue #113 for the expert provider review and
  approval interface.
- Added `bc-nppd build-provider-approval-review` to generate a local static
  approval app, `review_items.csv`, and a draft approval manifest from provider
  sandbox outputs.
- Added a reviewer workflow doc and extended the P19 FreshForge template with
  the approval-review node.
- Generated the Satinflower approval-review app under ignored
  `outputs/provider_approval_review/PROV-SATIN` with 115 review items and a
  575-row draft approval manifest that validates cleanly.
- Completed P19.4 verification with Ruff, 110 pytest tests, Sphinx docs, and
  provider approval-review draft validation passing.
- Verified package build and twine metadata checks for the P19 approval-review
  changes.
- Opened pull request #114 for Phase 19 closeout.
- Verified that pull request #114 passed CI for Python 3.11 and Python 3.12
  before merge.
- Merged pull request #114 to `main` as merge commit `949c5e5`.
- Closed Phase 19 as complete.
- Started Phase 20 Satinflower product detail extraction on
  `feature/p20-satinflower-product-details`.
- Created Phase 20 GitHub issue records: parent issue #115 and child issue
  #116.
- Confirmed the P19 scraper captured product title/type/tags but did not parse
  Satinflower product `Plant Details` or `Seed Details` sections.
- Added Shopify `body_html` parsing for product descriptions, `Plant Details`
  table rows, and `Seed Details` table rows.
- Regenerated ignored Satinflower source-sweep and approval-review outputs:
  115 candidate species, 2,086 candidate attribute rows, 115 supplier rows, 0
  mowability rows, and a 2,316-row draft approval manifest that validates
  cleanly.
- Opened pull request #117 for Phase 20 closeout.
