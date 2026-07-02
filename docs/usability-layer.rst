Usability Layer
===============

Phase 8 adds a static inspection layer for the Vancouver plant list PoC. It is
designed for quick human review, not final planting recommendations.

Where To Inspect
----------------

The tracked usability artifacts live in ``data/poc/vancouver/usability/``:

``index.html``
   Self-contained static table with search, candidate view filters, and
   click-to-open plant record details. It can be opened directly in a browser.

``plant_table.csv``
   Human-readable display table derived from the P7 hardening layer.

``use_case_views.csv``
   Candidate and review-queue membership rows for boulevard, rain garden, dry
   sun, shade, pollinator review, and low-growing views.

``view_summary.csv``
   Candidate counts, rule summaries, statuses, and caveats.

``manifest.json``
   Provenance, row counts, status, and public-hygiene flags.

``diagnostics.csv``
   Non-error caveats for the usability layer.

Record Detail Panel
-------------------

Click a plant row, or focus it with the keyboard and press Enter or Space, to
open the plant record detail panel. The panel shows the current identity fields,
candidate planting attributes, reviewed fields, evidence gaps, score-readiness
rows, source records, source-attribution rows, use-case memberships, and
caveats.

The detail panel is generated from tracked P6/P7/P8 artifacts embedded in the
static page as JSON. It does not call a server or load external assets.

CLI
---

Regenerate the static usability layer:

.. code-block:: shell

   bc-nppd generate-vancouver-usability data/poc/vancouver/evidence_hardening --out-dir data/poc/vancouver/usability --json

Validate the tracked artifact:

.. code-block:: shell

   bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json

Use-Case Boundaries
-------------------

The boulevard, rain garden, dry sun, and shade views are deterministic
candidate filters from current PoC display fields. They preserve P7 evidence
gaps and ``not_ready`` score readiness.

The pollinator view is a review queue, not a Pollinator Support Index score.
The low-growing view is marked ``insufficient_data`` because the current PoC
artifact does not include reviewed height or spread fields.

No P8 view should be treated as a final planting recommendation.
