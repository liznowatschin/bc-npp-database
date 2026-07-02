Source Attribution
==================

Phase 2 defines BC-NPPD's source and evidence contracts. These records make
ecological claims auditable before later phases normalize workbook data, query
source documents, or calculate scores.

Record Types
------------

The package now distinguishes:

``SourceRecord``
   A citable source or reference, with source ID, name, tier, citation or URL,
   optional external ID, review status, and notes.

``SourceAttributionRecord``
   A row connecting a source to a supported claim or field. Species-specific
   claims require a stable ``BCNPPD-0001`` style species ID.

``MaterializationManifest``
   A record for future source resolution or acquisition artifacts, such as BC
   Data Catalogue manifests or workflow summaries.

``MediaExtractionManifest``
   A record for future review-gated figure, table, PDF, or image extraction
   artifacts.

ID And Review Rules
-------------------

Source/reference IDs use ``SRC-0001`` or ``REF-0001`` style identifiers.
External IDs must be namespaced, such as ``bcdc:package:abc123``,
``hectaresbc:dl_adminunits_bcts``, ``figrecover:review:abc``, or
``freshforge:workflow:run``.

Evidence confidence stays separate from review status. Unreviewed or rejected
media and materialization outputs cannot be treated as accepted candidate
evidence. Unknown ecological values remain unknown until reviewed sources
support them.

CLI
---

Validate source records from CSV, JSON, or JSON Lines:

.. code-block:: bash

   bc-nppd validate-source-records sources.csv --json

Validate source attribution rows:

.. code-block:: bash

   bc-nppd validate-source-attribution source_attribution.json --json

These commands use synthetic/public-safe files in tests. They do not fetch
external data, parse PDFs, run figrecover, or query GIS services.
