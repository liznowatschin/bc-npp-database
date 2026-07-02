Pollinator Module
=================

The pollinator module turns the Phase 8 ``Pollinator Review`` queue into a
tracked evidence-review scaffold. It is designed to make missing pollinator
evidence visible without inventing plant-pollinator relationships or scores.

Tracked Artifact
----------------

The Vancouver PoC pollinator module lives in
``data/poc/vancouver/pollinator_module/``.

``pollinator_review.csv``
   One row per Vancouver PoC species queued for pollinator evidence review.
   Each row keeps ``psi_readiness`` at ``not_ready``.

``pollinator_evidence_gaps.csv``
   Species-by-field gaps for bloom period, floral resources, native bee
   support, butterfly support, hummingbird support, specialist relationships,
   and larval host use.

``pollinator_source_requirements.csv``
   Minimum source-tier and review-status requirements for each pollinator
   field.

``manifest.json``
   Provenance, row counts, PSI policy, caveat, and public-hygiene flags.

``diagnostics.csv``
   Non-error caveats recorded at generation time.

CLI
---

Regenerate the module:

.. code-block:: shell

   bc-nppd generate-vancouver-pollinator-module data/poc/vancouver/usability --out-dir data/poc/vancouver/pollinator_module --json

Validate the tracked artifact:

.. code-block:: shell

   bc-nppd validate-vancouver-pollinator-module data/poc/vancouver/pollinator_module --json

Evidence Boundary
-----------------

The module is not a Pollinator Support Index calculator. ``review_queue`` and
``needs_review`` rows are not accepted ecological claims. Future work can
promote individual pollinator fields only after accepted source-attributed
evidence is recorded and review gates pass.

This boundary keeps the PoC useful for prioritizing review while preserving the
BC-NPPD rule that ecological values and scores must be evidence-backed.
