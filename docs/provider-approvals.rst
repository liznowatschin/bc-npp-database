Provider Approvals
==================

P17 adds the approval gate between provider sandbox outputs and the tracked
Vancouver PoC product. Provider observations are not facts by default. They
enter the PoC only when an approval manifest marks a row ``approved``.

P18 tracks a small demo approval manifest under
``data/poc/vancouver/provider_data`` so the provider-data workflow can be
user-tested in the public PoC. These rows remain candidate/demo observations.

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

Tracked Demo
------------

The current Vancouver PoC includes a P18 demo provider-data slice with one
supplier row, one provisional mowability row, and one added provider candidate
species. The rejected vegetable demo row remains excluded. This demo exists for
interface testing and does not promote provider values to reviewed ecological
facts.
