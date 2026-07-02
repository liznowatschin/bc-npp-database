Evidence Hardening
==================

Phase 7 adds a field-level evidence-hardening layer for the Vancouver plant list
PoC. It does not fetch new sources, infer ecological values, or calculate
scores. It separates fields that are usable for PoC inspection from fields that
still need review.

Where To Inspect
----------------

The tracked hardening artifacts live in
``data/poc/vancouver/evidence_hardening/``:

``hardened_plant_list.csv``
   The 52 PoC species with reviewed-field counts, gap counts, hardening status,
   and score-readiness flags.

``reviewed_sources.csv``
   P7 source-review layer. Tier 1/2 sources are usable for PoC
   identity/native-range review. Tier 3 practitioner sources remain context.

``reviewed_fields.csv``
   Field-level rows that are PoC-reviewed. P7 limits these to botanical name,
   common name, family, and native status where Tier 1/2
   taxonomy/native-range attribution exists.

``evidence_gap_report.csv``
   Candidate or missing fields that still need field-specific review before
   promotion.

``score_readiness.csv``
   UNI, PSI, and RVI readiness rows. Every row is ``not_ready`` in P7.

``manifest.json``
   Row counts, score policy, public-hygiene flags, and caveats.

``diagnostics.csv``
   Non-error caveats for the hardening layer.

CLI
---

Regenerate the hardening layer:

.. code-block:: shell

   bc-nppd harden-vancouver-evidence data/poc/vancouver --out-dir data/poc/vancouver/evidence_hardening --json

Validate the tracked artifact:

.. code-block:: shell

   bc-nppd validate-vancouver-evidence data/poc/vancouver/evidence_hardening --json

Evidence Boundary
-----------------

P7 promotes only identity/native-range display fields to ``poc_reviewed`` when
the plant has Tier 1/2 taxonomy/native-range attribution. Horticultural,
use-case, and score-related fields remain candidate values.

The ``score_readiness.csv`` report deliberately marks UNI, PSI, and RVI as
``not_ready`` for every species. Workbook suitability and toughness values are
useful triage clues, but they are not accepted P4 score inputs until field-level
review creates explicit score-input rows.
