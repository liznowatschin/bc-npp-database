Seed Archives
=============

The seed archives are provenance inputs for BC-NPPD. They are not tracked
source-of-truth data.

Local extraction policy
-----------------------

Seed archives may be extracted under ignored local paths such as:

.. code-block:: text

   local/seed/

Do not track extracted archive directories, raw PDFs, screenshots, unpublished
source artifacts, or generated local exports.

Tracked derivatives
-------------------

Public-safe tracked derivatives may include:

* Cleaned planning notes.
* Sphinx documentation.
* Schema and lookup CSV seeds.
* Tests and synthetic fixtures.
* Approved workbook snapshots retained for traceability.

Use ``planning/seed_archive_inventory.md`` for the current archive inventory and
disposition notes.
