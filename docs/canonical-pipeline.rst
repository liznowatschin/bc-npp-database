Canonical Pipeline
==================

Phase 3 adds a package-backed canonical import and export layer for approved
workbook-shaped inputs. The pipeline is intentionally conservative: it converts
known sheets into structured records, preserves source-attribution rows for
validation, and emits diagnostics when values are incomplete or unsupported.

Imported Sheets
---------------

``Species_Master``
   Candidate species rows using the canonical master species column order from
   ``schemas/master_species_columns.csv``. Legacy workbook headers such as
   ``Species_ID`` and ``Botanical_Name`` are normalized to canonical names such
   as ``Species ID`` and ``Botanical Name``.

``Lookup_Tables``
   Controlled vocabulary rows. P3 supports simple ``lookup_name,value`` shaped
   rows and conservative workbook-block extraction.

``Source_Attribution``
   Evidence rows normalized into the P2 source-attribution validator. These rows
   support future review and joins; they are not treated as ecological facts by
   import alone.

``Bloom_Calendar``
   Month columns are imported as candidate bloom-calendar rows. P3 does not
   calculate scores or infer missing bloom values.

Validation Rules
----------------

Canonical import emits structured diagnostics for missing required species
fields, invalid ``BCNPPD-0001`` species IDs, invalid evidence confidence values,
duplicate species IDs, excluded source URLs, invalid source-attribution rows,
and sheets that are not imported by the canonical pipeline.

Warnings, such as ignored dashboard sheets, do not fail the CLI. Error
diagnostics produce a nonzero CLI exit code.

CLI
---

Inspect a workbook without writing files:

.. code-block:: shell

   bc-nppd import-canonical-workbook data/workbooks/native_plant_restoration_workbook_v1.0.0c.xlsx --json

Export deterministic CSV tables to an ignored output directory:

.. code-block:: shell

   bc-nppd export-canonical-workbook data/workbooks/native_plant_restoration_workbook_v1.0.0c.xlsx --out-dir outputs/p3 --json

Exported tables are intended for local review under ``outputs/`` unless a later
release task explicitly approves a public tracked derivative.

FreshForge Shape
----------------

P3 records an optional FreshForge workflow shape but does not add FreshForge as
a dependency. A future workflow provider can map these steps onto reproducible
nodes:

* ``workbook.inventory``
* ``workbook.import_tables``
* ``tables.validate``
* ``tables.export``

The example YAML in ``examples/p3_canonical_pipeline_freshforge.yaml`` is a
planning artifact only. CI does not execute it.
