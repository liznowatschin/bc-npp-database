# Ecosystem Integration Hooks

Date: 2026-07-01

## Purpose

BC-NPPD should use sibling UBC-FRESH projects as optional integration surfaces
when they improve reproducibility, source traceability, or ecosystem context.
These hooks are planning contracts, not core runtime dependencies.

## Dependency Policy

The core package should not depend on `freshforge`, `femic`,
`fresh-hectaresbc`, or `figrecover` during the foundation phases. Future
implementation may add optional extras such as `.[workflow]`, `.[bcdc]`,
`.[hectaresbc]`, or `.[figrecover]` after a small proof of concept validates
the boundary.

Prefer adapter modules and example workflow records before tight imports. This
keeps the database usable from a clean checkout and prevents public data
acquisition tools from becoming required for species validation.

## FreshForge Workflow Direction

FreshForge is the preferred orchestration model for reproducible BC-NPPD
processing once workflows need multiple auditable steps. BC-NPPD-owned nodes
should use provider id `bc_npp_database`.

Planned node families:

* P2 source nodes: `source.resolve`, `source.materialize_manifest`,
  `source.validate_attribution`.
* P3 pipeline nodes: `workbook.inventory`, `workbook.import_tables`,
  `tables.export`.
* P4 scoring nodes: `score.prepare_inputs`, `score.calculate`,
  `score.report`.
* Optional context nodes: `bcdc.resolve`, `bcdc.fetch_aoi`,
  `hectares.search`, `hectares.resolve`, `hectares.fetch`.
* Optional media nodes: `media.render_pdf_pages`,
  `media.discover_figure_candidates`, `media.crop_candidates`,
  `media.extract_calibrated_series`, `media.qa_bundle`,
  `media.export_accepted_tables`.

Workflow outputs should include FreshForge run summaries and provider-owned
diagnostics. Generated artifacts should stay under ignored `outputs/`, `local/`,
or another explicitly ignored run directory unless a later review approves a
public-safe derivative.

## FEMIC BC Data Catalogue Hooks

FEMIC includes useful BC Data Catalogue resolution and materialization patterns
that can inform BC-NPPD source workflows. Candidate hook concepts include:

* resolve a query or warehouse object name to BC Data Catalogue package and
  resource candidates;
* preserve package IDs, dataset page URLs, resource IDs, resource formats,
  access methods, and licence titles in a materialization manifest;
* classify resources as direct data downloads, service/API resources, indirect
  custom downloads, supporting documents, or unknown;
* materialize WFS-capable OpenMaps resources through AOI-scoped fetches when a
  future workflow explicitly allows it;
* record DWDS order and follow-up state when WFS or direct download is not the
  appropriate path.

BC-NPPD should treat these as optional public-data acquisition helpers. Raw
downloads remain ignored under `data/raw/`, `local/`, or `outputs/`. Tracked
records should be reviewed manifests, source summaries, or derived planning
notes only.

## fresh-hectaresbc Hooks

fresh-hectaresbc can provide optional BC-wide 1-ha raster context through its
catalog and retrieval facade. Candidate hook concepts include:

* search the recovered catalog for BEC, climate, topography, hydrology,
  administrative, species, or ecosystem context layers;
* resolve catalog records to local paths and content status without fetching;
* fetch selected rasters only in explicit, ignored local workflows;
* summarize candidate context for a species, source document, or study area
  without converting the context into unsupported ecological claims.

HectaresBC layers may help identify candidate ecosystem context, review
priorities, or diagnostic questions. They should not create species facts,
source confidence, or score values unless a later evidence rule defines exactly
how that layer supports the claim.

## figrecover Hooks

figrecover can provide optional media-derived evidence recovery when source
values are published only inside figures, tables, PDFs, image files, or similar
media. Candidate hook concepts include:

* render selected PDF pages to ignored local page images;
* record figure candidate manifests with page numbers, bounding boxes,
  candidate source, confidence, and available captions;
* crop candidate figures into image artifacts for calibrated review;
* run deterministic calibrated extraction for supported chart types;
* generate QA overlays, quality metrics, review manifests, and diagnostics;
* export only accepted or manually corrected recovered tables for downstream
  source-attribution review.

BC-NPPD should consume reviewed figrecover outputs as candidate source evidence,
not direct canonical species facts. Preferred inputs are generic long-table
exports with JSON sidecars that preserve source document, figure, calibration,
toolchain, diagnostics, QA, and review metadata.

VLM-derived proposals may help identify chart type, labels, legends, colours,
or calibration hints. They are review aids only. Numeric values should not be
treated as evidence unless they come from deterministic calibration or explicit
human correction and have an accepted review status.

Source PDFs, rendered pages, image crops, VLM prompts and responses, overlays,
review bundles, and recovered private tables must stay under ignored `local/`,
`tmp/`, `outputs/`, or `data/raw/` paths unless explicitly sanitized and
approved for public release.

## Evidence And Public Hygiene Rules

External data integrations must preserve BC-NPPD's evidence standard:

* do not invent ecological values from spatial context;
* do not treat recovered figure or table values as authoritative without review;
* distinguish source resolution, materialization, attribution, and review;
* keep excluded-source checks active across source fields, manifests, workflow
  parameters, and generated summaries;
* keep raw PDFs, screenshots, rendered pages, image crops, VLM logs, unchecked
  downloads, recovered private tables, and bulk GIS/raster outputs out of git;
* track only public-safe manifests, inventories, planning notes, and reviewed
  derivatives.

## Phase Placement

P2 should define the source and manifest records needed to cite external
materials, including review-gated media extraction manifests. P3 can add
deterministic workflow examples for workbook-to-table, source-manifest, and
accepted recovered-table joins. P4 can add scoring workflow records after
evidence-aware score inputs exist. P5 should include documented hooks and
optional dry-run examples, not live GIS/raster ingestion or media extraction.

A later P6 candidate should cover external ecosystem context adapters if the
project needs live BCDC, HectaresBC, or figrecover acquisition after the
v1.0.0a foundation.
