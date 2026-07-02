# v1.0.0a Foundation Scope

Date: 2026-07-01

## Goal

The v1.0.0a foundation should provide a reviewed schema direction, source and
evidence model, scoring framework direction, and one gold-standard species
record.

## First Gold-Standard Record

The planned first species is `Achillea millefolium`. It is common, well studied,
widely available, urban tolerant, drought tolerant, pollinator-supportive, and
useful as a template for later species records.

## Release Boundary

The v1.0.0a release should not imply that BC-NPPD has scaled to 50-60 species or
that all candidate workbook values are verified. Candidate records remain draft
until source-attribution and review are complete.

The foundation can include documented integration hooks and dry-run workflow
examples, but it should not require live BC Data Catalogue downloads,
fresh-hectaresbc raster retrieval, or bulk GIS materialization. External context
adapters remain optional until a later phase approves reviewed source and score
rules for their use.

## P5 Implementation Direction

P5 prepares a foundation-ready scaffold rather than publishing a tag. The
tracked artifacts should include:

* a schema-freeze manifest;
* one `Achillea millefolium` species row;
* source and source-attribution sidecars;
* score-input sidecars that exercise P4 without asserting ecological scores;
* a release checklist and dry-run workflow example.

The foundation validator should ensure required files exist, source and score
sidecars satisfy the package validators, species IDs and source IDs link across
files, and public-hygiene flags remain false for raw sources, generated outputs,
external-download requirements, and private data.
