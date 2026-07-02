Scoring Framework
=================

Phase 4 defines evidence-aware scoring records for three BC-NPPD score
families:

``UNI``
   Urban Native Index.

``PSI``
   Pollinator Support Index.

``RVI``
   Restoration Value Index.

P4 scores are provisional framework outputs. They are calculated only from
explicit numeric score inputs that already carry source IDs, evidence
confidence, and accepted or manually corrected review status.

Score Inputs
------------

Each score input must include:

* species ID, such as ``BCNPPD-0001``;
* score family, one of ``UNI``, ``PSI``, or ``RVI``;
* metric name;
* numeric value from 0 to 5;
* source or reference ID, such as ``SRC-0001``;
* evidence confidence;
* review status.

Optional external or context IDs may point to reviewed GIS, media, or workflow
context. These fields are provenance only. They do not create score values.

Calculation Rule
----------------

P4 uses a transparent provisional formula:

.. code-block:: text

   score = weighted_average(reviewed_input_values) / 5 * 100

Inputs with invalid values, missing source IDs, invalid evidence confidence,
missing weights, or unaccepted review status are diagnosed and excluded.

CLI
---

Validate inputs:

.. code-block:: shell

   bc-nppd validate-score-inputs scores.csv --weights weights.csv --json

Calculate scores:

.. code-block:: shell

   bc-nppd calculate-scores scores.csv --weights weights.csv --json

The CLI accepts CSV, JSON, and JSON Lines files using the same mapping loader as
the source-attribution validators.

Deferred Work
-------------

P4 does not select final ecological weights, run external GIS/raster workflows,
execute media extraction, or publish reviewed score tables. Those actions remain
future review or release tasks.
