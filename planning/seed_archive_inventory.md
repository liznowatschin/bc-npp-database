# Seed Archive Inventory

Date: 2026-07-01

## Purpose

This note records the public-safe inventory of the two seed archives used to
launch BC-NPPD. The archives are provenance inputs, not tracked source-of-truth
data. Extracted archive contents must stay under ignored local paths unless a
future task explicitly approves a cleaned derivative for tracking.

## Local Extraction

The archives were extracted to ignored local working paths:

* `local/seed/BC-NPPD_v1.0.0a_project_bundle/`
* `local/seed/native-plant-restoration-database_repo_bundle/`

The repository `.gitignore` keeps `local/` ignored.

## Archive: `BC-NPPD_v1.0.0a_project_bundle.zip`

Disposition:

* Public-safe docs from this archive were cleaned into tracked Sphinx docs during
  P0.
* `schemas/master_species_columns.csv` and `schemas/lookups_seed.csv` are
  tracked as seed schema inputs.
* Raw PDF and screenshot source artifacts stay ignored pending source/license
  review.
* Workbook templates remain seed/provenance inputs until a future task approves
  a derivative.

Important contents:

* Project brief, foundation plan, data standards, source-priority notes,
  flagship species list, and coding-agent notes.
* Seed schema and lookup CSV files.
* Raw PDF and screenshot source artifacts.
* Two workbook/template files: `Wildflower_Mix_Table.xlsx` and
  `Plant_Table_Template.xlsx`.

## Archive: `native-plant-restoration-database_repo_bundle.zip`

Disposition:

* Workbook snapshots `v1.0.0a`, `v1.0.0b`, and `v1.0.0c` are tracked under
  `data/workbooks/` for traceability.
* The older package code was used as implementation seed material during P0 and
  should not be copied forward under its old package identity.
* Restoration-first wording is provenance only; BC-NPPD remains the canonical
  project identity.

Important contents:

* Latest workbook snapshot `native_plant_restoration_workbook_v1.0.0c.xlsx`.
* Older workbook snapshots for traceability.
* Source policy and coding-agent brief.
* Minimal legacy validators now superseded by `bc_npp_database`.

## Public Hygiene Rules

* Do not track extracted archive directories.
* Do not track raw PDFs, screenshots, unpublished source artifacts, or generated
  local exports.
* Track cleaned planning notes, docs, tests, schemas, and public-safe derived
  artifacts only.
