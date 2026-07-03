Provider Sandbox
================

P15 adds source-provider records and provider sandbox contracts for future
supplier website workflows. It does not scrape live websites or update the
tracked Vancouver PoC plant list.

Provider registry
-----------------

The tracked provider registry lives at
``data/source_providers/provider_registry.csv``. Provider IDs use ``PROV-*``:

* ``PROV-SATIN``: Satinflower Nurseries.
* ``PROV-NWM``: Northwest Meadowscapes.
* ``PROV-WCS``: West Coast Seeds.
* ``PROV-PREMIER``: Premier Pacific Seeds.

All four providers are treated as Tier 3 commercial or practitioner sources.
They may support supplier availability, cultivation clues, candidate species
discovery, and candidate mowability observations. They are not sole authority
for native status, ecological scoring, pollinator scoring, or final planting
recommendations.

Sandbox contracts
-----------------

Provider scrape and review outputs must be sandboxed before integration. A
valid sandbox directory contains:

* ``manifest.json``
* ``inventory_pages.csv``
* ``candidate_species.csv``
* ``candidate_attributes.csv``
* ``supplier_availability.csv``
* ``mowability.csv``
* ``diagnostics.csv``

The column contracts are documented in
``schemas/provider_sandbox_contracts.csv``. Vancouver eligibility rules are
documented in ``schemas/vancouver_provider_eligibility_rules.csv``.

Vancouver rules
---------------

Provider observations start as candidate data. West Coast Seeds vegetable rows
must be excluded. Northwest Meadowscapes rows require Vancouver or BC
suitability review before they can be treated as directly eligible.

Supplier information is stored separately from plant identity rows because one
species can have multiple suppliers. Mowability is a provisional 0-5 candidate
score and does not make UNI, PSI, or RVI score readiness become ready.

Validation
----------

Validate the tracked provider registry:

.. code-block:: bash

   bc-nppd validate-source-providers data/source_providers/provider_registry.csv --json

Validate a future provider sandbox directory:

.. code-block:: bash

   bc-nppd validate-provider-sandbox outputs/provider_sandbox/PROV-SATIN --json

P16 fixture-backed sandbox generation:

.. code-block:: bash

   bc-nppd scrape-provider-sandbox PROV-SATIN --input-dir tests/fixtures/providers --out-dir outputs/provider_sandbox/PROV-SATIN --json
   bc-nppd build-provider-review outputs/provider_sandbox/PROV-SATIN --out-dir outputs/provider_review/PROV-SATIN --json

Targeted source sweep
---------------------

For user-testing or manual review, provider catalogues can be swept into an
ignored sandbox directory. This is still a review workflow: rows are provider
observations, not approved Vancouver PoC facts.

The Satinflower seed-collection entrypoint is:

.. code-block:: bash

   bc-nppd scrape-provider-sandbox PROV-SATIN \
     --database-instance vancouver \
     --live-fetch \
     --source-sweep \
     --catalog-url https://satinflower.ca/collections/seed \
     --max-pages 5 \
     --raw-dir local/provider_raw \
     --out-dir outputs/provider_sandbox_source_sweep/PROV-SATIN \
     --json
   bc-nppd validate-provider-sandbox outputs/provider_sandbox_source_sweep/PROV-SATIN --json
   bc-nppd build-provider-review outputs/provider_sandbox_source_sweep/PROV-SATIN \
     --out-dir outputs/provider_review_source_sweep/PROV-SATIN \
     --json
   bc-nppd build-provider-approval-review outputs/provider_sandbox_source_sweep/PROV-SATIN \
     --poc-dir data/poc/vancouver \
     --out-dir outputs/provider_approval_review/PROV-SATIN \
     --reviewer "expert reviewer" \
     --json

The source sweep currently supports Shopify-style product catalog feeds. For
Satinflower-style product bodies, it extracts product descriptions plus
``Plant Details`` and ``Seed Details`` table rows into
``candidate_attributes.csv``. Raw catalog JSON is written only under
``local/provider_raw``. Review CSV and HTML bundles are written under
``outputs`` and must remain untracked unless a later phase explicitly approves a
public-safe derivative.

The dependency-free FreshForge workflow shape for this process lives at
``examples/p19_provider_source_sweep_freshforge.yaml``. It can be copied or
overlaid per provider by changing ``provider_id`` and ``catalog_url``.

The expert review walkthrough lives in ``provider-review-workflow``. It explains
how to inspect the local approval app, export ``approval_manifest.csv``,
validate it, and dry-run approved rows into ignored PoC outputs.

Raw provider HTML, screenshots, downloads, and scrape caches must remain under
ignored directories such as ``local/``, ``tmp/``, ``data/raw/``, or
``outputs/``.

Approval Boundary
-----------------

P16 review bundles do not update the Vancouver PoC. P17 consumes a separate
``approval_manifest.csv`` and imports only rows marked ``approved``. Supplier
and mowability observations stay in separate provider-data tables, and
mowability remains a provisional candidate signal.
