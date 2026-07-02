Vancouver Plant List PoC
========================

Phase 6 creates the first useful BC-NPPD product artifact: a caveated
20-species Vancouver/CDF plant list generated from the tracked workbook
snapshot.

Where To Inspect
----------------

The tracked PoC artifacts live in ``data/poc/vancouver/``:

``plant_list.csv``
   Human-inspectable plant list with stable ``BCNPPD-*`` IDs, preserved legacy
   ``CDF-*`` IDs, common names, selected workbook fields, source references,
   and PoC caveats.

``sources.csv``
   Deterministic ``SRC-*`` source registry generated from workbook
   source-attribution rows.

``source_attribution.csv``
   Valid source-attribution links between PoC species IDs and source IDs.

``manifest.json``
   Generation metadata, row counts, public-hygiene flags, and caveats.

``diagnostics.csv``
   Non-error PoC caveats. The tracked artifact validates with no hard errors.

CLI
---

Regenerate the PoC list from the tracked workbook:

.. code-block:: shell

   bc-nppd generate-vancouver-poc-list data/workbooks/native_plant_restoration_workbook_v1.0.0c.xlsx --out-dir data/poc/vancouver --json

Validate the tracked artifact:

.. code-block:: shell

   bc-nppd validate-vancouver-poc-list data/poc/vancouver --json

Boundary
--------

The PoC list is useful for inspection, prioritization, and workflow validation.
It is not yet a final planting recommendation list. Phase 7 should harden
field-level evidence and Phase 8 should add more usable filtered views.

Phase 7 Evidence Layer
----------------------

The P7 evidence-hardening layer lives in
``data/poc/vancouver/evidence_hardening/``. It marks identity/native-range
fields as PoC-reviewed where Tier 1/2 taxonomy attribution exists, records
field-level evidence gaps, and keeps UNI, PSI, and RVI readiness at
``not_ready`` until reviewed score inputs exist.

Validate it with:

.. code-block:: shell

   bc-nppd validate-vancouver-evidence data/poc/vancouver/evidence_hardening --json

Phase 8 Usability Layer
-----------------------

The P8 static inspection layer lives in ``data/poc/vancouver/usability/``.
Open ``index.html`` directly in a browser to inspect the 20-species table with
search and candidate view filters.

Validate it with:

.. code-block:: shell

   bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json
