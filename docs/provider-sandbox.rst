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

Raw provider HTML, screenshots, downloads, and scrape caches must remain under
ignored directories such as ``local/``, ``tmp/``, ``data/raw/``, or
``outputs/``.
