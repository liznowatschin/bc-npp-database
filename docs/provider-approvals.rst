Provider Approvals
==================

P17 adds the approval gate between provider sandbox outputs and the tracked
Vancouver PoC product. Provider observations are not facts by default. They
enter the PoC only when an approval manifest marks a row ``approved``.

The tracked Vancouver PoC stores provider approval data under
``data/poc/vancouver/provider_data``. Provider-derived rows remain
candidate/pending-review observations unless a later review artifact promotes a
specific value.

Approval Manifest
-----------------

Approval manifests use ``approval_manifest.csv`` columns documented in
``schemas/provider_approval_manifest_columns.csv``. Supported approval statuses
are:

* ``approved``
* ``rejected``
* ``deferred``
* ``needs_source_review``
* ``needs_taxonomy_review``

Only ``approved`` rows are imported. Rejected, deferred, and review-needed rows
remain part of the audit trail but do not update plant, source, supplier, or
mowability artifacts.

Provider Data Artifacts
-----------------------

Approved supplier and mowability observations are stored under
``provider_data`` beside the Vancouver PoC artifacts:

* ``approval_manifest.csv``
* ``candidate_species.csv``
* ``candidate_attributes.csv``
* ``supplier_availability.csv``
* ``mowability.csv``
* ``source_attribution.csv``
* ``manifest.json``
* ``diagnostics.csv``

Supplier rows are separate from plant identity rows because one species can
have multiple providers. Mowability remains a provisional 0-5 candidate signal;
it does not make UNI, PSI, or RVI score inputs ready.

Commands
--------

Build a static expert review app from a provider sandbox:

.. code-block:: console

   bc-nppd build-provider-approval-review outputs/provider_sandbox_source_sweep/PROV-SATIN --poc-dir data/poc/vancouver --out-dir outputs/provider_approval_review/PROV-SATIN --reviewer "expert reviewer" --json

The full reviewer workflow is documented in ``provider-review-workflow``.

Validate an approval manifest:

.. code-block:: console

   bc-nppd validate-provider-approvals examples/provider_approval_manifest.csv --json

Apply approved rows to a Vancouver PoC output directory:

.. code-block:: console

   bc-nppd apply-provider-approvals examples/provider_approval_manifest.csv --poc-dir data/poc/vancouver --out-dir outputs/provider_approved_vancouver --json

Use ``--skip-regeneration`` for fast dry runs that do not regenerate evidence,
usability, or pollinator artifacts.

Tracked Provider Data
---------------------

The current Vancouver PoC includes the July 2026 all-provider promotion from
Satinflower, Northwest Meadowscapes, West Coast Seeds, Premier Pacific Seeds,
and Oak Summit Nursery. The tracked provider data validates at 5,160 approval
rows, 402 candidate-species rows, 1,816 candidate-attribute rows, 603 supplier
rows, and 1 provisional mowability row. These rows support inspection and
review; they do not promote provider values to reviewed ecological facts.
