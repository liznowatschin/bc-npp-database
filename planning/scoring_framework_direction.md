# Scoring Framework Direction

Date: 2026-07-01

## Purpose

BC-NPPD expects three score families: Urban Native Index (UNI), Pollinator
Support Index (PSI), and Restoration Value Index (RVI).

## Principles

* Do not invent ecological values.
* Keep evidence confidence separate from score.
* Emit diagnostics where source support is missing or weak.
* Treat early weights as provisional until reviewed.
* Treat external GIS and raster context as diagnostic context until reviewed
  evidence rules define how it supports a score input.

## Workflow Hook Direction

P4 can use FreshForge workflow records for UNI, PSI, and RVI runs once the score
input records exist. Candidate nodes are `score.prepare_inputs`,
`score.calculate`, and `score.report`.

Optional BCDC or HectaresBC context may help flag ecosystem, climate,
topographic, or regional review questions. Those context layers must not create
score values directly. A score should be calculated only from reviewed inputs
with source attribution and evidence confidence.

## P4 Implementation Direction

P4 defines scoring records, provisional weighting policy, evidence-aware
diagnostics, CLI/reporting surfaces, and optional workflow records for
calculated provisional scores.

The implementation should include:

* UNI, PSI, and RVI score-family vocabulary;
* score input rows with species ID, metric, numeric 0-5 value, source ID,
  evidence confidence, review status, optional context/media/workflow IDs, and
  optional input-specific weights;
* provisional weight rows by score family and metric;
* a transparent weighted-average calculation normalized to 0-100;
* diagnostics for invalid IDs, invalid evidence confidence, missing weights,
  invalid numeric values, and unreviewed score inputs;
* CLI commands for validation and calculation using CSV, JSON, or JSON Lines.

External context remains provenance only. P4 must not infer score inputs from
GIS, raster, media, source text, workbook prose, or canonical species rows.
