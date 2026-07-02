# Source Attribution Model

Date: 2026-07-01

## Direction

BC-NPPD should separate ecological values from evidence confidence and source
attribution. A strong score without strong evidence should remain visibly
uncertain.

## Minimum Future Record Concepts

* Reference ID
* Source name
* Source tier
* URL or citation
* Field or claim supported
* Species ID
* Evidence confidence
* Notes and limitations
* External source IDs where available
* Materialization manifest path or URI where a public-safe manifest exists
* Acquisition or resolution status for derived source artifacts
* Media-derived extraction provenance where a figure, table, or image supplies
  a candidate value

## Source Tiers

* Tier 1: peer-reviewed literature.
* Tier 2: government, academic, herbarium, and technical sources.
* Tier 3: regional practitioner sources such as Satinflower Nurseries.

## Excluded Source

The City of Vancouver Green Rainwater Infrastructure Planting Guidelines PDF is
excluded. The exclusion applies to citations, source-attribution fields, scoring
rationale, species notes, and documentation.

## External Source Manifests

P2 should make room for public-data materialization records without requiring
live downloads in normal validation. Future source records may reference:

* BC Data Catalogue package IDs, dataset page URLs, resource IDs, formats,
  licence titles, and resource classifications.
* WFS, direct-download, indirect custom-download, or DWDS acquisition state.
* FreshForge workflow IDs, run namespaces, run summaries, provider diagnostics,
  and artifact manifest paths.
* HectaresBC dataset IDs, catalog family, title candidates, source ZIP paths,
  content status, and retrieval diagnostics.
* figrecover source document IDs, page numbers, figure or table IDs, crop or
  image IDs, extraction method, calibration settings, tool and version, QA
  metrics, review status, reviewer notes, accepted-table paths, and extraction
  diagnostics.

These records support provenance and review. They do not, by themselves, make an
ecological claim true or score-ready.

## Media-Derived Evidence Boundary

When a value is recovered from a figure, table, PDF, image, or other media,
BC-NPPD should keep two provenance layers separate:

* the original document citation that supports why the source is relevant;
* the recovered-data artifact provenance that explains how a candidate value was
  extracted, calibrated, reviewed, corrected, and exported.

Only reviewed recovered rows should become candidate source-attribution records.
Unreviewed, rejected, or VLM-only numeric proposals should remain local review
artifacts and must not become canonical species facts or score inputs.

## Implemented Source And Hardening Layers

P2 implemented durable source/reference dataclasses, source completeness checks,
reference ID conventions, source-attribution validation behavior, and optional
source materialization and media-derived extraction manifest contracts in
`src/bc_npp_database/sources.py`.

P7 adds a field-level hardening pattern for the Vancouver PoC list in
`src/bc_npp_database/evidence_hardening.py`. The P7 layer can mark
identity/native-range display fields as `poc_reviewed` where Tier 1/2
taxonomy/native-range attribution exists. It also records explicit evidence
gaps for horticultural, use-case, and score-related fields.

Future review work should consume P7 reviewed-field and evidence-gap artifacts
instead of promoting values directly from the workbook or from external context.
