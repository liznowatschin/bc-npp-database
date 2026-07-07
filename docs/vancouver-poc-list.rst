Vancouver Plant List PoC
========================

Phase 6 created the first useful BC-NPPD product artifact. The current tracked
artifact is a caveated 493-row Vancouver/CDF plant list including the original
workbook snapshot rows, unreviewed user-submitted expansion candidates, and
all-provider candidate observations promoted from the July 2026 provider
source-sweep preview.

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

``requested_species_additions.csv``
   Request audit showing submitted names, deduplication disposition, assigned
   species IDs, and notes for the expansion candidates.

``provider_data/``
   Provider approval manifest, candidate species, candidate attributes,
   supplier availability, provisional mowability, provider source attribution,
   manifest, and diagnostics.

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

Export the tracked Vancouver PoC database to a formatted Excel workbook:

.. code-block:: shell

   bc-nppd export-vancouver-poc-excel data/poc/vancouver \
     --out-path outputs/vancouver_poc_export.xlsx \
     --json
   bc-nppd validate-vancouver-poc-excel outputs/vancouver_poc_export.xlsx --json

A downloadable copy of the current tracked export is committed at
``data/poc/vancouver/exports/vancouver_poc_export.xlsx``.

The July 2026 tracked PoC contains 493 plant rows, 460 sources, 5,176
source-attribution rows, 5,160 provider approval-manifest rows, 402 provider
candidate-species rows, 1,816 provider candidate-attribute rows, 603 supplier
rows, and 1 mowability row. Provider-derived rows remain candidate/pending
review data with source-attribution caveats.

The Excel workbook is a formatted inspection copy, not a new source of truth.
It includes an overview sheet, flattened manifests, core PoC tables, source
attribution, provider data, evidence-hardening tables, usability views, and
pollinator review tables when those artifacts exist in the input directory.
Sheets use frozen headers, filters, Excel table styling, wrapped text,
reasonable column widths, and hyperlinks for URL fields.

Boundary
--------

The PoC list is useful for inspection, prioritization, and workflow validation.
It is not yet a final planting recommendation list. User-submitted expansion
candidates remain ``Pending review`` until identity, native range, traits,
sources, pollinator relationships, and planting suitability are reviewed.

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
Open ``index.html`` directly in a browser to inspect the 493-row table with
search, candidate view filters, provider-data filters, and detail-panel
provider provenance.

Validate it with:

.. code-block:: shell

   bc-nppd validate-vancouver-usability data/poc/vancouver/usability --json
