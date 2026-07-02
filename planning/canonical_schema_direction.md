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

## Deferred To P3

P3 should create the package-backed canonical table model, deterministic
import/export workflow, and optional workflow records for source-manifest joins.
