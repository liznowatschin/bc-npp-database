# P16 Provider Scraping Sandbox Plan

Date: 2026-07-03

## Goal

P16 should build the first provider scraping sandbox: a safe, review-first
pipeline that can parse provider inventory/product pages into normalized CSV
tables and a static review page without integrating data into the Vancouver PoC
database.

## Scope

In scope:

* fixture-backed provider adapters for `PROV-SATIN`, `PROV-NWM`, `PROV-WCS`,
  and `PROV-PREMIER`;
* optional live-fetch entry points that write raw material only to ignored
  directories;
* normalized sandbox tables matching the P15 contract;
* Vancouver eligibility classification;
* CSV plus static HTML review outputs;
* CLI commands for scrape/build/validate workflows.

Out of scope:

* updating `data/poc/vancouver`;
* assigning new `BCNPPD-*` IDs;
* approving provider observations;
* making supplier or mowability data visible in the main PoC web app;
* changing UNI, PSI, or RVI score readiness.

## Provider Adapter Direction

Each adapter should return the same provider sandbox records even if the source
site structure differs. The first implementation should prefer deterministic
fixture parsing and small, boring extraction helpers over clever scraping.

Provider-specific guardrails:

* Satinflower: broadly in scope for southern Vancouver Island native plants,
  seeds, blends, propagation, supplier availability, and cultivation clues.
* Northwest Meadowscapes: useful PNW candidate context, but default species
  rows to `needs_northward_review` unless Vancouver/BC suitability evidence is
  explicit.
* West Coast Seeds: exclude vegetables; route native wildflower, regional
  wildflower, and lawn-compatible material through review.
* Premier Pacific: useful for BC seed supplier context, native grasses/forbs,
  reclamation seed, wildflower seed, and lawn/turf cues.

## Data Flow

1. Load the tracked provider registry.
2. Resolve provider adapter by provider ID.
3. Parse fixture HTML in CI, or optionally fetch live pages into ignored local
   raw storage.
4. Normalize observations into:
   * `inventory_pages.csv`;
   * `candidate_species.csv`;
   * `candidate_attributes.csv`;
   * `supplier_availability.csv`;
   * `mowability.csv`;
   * `diagnostics.csv`;
   * `manifest.json`.
5. Validate the sandbox with the P15 validator.
6. Build a static review page and review CSV bundle under ignored
   `outputs/provider_review/`.

## CLI Direction

P16 should add:

```bash
bc-nppd scrape-provider-sandbox PROVIDER_ID --database-instance vancouver --out-dir outputs/provider_sandbox/PROVIDER_ID --json
bc-nppd build-provider-review outputs/provider_sandbox/PROVIDER_ID --out-dir outputs/provider_review/PROVIDER_ID --json
```

Live fetching should be opt-in. If a command runs without a live-fetch flag, it
should use fixture or previously materialized input paths.

## Public Hygiene

Do not track raw HTML, rendered pages, screenshots, downloaded assets, caches,
or generated review outputs. Track only source code, tests, schemas, planning
notes, and public-safe examples.

Provider text should be attributed by source URL and provider ID. Scraped rows
are observations and remain `pending_review` until an approval phase.

## Acceptance Direction

P16 is acceptable when:

* each configured provider has at least one fixture-backed adapter test;
* sandbox outputs validate cleanly for synthetic provider fixtures;
* WCS vegetable rows are excluded or error-diagnosed;
* NWM rows are classified for northward/Vancouver suitability review;
* mowability rows preserve provisional score and caveat;
* review HTML can be generated without external assets or live network access;
* full package, docs, and Vancouver artifact validators still pass.
