Release Checklist
=================

Before a release:

* Confirm `ROADMAP.md` and `CHANGE_LOG.md` reflect completed work.
* Run all local acceptance commands.
* Confirm docs build warning-clean.
* Confirm package artifacts build and pass `twine check`.
* Confirm no private data, raw source PDFs, screenshots, generated outputs, or
  local scratch files are included.
* Tag only after the release scope and artifacts are verified.

For the v1.0.0a foundation scaffold:

* Run ``bc-nppd validate-foundation data/foundation/v1.0.0a --json``.
* Confirm ``data/foundation/v1.0.0a/release_checklist.md`` is accurate.
* Confirm the dry-run workflow example does not create tags, publish releases,
  or require external downloads.
* Create tag ``v1.0.0a`` only after explicit maintainer approval.
