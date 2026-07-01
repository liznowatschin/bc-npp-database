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

## Deferred To P3

P3 should create the package-backed canonical table model and deterministic
import/export workflow.
