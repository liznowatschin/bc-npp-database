# Vancouver Pollinator Module

This directory contains the pollinator evidence-review scaffold for the
Vancouver Plant List PoC.

The module does not contain reviewed plant-pollinator claims and does not
calculate a Pollinator Support Index. It makes the current review queue
explicit so future source review can fill accepted, source-attributed
pollinator fields.

## Files

- `pollinator_review.csv`: one row per Vancouver PoC species queued for
  pollinator evidence review.
- `pollinator_evidence_gaps.csv`: species-by-field evidence gaps for bloom
  period, floral resources, native bee support, butterfly support,
  hummingbird support, specialist relationships, and larval host use.
- `pollinator_source_requirements.csv`: source tier and review-status
  requirements for each pollinator field.
- `manifest.json`: provenance, row counts, PSI policy, and public-hygiene
  flags.
- `diagnostics.csv`: non-error caveats recorded when the artifact was
  generated.

## CLI

Regenerate the module:

```shell
bc-nppd generate-vancouver-pollinator-module data/poc/vancouver/usability --out-dir data/poc/vancouver/pollinator_module --json
```

Validate the tracked artifact:

```shell
bc-nppd validate-vancouver-pollinator-module data/poc/vancouver/pollinator_module --json
```

## Evidence Boundary

Rows with `review_status` values of `review_queue` or `needs_review` are not
accepted claims. PSI remains `not_ready` until accepted field-level pollinator
evidence exists and can be converted into reviewed score inputs.
