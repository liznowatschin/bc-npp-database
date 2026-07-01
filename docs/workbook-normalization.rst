Workbook Normalization
======================

P1 defines the workbook normalization contract before bulk CSV export.

Seed archives are unpacked only under ignored local paths such as
``local/seed/``. Raw PDFs, screenshots, extracted legacy repositories, generated
outputs, and unchecked source artifacts must not be tracked.

Current workbook source
-----------------------

The latest tracked workbook snapshot is:

.. code-block:: text

   data/workbooks/native_plant_restoration_workbook_v1.0.0c.xlsx

Its main sheets are mapped as follows:

.. list-table::
   :header-rows: 1

   * - Sheet
     - Direction
   * - Species_Master
     - Candidate species table.
   * - Lookup_Tables
     - Controlled vocabulary records.
   * - Reference_Policy
     - Source policy documentation and future reference configuration.
   * - Source_Attribution
     - Field/source attribution records.
   * - Bloom_Calendar
     - Derived or validated bloom-month records.
   * - Dashboard
     - Report output concept, not canonical source data.
   * - QA_Log
     - Review queue or issue provenance.

CLI
---

.. code-block:: bash

   bc-nppd inventory-workbook data/workbooks/native_plant_restoration_workbook_v1.0.0c.xlsx
   bc-nppd validate-workbook data/workbooks/native_plant_restoration_workbook_v1.0.0c.xlsx --json

P1 inspection helpers are read-only. Deterministic exports remain deferred until
a later phase approves canonical tracked data.
