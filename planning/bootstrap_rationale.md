# Bootstrap Rationale

Date: 2026-07-01

## Context

BC-NPPD was initialized from two legacy project bundles:

* `BC-NPPD_v1.0.0a_project_bundle.zip`, which established the renamed BC Native
  Plant & Pollinator Database identity, seed schema, lookup values, public-safe
  project brief, and initial flagship species list.
* `native-plant-restoration-database_repo_bundle.zip`, which contained an older
  restoration-oriented package scaffold, workbook snapshots, source policy, and
  minimal validators.

The bootstrap keeps the BC-NPPD identity as canonical and treats the older
restoration bundle as provenance and implementation seed material.

## Decisions

* Use `bc-npp-database` as the distribution name.
* Use `bc_npp_database` as the import package.
* Use `bc-nppd` as the CLI command.
* Track public-safe docs, seed schemas, and workbook snapshots.
* Keep raw PDFs, screenshots, private data, generated outputs, and local scratch
  ignored.
* Preserve the excluded-source policy for the City of Vancouver Green Rainwater
  Infrastructure Planting Guidelines PDF.
* Keep ecological claims evidence-backed and preserve `Unknown` values where
  evidence is incomplete.

## Deferred Work

* Full workbook normalization.
* Excel import/export automation.
* Scoring formula implementation.
* Source ingestion and bibliography records.
* First gold-standard species record.
