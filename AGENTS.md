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

This repository is in Phase 0 bootstrap. It contains:

- `README.md`: concise public overview and current status.
- `ROADMAP.md`: phase/task roadmap and issue tracker map.
- `CHANGE_LOG.md`: append-only project narrative.
- `planning/`: focused design notes and provenance records.
- `pyproject.toml`: package metadata and optional dependency groups.
- `src/bc_npp_database/`: importable package code for CLI and validation.
- `tests/`: package-backed tests for package metadata, CLI behavior, docs, and
  validation.
- `docs/`: Sphinx documentation skeleton.
- `schemas/`: seed schema and lookup CSV files.
- `data/workbooks/`: legacy workbook snapshots retained for traceability.
- `.github/workflows/`: CI, docs, and release-artifact checks.
- `tmp/`: ignored local working area for notes, experiments, and source bundles.

Do not claim that BC-NPPD already implements full workbook normalization, score
calculation, source ingestion, dashboard generation, or species research records
until those capabilities are implemented and recorded in the roadmap.

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
- Prefer structured records and parsers over ad hoc string handling.
- Keep source policy and validation behavior explicit.
- Preserve uncertainty and record assumptions.
- Keep public repo content clean of private, irrelevant, or unpublished
  references.
- Keep changes scoped to the active roadmap phase and issue.

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
