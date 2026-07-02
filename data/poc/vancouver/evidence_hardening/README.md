# Vancouver Evidence Hardening

This directory contains the Phase 7 evidence-hardening layer for the Vancouver
plant list proof of concept.

The source product remains `data/poc/vancouver/plant_list.csv`. These files add
field-level evidence status and score-readiness boundaries without changing the
original PoC rows.

## Files

- `hardened_plant_list.csv`: the 52 PoC species with P7 hardening status,
  reviewed-field counts, evidence-gap counts, and score-readiness flags.
- `reviewed_sources.csv`: P7 source review status for the source registry.
- `reviewed_fields.csv`: field-level rows that are PoC-reviewed for
  identity/native-range use.
- `evidence_gap_report.csv`: fields that still need field-specific review
  before promotion.
- `score_readiness.csv`: UNI, PSI, and RVI readiness rows. All rows are
  `not_ready` in P7.
- `manifest.json`: row counts, caveats, score policy, and public-hygiene flags.
- `diagnostics.csv`: non-error caveats for the hardening layer.

## Boundary

P7 marks only identity/native-range display fields as PoC-reviewed where Tier
1/2 taxonomy/native-range attribution exists. Horticultural, use-case, and
score-related values remain candidate values until future review adds explicit
field-level attribution.

The score-readiness report deliberately keeps UNI, PSI, and RVI as `not_ready`.
Workbook suitability/toughness values are useful triage clues, but they are not
accepted P4 score inputs.

## CLI

Regenerate the hardening layer:

```shell
bc-nppd harden-vancouver-evidence data/poc/vancouver --out-dir data/poc/vancouver/evidence_hardening --json
```

Validate it:

```shell
bc-nppd validate-vancouver-evidence data/poc/vancouver/evidence_hardening --json
```
