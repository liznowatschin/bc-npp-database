# AGENTS.md

This file is the working contract for AI coding agents in this repository.

## Project Purpose

`bc-npp-database` exists to build the BC Native Plant & Pollinator Database
(BC-NPPD): an evidence-based native plant and pollinator decision-support
database for coastal British Columbia.

The initial project scope focuses on low-growing native species suitable for
urban landscapes in Metro Vancouver, the Fraser Valley, and related coastal BC
contexts. The project should support native plant selection, pollinator garden
design, municipal and school-ground plantings, seed mix design, restoration-style
planting decisions, education, and transparent ecological data review.

The database must remain auditable. Do not turn uncertain ecological claims into
facts. Unknown values should stay `Unknown` or blank according to the data
standard until a source supports them.

## Current Repo State

This repository has completed Phase 0 bootstrap and Phase 1 seed archive
inventory and normalization contracts. Phase 2 evidence and source attribution
work is planned on `feature/p2-evidence-source-attribution` but is not complete
until the roadmap tasks, issue records, implementation, verification, PR, CI,
merge, and issue closeout all say so. The repository contains:

- `README.md`: concise public overview and current status.
- `ROADMAP.md`: phase/task roadmap and issue tracker map.
- `CHANGE_LOG.md`: append-only project narrative.
- `planning/`: focused design notes and provenance records.
- `pyproject.toml`: package metadata and optional dependency groups.
- `src/bc_npp_database/`: importable package code for CLI and validation.
- `src/bc_npp_database/workbooks.py`: read-only workbook inspection and
  validation helpers.
- `src/bc_npp_database/seed_archives.py`: seed archive inventory helpers.
- `tests/`: package-backed tests for package metadata, CLI behavior, docs, and
  validation.
- `docs/`: Sphinx documentation skeleton.
- `schemas/`: seed schema and lookup CSV files.
- `data/workbooks/`: legacy workbook snapshots retained for traceability.
- `local/seed/`: ignored local extraction area for seed archives.
- `.github/workflows/`: CI, docs, and release-artifact checks.
- `tmp/`: ignored local working area for notes, experiments, and source bundles.

Do not claim that BC-NPPD already implements full workbook normalization, score
calculation, source ingestion, dashboard generation, canonical CSV export, or
species research records until those capabilities are implemented and recorded
in the roadmap.

## Data And Source Rules

Rules:

- Keep `tmp/`, `local/`, `data/raw/`, `data/private/`, and `outputs/` ignored.
- Do not commit private project data, raw transcripts, credentials,
  machine-specific paths, generated local outputs, or unpublished source
  documents.
- Tracked examples, tests, and docs must use synthetic or public-safe fixtures.
- Track source provenance for every non-obvious ecological attribute.
- Do not invent citations, pollinator relationships, plant traits, seed biology,
  native status, suitability scores, or cultivation guidance.
- Separate evidence confidence from ecological score.
- Preserve stable species IDs even when botanical names change.
- The City of Vancouver Green Rainwater Infrastructure Planting Guidelines PDF
  is excluded and must not be used as a project source.
- Satinflower Nurseries may be used as an approved Tier 3 regional
  practitioner source when appropriate.

## Working Principles

- Read `AGENTS.md`, `ROADMAP.md`, and `CHANGE_LOG.md` before making
  project-shaping changes.
- Keep CLI commands thin wrappers over Python APIs.
- Use FreshForge as the default orchestration layer for reusable, multi-step
  UBC-FRESH workflows.
- Prefer structured records and parsers over ad hoc string handling.
- Keep source policy and validation behavior explicit.
- Preserve uncertainty and record assumptions.
- Keep public repo content clean of private, irrelevant, or unpublished
  references.
- Keep changes scoped to the active roadmap phase and issue.

## Workflow Orchestration Contract

FreshForge is the preferred UBC-FRESH workflow runner. When BC-NPPD needs a
reusable multi-step pipeline, such as provider scraping, source materialization,
workbook-to-table import, approval preview, scoring, or release dry-runs, define
the workflow as FreshForge YAML and expose BC-NPPD behavior as small domain
commands or provider nodes.

Do not build a parallel package-specific orchestration framework, sidecar
overlay engine, bespoke DAG runner, hidden state machine, or command sequencer
inside BC-NPPD when the same job should be expressed as a FreshForge workflow.
BC-NPPD may provide thin launchers for humane local use, especially on Windows,
but those launchers should invoke FreshForge workflows or stable `bc-nppd`
domain commands. They must not become independent reimplementations of
FreshForge.

Per-provider or per-task customization should live in FreshForge YAML workflow
parameters, overlays, or documented workflow inputs unless a roadmap phase
explicitly approves another format for a narrow non-workflow data contract.
Lower-level `bc-nppd` commands remain useful as debuggable primitives and
manual fallbacks, not as a reason to fork workflow orchestration across the
UBC-FRESH package ecosystem.

## Product Delivery Pattern

When a task aims to turn external source material into useful BC-NPPD product
data, use the proven sandbox-review-manifest pattern by default:

1. Start from a concrete user-facing outcome and a real input entrypoint.
2. Acquire raw source material only into ignored locations such as `local/`,
   `tmp/`, `data/raw/`, or `outputs/`.
