# Canonical Schema Direction

Date: 2026-07-01

## Purpose

The P0 seed schema and P1 workbook inventory should converge into a canonical
schema that supports BC-NPPD's broader native plant and pollinator database
scope.

## Schema Inputs

* `schemas/master_species_columns.csv`
* `schemas/lookups_seed.csv`
* Latest tracked workbook snapshot
* Source attribution and evidence policy docs

## Direction

The canonical schema should prefer stable field names, controlled vocabularies,
explicit uncertainty, and source-attribution hooks. Dashboard fields and
workbook-specific visual scaffolds should not become core source tables unless
they encode durable data.

## Workflow Contract Direction

P3 should be able to express workbook-to-table normalization as an optional
FreshForge workflow after the table contracts exist. The first workflow contract
should stay small: inspect workbook, import approved sheets, join reviewed
source/manifests where present, validate canonical rows, and export
deterministic tables under ignored `outputs/` unless a release task approves
tracked derivatives.

Source-manifest joins should preserve external identifiers and acquisition
status without requiring live BC Data Catalogue, FEMIC, or HectaresBC access in
CI.

## P3 Implementation Direction

P3 creates the package-backed canonical table model, deterministic import/export
workflow, and optional workflow shape for source-manifest joins. The
implementation should treat workbook rows as candidate records, preserve source
attribution through P2 validators, and write generated CSV outputs only to
caller-provided ignored directories such as `outputs/`.

The first canonical implementation should include:

* schema helpers for `schemas/master_species_columns.csv` and
  `schemas/lookups_seed.csv`;
* alias-aware workbook headers such as `Species_ID` to `Species ID`;
* candidate species, lookup, bloom-calendar, and source-attribution records;
* deterministic CSV export with stable filenames and column order;
* a planning-only FreshForge workflow shape without a runtime dependency.
