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

For the v0.1.0a1 GitHub alpha prerelease:

* Confirm package, citation, and tests report ``0.1.0a1``.
* Confirm ``docs/releases/v0.1.0a1.md`` accurately describes the PoC product
  and caveats.
* Confirm PoC, evidence-hardening, and usability artifact validators pass.
* Create annotated tag ``v0.1.0a1`` from clean ``main`` after the release-prep
  PR merges.
* Confirm the tag workflow creates a GitHub prerelease and attaches wheel and
  source distribution artifacts.