3. Normalize observations into inspectable sandbox CSV/JSON artifacts.
4. Build or update a humane review surface before promoting observations.
5. Treat expert decisions as an exported, durable approval manifest.
6. Validate the approval manifest before applying it.
7. Apply first to ignored preview outputs unless the maintainer explicitly asks
   to update tracked product artifacts.
8. Record before/after counts, diagnostics, commands, and artifact paths in
   roadmap, changelog, issues, or planning notes.

Do not import scraped, parsed, media-derived, GIS-derived, or provider-derived
observations directly into tracked PoC data as facts. They must pass through a
review/approval boundary unless a roadmap phase explicitly defines a different
auditable gate.

For repeated expert decisions, prefer static, dependency-light review tools
with search, filters, detail panels, batch controls, CSV export/copy, and clear
caveats before introducing a server, database, or hidden state.

Provider scraping commands with `--live-fetch`, `--source-sweep`, or equivalent
website acquisition behavior require outbound network access. If one of these
commands fails under sandboxed networking with DNS, fetch, robots, empty-catalog,
or other website-access diagnostics, rerun the same documented command with
network escalation before interpreting the result as a provider/source problem.
Do not waste time searching for old ignored artifacts when the task is to
regenerate provider data; run the provider acquisition pipeline against the
current source site and then validate the generated sandbox/review/preview
artifacts.

## Planning Workflow

This repo follows the UBC-FRESH phase/task/subtask workflow:

- `ROADMAP.md` is the current plan and issue tracker map.
- One roadmap phase maps to one GitHub parent issue and one feature branch.
- One roadmap task maps to one child issue linked from the parent issue body.
- Subtasks usually stay as checklist items inside the child issue body.
- Use at most three issue levels: phase, task, implementation subtask.
- Record issue numbers beside roadmap phases and tasks once created.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, planning notes, issue bodies, and PR
  descriptions synchronized.
- Open a PR from the phase branch to `main` only after phase tasks, tests, docs,
  and closeout notes are complete or explicitly deferred.

## Strict Development Workflow

Use this workflow for active development from the first phase boundary onward:

- One active roadmap phase should generally correspond to one GitHub parent
  issue and one feature branch.
- Create or activate the GitHub parent issue before starting a roadmap phase.
- Create the feature branch from current `main` for that parent issue.
- Create child issues for roadmap tasks under the parent issue.
- Document task subtasks as checklist steps inside the child issue body unless
  they are large enough to deserve third-level implementation issues.
- Work child issues one at a time where practical, usually in roadmap order.
- Before closing a child issue, update every issue-body checklist item to
  checked, or rewrite the issue body to make superseded work explicit.
- Close each child issue only after its repo changes, documentation, issue-body
  checklist, and verification for that task are complete.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, and issue comments synchronized as task
  state changes.
- Open a PR from the phase branch back to `main` when the parent issue's child
  issues are complete or explicitly deferred.
- Close the parent issue only after the PR has merged back to `main`.
- Do not start a new active parent issue and branch until the current parent
  issue is closed unless the maintainer explicitly approves a parallel lane.

## Phase Closeout Readiness Standard

When the maintainer asks whether a roadmap phase is ready for closeout, answer
with an evidence-backed audit, not a guess or a summary of recent activity. A
phase is not ready for closeout merely because planning notes exist, a branch is
clean, or tests passed once.

Before saying a phase is ready for closeout, verify and report all of these:

- `ROADMAP.md` lists the phase as active or complete with real issue numbers,
  not `TBD` placeholders.
- The GitHub parent issue exists and each roadmap task has a child issue.
- Each child issue checklist is complete, or each deferral is explicit and
  accepted in the issue body and roadmap.
- The phase implementation exists in repo code, docs, schemas, tests, or
  planning artifacts as required by the roadmap task wording.
- Required tests and acceptance commands have passed after the final phase
  changes.
- `CHANGE_LOG.md`, planning notes, issue comments, and PR text are synchronized.
- A PR exists from the phase branch to `main`, CI is green, and any PR number is
  recorded where required.
- The parent issue is not closed until the PR is merged to `main`.

If any item is missing, say the phase is **not ready for closeout** and list the
missing items plainly. Use wording such as `planning groundwork is ready` only
when the work is genuinely planning-only, and do not call that phase closeout
readiness unless the roadmap phase itself is defined as planning-only.

## GitHub Issue Body Quality Standard

Issue bodies are part of the project specification and onboarding material.
Write them so a new lab student, external collaborator, or coding agent can
understand the task, implement it, verify it, and close it without reading the
original chat transcript.

Parent phase issues must include phase identifier, status, branch name, roadmap
links, goal, scope, out-of-scope boundaries, architecture notes, child task
checklist, acceptance criteria, verification, and closeout requirements.

Child task issues must include task identifier, parent phase issue, status,
related planning links, goal, scope, out-of-scope boundaries, subtasks,
acceptance criteria, verification commands, artifacts, risks, and completion
metadata once closed.

Use readable Markdown with real task-list syntax. Wrap branch names, file paths,
commands, and commit hashes in backticks.

## Verification

Default local checks:

```bash
python -m ruff check .
python -m pytest
sphinx-build -b html docs _build/html -W
python -m build
twine check dist/*
```

Default CI must not require private project data, commercial GIS software, local
desktop applications, credentials, or network downloads beyond package
installation.
