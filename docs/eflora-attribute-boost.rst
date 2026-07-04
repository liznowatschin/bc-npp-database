E-Flora Attribute Boost
=======================

P32 adds a review-gated E-Flora BC attribute boost sandbox. E-Flora is treated
as a Tier 2 academic/reference source, not as a commercial provider.

What It Produces
----------------

The boost workflow resolves botanical names to E-Flora atlas pages and writes an
ignored sandbox directory with:

* ``resolved_species.csv``
* ``candidate_attributes.csv``
* ``source_attribution.csv``
* ``synonyms.csv``
* ``diagnostics.csv``
* ``manifest.json``

Candidate values remain pending review. They can support source-attributed
review work, but they do not automatically make BC-NPPD fields reviewed or
score-ready.

CLI Workflow
------------

Fixture-backed or previously materialized atlas pages:

.. code-block:: console

   bc-nppd build-eflora-boost data/poc/vancouver/plant_list.csv ^
     --input-dir local/eflora_raw ^
     --out-dir outputs/eflora_boost/vancouver ^
     --json

Live fetches must be explicit and write raw HTML only to ignored storage:

.. code-block:: console

   bc-nppd build-eflora-boost data/poc/vancouver/plant_list.csv ^
     --live-fetch ^
     --raw-dir local/eflora_raw ^
     --out-dir outputs/eflora_boost/vancouver ^
     --json

Validate and preview-apply the boost:

.. code-block:: console

   bc-nppd validate-eflora-boost outputs/eflora_boost/vancouver --json
   bc-nppd apply-eflora-boost outputs/eflora_boost/vancouver ^
     --poc-dir data/poc/vancouver ^
     --out-dir outputs/eflora_boost_preview/vancouver ^
     --json

Preview application fills blank, ``Unknown``, or ``Pending review`` fields only.
It must not overwrite non-empty reviewed values in ``plant_list.csv``.

FreshForge Workflow
-------------------

The FreshForge example is:

.. code-block:: console

   freshforge run examples/workflows/eflora_attribute_boost.yaml --workdir . --json

The E-Flora workflow nodes are exposed through the
``bc_npp_database.eflora`` FreshForge provider namespace:

* ``bc_npp_database.eflora.resolve_species``
* ``bc_npp_database.eflora.extract_boost``
* ``bc_npp_database.eflora.validate_boost``
* ``bc_npp_database.eflora.apply_preview``

Public Hygiene
--------------

Raw E-Flora HTML belongs under ignored ``local/`` or ``outputs/`` paths.
Tracked files should be limited to source contracts, tests, documentation,
example workflows, and intentionally reviewed derivatives.
