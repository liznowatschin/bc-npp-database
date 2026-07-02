v1.0.0a Foundation
==================

Phase 5 prepares the BC-NPPD v1.0.0a foundation scaffold. It does not publish a
GitHub release or imply that the full workbook has been reviewed.

Tracked Foundation Artifacts
----------------------------

The public-safe foundation artifacts live under
``data/foundation/v1.0.0a/``:

``schema_freeze.json``
   Records the schema files, package contracts, foundation species IDs, and
   public-hygiene boundaries included in the foundation.

``species.csv``
   Contains one reviewed example species row for ``Achillea millefolium``.
   Unresolved ecological values remain ``Unknown``.

``sources.csv`` and ``source_attribution.csv``
   Preserve the source IDs and evidence-attribution rows for the foundation
   record.

``score_inputs.csv``
   Exercises the P4 score-input contract with explicit placeholder schema
   exercise rows. These rows are not ecological suitability claims.

``release_checklist.md``
   Lists the release-preparation checks that must be satisfied before a future
   approved tag.

Validation
----------

Validate the foundation directory:

.. code-block:: shell

   bc-nppd validate-foundation data/foundation/v1.0.0a --json

The validator checks required files, schema-freeze metadata, canonical species
row shape, source records, source-attribution records, score inputs, and
cross-file species/source links.

Release Boundary
----------------

P5 prepares release artifacts but does not create tag ``v1.0.0a``. A future
maintainer-approved release step must rerun acceptance on ``main``, confirm
GitHub CI and Docs workflows, review release notes, and then create the tag.
