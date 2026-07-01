# BC Native Plant & Pollinator Database

`bc-npp-database` is the repository for the BC Native Plant & Pollinator
Database (BC-NPPD), an evidence-based native plant and pollinator
decision-support database for coastal British Columbia.

The initial scope focuses on low-growing native species suitable for urban
landscapes in Metro Vancouver, the Fraser Valley, and related coastal BC
contexts. The project is intended to support native plant selection, pollinator
garden design, municipal and school-ground plantings, seed mix design,
restoration-style planting decisions, education, and transparent ecological data
review.

## Current Status

This repository is in Phase 0 bootstrap. It provides:

- UBC-FRESH-style agent and development workflow governance.
- A small Python package using a `src/` layout.
- A minimal `bc-nppd` command-line interface.
- Initial validation helpers for source policy, species IDs, and evidence
  confidence values.
- Sphinx documentation scaffold.
- Seed schema and lookup CSV files from the BC-NPPD foundation bundle.
- Legacy workbook snapshots retained for traceability.
- CI, docs, and release-artifact workflow scaffolds.

BC-NPPD does not yet implement full workbook normalization, score calculation,
species research automation, dashboard generation, or source ingestion.

## Development Setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

Run the local checks:

```bash
python -m ruff check .
python -m pytest
sphinx-build -b html docs _build/html -W
python -m build
twine check dist/*
```

## Command Line

```bash
bc-nppd --version
bc-nppd info
bc-nppd validate-source-policy path/to/source-notes.txt
```

The CLI commands are thin wrappers over package APIs.

## Public-Repo Hygiene

Do not commit private project data, raw chat transcripts, unpublished source
documents, generated local outputs, credentials, or machine-specific paths. Keep
scratch material under ignored local paths such as `tmp/`, `local/`,
`data/raw/`, `data/private/`, or `outputs/`.

Every non-obvious ecological claim should be traceable to an approved source.
Unknown values should remain `Unknown` or blank according to the data standard
until evidence supports them.
