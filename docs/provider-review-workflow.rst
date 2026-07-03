Provider Review Workflow
========================

Provider source sweeps create observations, not approved BC-NPPD facts. The
expert review workflow turns an ignored sandbox into an approval manifest that
can be validated and applied.

Generate Review Inputs
----------------------

Run or reuse a provider sandbox. For the Satinflower seed source sweep:

.. code-block:: console

   bc-nppd scrape-provider-sandbox PROV-SATIN \
     --database-instance vancouver \
     --live-fetch \
     --source-sweep \
     --catalog-url https://satinflower.ca/collections/seed \
     --max-pages 5 \
     --raw-dir local/provider_raw \
     --out-dir outputs/provider_sandbox_source_sweep/PROV-SATIN \
     --json

Build the expert approval review app:

.. code-block:: console

   bc-nppd build-provider-approval-review \
     outputs/provider_sandbox_source_sweep/PROV-SATIN \
     --poc-dir data/poc/vancouver \
     --out-dir outputs/provider_approval_review/PROV-SATIN \
     --reviewer "expert reviewer" \
     --json

Open ``outputs/provider_approval_review/PROV-SATIN/index.html`` locally.

Review And Export
-----------------

The review app groups rows by botanical name. Use the search box, filters, and
detail panel to inspect:

* whether the candidate already matches a Vancouver PoC species;
* supplier availability rows;
* candidate attribute rows, including product descriptions and extracted
  ``Plant Details`` / ``Seed Details`` values when available;
* provisional mowability rows, if present;
* provider URLs and taxonomy/source-review flags.

Use the selection checkboxes and **Batch Review** controls when several species
need the same decision. Batch actions can:

* select all currently visible species after search/filtering;
* clear the current selection;
* set the approval status on all selected species;
* include or defer supplier rows on all selected approved species;
* include or defer candidate attribute rows on all selected approved species;
* include or defer provisional mowability rows on all selected approved species.

Set a species-level decision:

* ``approved`` for observations ready to enter the candidate PoC layer;
* ``rejected`` for rows that should stay out;
* ``deferred`` when no decision is ready;
* ``needs_source_review`` when the source/provenance is not sufficient;
* ``needs_taxonomy_review`` when the taxon needs name review before approval.

Attribute rows default to deferred. Mowability rows default to deferred because
mowability remains provisional. Supplier rows can be included with the species
decision when supplier availability is the reviewed claim.

Use **Download approval_manifest.csv** or **Copy CSV**. The static app does not
write directly to the repository.

Simple Apply Preview
--------------------

For the easiest user-test path, download ``approval_manifest.csv`` from the
review app into the default Downloads folder, then run:

.. code-block:: console

   .\scripts\apply-downloaded-provider-approval.cmd -OpenPreview

The command wrapper works on Windows systems that block direct PowerShell script
execution. It validates the downloaded manifest, copies it to an ignored
scratch path, applies approved rows into ``outputs/provider_approved_vancouver``,
regenerates downstream preview artifacts, validates the preview, and opens the
static preview app when ``-OpenPreview`` is included. It also prints the preview
path:

.. code-block:: text

   outputs/provider_approved_vancouver/usability/index.html

Use ``-ManifestPath`` when the CSV was saved somewhere else. The direct
PowerShell fallback is:

.. code-block:: console

   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\apply-downloaded-provider-approval.ps1 -OpenPreview

Greg or an automation agent can use the dependency-free FreshForge workflow
shape in ``examples/p21_downloaded_provider_approval_freshforge.yaml`` for the
same validate/apply/validate-preview sequence.

The script does not promote reviewed manifests into tracked product data. Only
after human inspection should a reviewed manifest be copied into a tracked input
path such as ``data/poc/vancouver/provider_data/reviewed_manifests/``.

Validate And Apply
------------------

Save the exported CSV as a local approval manifest, then validate it:

.. code-block:: console

   bc-nppd validate-provider-approvals path/to/approval_manifest.csv --json

Dry-run an approved manifest into ignored outputs:

.. code-block:: console

   bc-nppd apply-provider-approvals path/to/approval_manifest.csv \
     --poc-dir data/poc/vancouver \
     --out-dir outputs/provider_approved_vancouver \
     --json

Only after expert review should the manifest be promoted to a tracked reviewed
input path such as ``data/poc/vancouver/provider_data/reviewed_manifests/``.
Raw fetched catalogue JSON, HTML, screenshots, and generated review apps remain
ignored.

Caveats
-------

Provider approvals create candidate PoC data. They do not make native status,
ecological scores, pollinator scores, UNI, PSI, RVI, or mowability
score-readiness final.
