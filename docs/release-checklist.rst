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
