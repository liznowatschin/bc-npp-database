# Vancouver Plant List PoC

This directory contains the tracked Vancouver/CDF plant-list PoC. As of the
July 2026 all-provider promotion it validates at 493 plant rows, including the
original tracked workbook seed rows, unreviewed user-submitted expansion
candidates, and provider-derived candidate observations from the configured
provider registry.

Inspect:

* `plant_list.csv` for the plant list.
* `sources.csv` for deterministic `SRC-*` source records.
* `source_attribution.csv` for species/source links.
* `requested_species_additions.csv` for the request audit and deduplication
  disposition.
* `provider_data/` for provider approval decisions, candidate species,
  candidate attributes, supplier rows, provisional mowability rows, and
  provider attribution.
* `exports/vancouver_poc_export.xlsx` for a downloadable formatted Excel dump
  of the current tracked PoC database instance.
* `manifest.json` for generation metadata and caveats.
* `diagnostics.csv` for PoC warnings.

This is a proof of concept, not a final planting recommendation list.
Provider-derived and other candidate values remain pending review unless a
tracked source artifact explicitly says otherwise.
