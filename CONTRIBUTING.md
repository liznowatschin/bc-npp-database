# Contributing

BC-NPPD is early research infrastructure from the UBC FRESH Lab. Contributions
should keep the repository public-safe, reproducible, and aligned with the
active roadmap phase.

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

## Local Checks

```bash
python -m ruff check .
python -m pytest
sphinx-build -b html docs _build/html -W
python -m build
twine check dist/*
```

## Workflow

- Check `ROADMAP.md` before starting non-trivial work.
- Use the active phase branch and linked GitHub issues.
- Keep `CHANGE_LOG.md`, roadmap checklists, issue comments, and PR descriptions
  synchronized with completed work.
- Keep CLI commands thin wrappers over importable Python APIs.
- Use FreshForge YAML for reusable multi-step workflows. Do not create
  package-specific mini-orchestrators, custom DAG runners, sidecar overlay
  engines, or hidden command sequencers when a workflow belongs in FreshForge.
- Keep BC-NPPD focused on domain commands and data contracts; thin local
  launchers may make FreshForge workflows easier to run, but they should not
  reimplement FreshForge.
- Do not commit private data, raw transcripts, credentials, generated local
  outputs, or machine-specific paths.
- Do not invent ecological values or citations.

See `AGENTS.md` for the full agent and development workflow contract.
