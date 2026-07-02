# Workbook Normalization Contract

Date: 2026-07-01

## Purpose

P1 defines the workbook normalization contract before bulk data export. The goal
is to make workbook contents inspectable, auditable, and ready for later
canonical table conversion without treating hand-edited spreadsheets as the only
source of truth.

## Current Workbook Source

The latest tracked workbook snapshot is:

* `data/workbooks/native_plant_restoration_workbook_v1.0.0c.xlsx`

It contains these relevant sheets:

* `Species_Master`
* `Lookup_Tables`
* `Reference_Policy`
* `Source_Attribution`
* `Bloom_Calendar`
* `Dashboard`
* `QA_Log`

## Canonical Table Direction

* `Species_Master` becomes the candidate species table.
* `Lookup_Tables` becomes controlled vocabulary records.
* `Reference_Policy` becomes source policy documentation and future reference
  configuration.
* `Source_Attribution` becomes field/source attribution records.
* `Bloom_Calendar` becomes derived or validated bloom-month records.
* `Dashboard` remains an output/report concept, not canonical source data.
* `QA_Log` becomes review queue or issue provenance, not species data.

## Naming Direction

BC-NPPD should use stable IDs in the `BCNPPD-0001` style. Legacy IDs such as
`CDF-0001` should be preserved as legacy identifiers or migration notes, not
silently rewritten in place.

## Unknowns And Blanks

Use `Unknown` where a relevant value is unresolved. Leave cells blank only when
the field is intentionally not applicable or intentionally unpopulated.

## P3 Canonical Import Boundary

P3 may import approved workbook sheets into package-backed canonical records and
write deterministic CSV exports to ignored local output directories. Those CSV
exports remain review artifacts until a later release task explicitly approves a
tracked derivative.

P3 must not infer missing ecological values, calculate scores, or treat
source-attribution rows as facts by import alone. Source-attribution rows pass
through the P2 validator and remain evidence records for later review.

## P6 PoC Product Boundary

P6 may promote the 20 tracked workbook candidates into a caveated Vancouver PoC
artifact when it also migrates legacy IDs, creates deterministic source IDs,
preserves source-attribution links, and labels the output as a PoC candidate
list. The artifact is useful for inspection and prioritization, but not a final
planting recommendation list.
