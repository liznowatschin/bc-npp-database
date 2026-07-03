# Vancouver Plant List PoC

This directory contains the first useful BC-NPPD product artifact: a caveated
54-species Vancouver/CDF plant list. It includes the original tracked workbook
seed rows, unreviewed user-submitted expansion candidates, and a caveated P18
demo provider-data candidate.

Inspect:

* `plant_list.csv` for the plant list.
* `sources.csv` for deterministic `SRC-*` source records.
* `source_attribution.csv` for species/source links.
* `requested_species_additions.csv` for the request audit and deduplication
  disposition.
* `provider_data/` for the P18 demo approval manifest, supplier row,
  provisional mowability row, and provider attribution.
* `manifest.json` for generation metadata and caveats.
* `diagnostics.csv` for PoC warnings.

This is a proof of concept, not a final planting recommendation list. Candidate
values remain subject to evidence hardening in a later phase.
