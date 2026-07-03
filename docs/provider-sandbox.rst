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
* ``PROV-OAKSUMMIT``: Oak Summit Nursery.

All providers are treated as Tier 3 commercial or practitioner sources.
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
``candidate_attributes.csv``. If a provider allows public collection HTML but
disallows the Shopify ``products.json`` catalogue endpoint, the scraper falls
back to the collection HTML and extracts product titles, product URLs, and
product types only. Raw catalog JSON or HTML is written only under
``local/provider_raw``. Review CSV and HTML bundles are written under
``outputs`` and must remain untracked unless a later phase explicitly approves a
public-safe derivative.

FreshForge Source-Review Workflow
---------------------------------

P29 makes FreshForge the canonical workflow runner for repeated provider source
sweeps. Install the workflow extra when FreshForge is not already available:

.. code-block:: console

   python -m pip install -e .[workflow]

Then build a provider review package with the Windows launcher:

.. code-block:: console

   .\scripts\build-provider-source-review.cmd PROV-SATIN -OpenReview

To create a new provider-specific workflow file with the correct FreshForge
node shape, use the BC-NPPD authoring helper:

.. code-block:: console

   bc-nppd generate-provider-source-workflow PROV-PREMIER \
     --catalog-url https://premierpacificseeds.ca \
     --out-path examples/workflows/providers/PROV-PREMIER.yaml \
     --force

This helper only writes FreshForge-compatible YAML. It does not validate, plan,
or execute the workflow; FreshForge still owns those steps.

The launcher calls ``freshforge run`` on a provider-specific workflow YAML. It
does not reimplement the scrape/validate/review sequence itself. Provider
workflow files live under ``examples/workflows/providers/``:

* ``PROV-SATIN.yaml``
* ``PROV-NWM.yaml``
* ``PROV-WCS.yaml``
* ``PROV-PREMIER.yaml``
* ``PROV-OAKSUMMIT.yaml``

The generic workflow shape lives at
``examples/workflows/provider_source_review.yaml``. The historical
``examples/p19_provider_source_sweep_freshforge.yaml`` path remains as a
compatibility example, but the P29 workflow files are the preferred surface.
Use lower-level ``bc-nppd`` commands only for debugging or manual fallback.

P30 uses ``PROV-OAKSUMMIT`` as the first post-P29 new-provider bootstrap
exercise. Its generated workflow points at the Oak Summit Nursery native-seed
collection and routes all observations through the same ignored sandbox,
review, and approval-review directories as the other providers.

The expert review walkthrough lives in ``provider-review-workflow``. It explains
how to inspect the local approval app, export ``approval_manifest.csv``,
validate it, and dry-run approved rows into ignored PoC outputs.

Northwest Meadowscapes Source Sweep
-----------------------------------

Northwest Meadowscapes uses common-name-first Shopify product titles such as
``Western Yarrow Seeds (Achillea millefolium)``. The provider adapter parses
botanical names from parentheticals and skips NWM products without botanical
parentheticals, such as tools, books, and vegetables. NWM rows remain
``needs_northward_review`` until Vancouver or BC suitability is reviewed.

Run the NWM source sweep with:

.. code-block:: bash

   bc-nppd scrape-provider-sandbox PROV-NWM \
     --database-instance vancouver \
     --live-fetch \
     --source-sweep \
     --catalog-url https://northwestmeadowscapes.com \
     --max-pages 5 \
     --raw-dir local/provider_raw \
     --out-dir outputs/provider_sandbox_source_sweep/PROV-NWM \
     --json
   bc-nppd validate-provider-sandbox outputs/provider_sandbox_source_sweep/PROV-NWM --json
   bc-nppd build-provider-review outputs/provider_sandbox_source_sweep/PROV-NWM \
     --out-dir outputs/provider_review_source_sweep/PROV-NWM \
     --json
   bc-nppd build-provider-approval-review outputs/provider_sandbox_source_sweep/PROV-NWM \
     --poc-dir data/poc/vancouver \
     --out-dir outputs/provider_approval_review/PROV-NWM \
     --reviewer "expert reviewer" \
     --json

West Coast Seeds Source Sweep
-----------------------------

West Coast Seeds is treated as a Tier 3 commercial/practitioner provider.
The adapter uses the WCS ``wildflower-seeds`` and ``lawn-solutions`` Shopify
collection feeds by default instead of the site-wide product feed, because the
site-wide feed contains vegetables and many unrelated products. WCS rows are
kept as review-only observations: single-species products can be parsed from
body text, blend ingredient lists can become candidate species observations,
and blend ingredients are recorded as ``mix_component`` supplier rows.

All WCS candidate species remain ``needs_review`` until an expert rejects,
defers, or approves them. This is especially important because many commercial
wildflower blend components are not native to Vancouver or British Columbia.

Run the WCS source sweep with:

.. code-block:: bash

   bc-nppd scrape-provider-sandbox PROV-WCS \
     --database-instance vancouver \
     --live-fetch \
     --source-sweep \
     --max-pages 3 \
     --raw-dir local/provider_raw \
     --out-dir outputs/provider_sandbox_source_sweep/PROV-WCS \
     --json
   bc-nppd validate-provider-sandbox outputs/provider_sandbox_source_sweep/PROV-WCS --json
   bc-nppd build-provider-review outputs/provider_sandbox_source_sweep/PROV-WCS \
     --out-dir outputs/provider_review_source_sweep/PROV-WCS \
     --json
   bc-nppd build-provider-approval-review outputs/provider_sandbox_source_sweep/PROV-WCS \
     --poc-dir data/poc/vancouver \
     --out-dir outputs/provider_approval_review/PROV-WCS \
     --reviewer "expert reviewer" \
     --json

Raw provider HTML, screenshots, downloads, and scrape caches must remain under
ignored directories such as ``local/``, ``tmp/``, ``data/raw/``, or
``outputs/``.

Approval Boundary
-----------------

P16 review bundles do not update the Vancouver PoC. P17 consumes a separate
``approval_manifest.csv`` and imports only rows marked ``approved``. Supplier
and mowability observations stay in separate provider-data tables, and
mowability remains a provisional candidate signal.
