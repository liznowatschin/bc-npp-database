---
name: Parent phase
about: Track a UBC-FRESH roadmap phase and feature branch
title: "P?: "
labels: ["phase"]
assignees: ""
---

Roadmap phase:

Status:

Branch:

Roadmap link:

## Goal


## Scope


## Out Of Scope


## Architecture Notes


## Child Task Checklist

- [ ] P?.1
- [ ] P?.2
- [ ] P?.3
- [ ] P?.4

## Acceptance Criteria

- [ ] Roadmap tasks are complete or explicitly deferred.
- [ ] Tests and docs for the phase are complete.
- [ ] `ROADMAP.md` is updated.
- [ ] `CHANGE_LOG.md` is updated.
- [ ] Public repo hygiene has been checked.
- [ ] PR is merged back to `main`.

## Verification

```bash
python -m ruff check .
python -m pytest
sphinx-build -b html docs _build/html -W
python -m build
twine check dist/*
```

## Closeout Notes


