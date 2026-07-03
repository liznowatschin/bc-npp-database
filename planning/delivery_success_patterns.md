# Delivery Success Patterns

This note captures what made the P19-P20 Satinflower provider workflow land
cleanly and turn into a working product loop instead of staying as scaffolding.
It is based on the recent conversation, `ROADMAP.md`, `CHANGE_LOG.md`, PR #114,
PR #117, parent issues #109 and #115, and child issues #113 and #116.

## Trigger

The working product loop emerged from a concrete user need:

* "run this thing and see if it works";
* use the real Satinflower seed collection entrypoint;
* show the full catch so an expert can approve or reject it;
* surface missing product-page details when the first review showed they were
  absent;
* make the review UI fast enough to approve many rows without hand-editing CSV.

The important move was not treating these as vague feature requests. Each one
became a bounded workflow gap with a visible acceptance test.

## What Worked

### We Separated Discovery, Review, And Promotion

The provider workflow succeeded because it kept three layers distinct:

* scrape and normalize provider observations into ignored sandbox outputs;
* let a human inspect and approve those observations in a static review app;
* validate and apply an exported approval manifest into a preview or tracked
  product layer.

That boundary made live scraping safe. Raw fetched material stayed in ignored
`local/` and generated review products stayed in ignored `outputs/`, while the
durable product input became the approval manifest.

### We Used A Real Provider Entrypoint Early

The Satinflower seed collection URL forced the code to deal with a real
catalogue shape. The first pass caught 115 candidate species, 345 attribute
rows, and 115 supplier rows. That was enough signal to prove the source sweep
was useful, but also enough friction to reveal the missing product-page
`Plant Details` and `Seed Details` extraction.

Synthetic fixtures kept CI stable, but the real local run told us whether the
workflow caught the right material.

### We Designed For Expert Judgment Instead Of Pretending Automation Was Enough

The static approval app worked because it was species-first and review-first.
It showed PoC matches, new candidates, provenance, candidate attributes,
supplier rows, taxonomy flags, source flags, and exported a manifest instead of
mutating repo data directly.

The later batch controls were a natural extension of the same design: help the
expert make repeated decisions quickly, but preserve the exported manifest as
the auditable artifact.

### We Kept The CLI Thin And The Files Inspectable

The successful commands were understandable and repeatable:

```bash
bc-nppd scrape-provider-sandbox PROV-SATIN \
  --database-instance vancouver \
  --live-fetch \
  --source-sweep \
  --catalog-url https://satinflower.ca/collections/seed \
  --max-pages 5 \
  --raw-dir local/provider_raw \
  --out-dir outputs/provider_sandbox_source_sweep/PROV-SATIN \
  --json

bc-nppd build-provider-approval-review \
  outputs/provider_sandbox_source_sweep/PROV-SATIN \
  --poc-dir data/poc/vancouver \
  --out-dir outputs/provider_approval_review/PROV-SATIN \
  --reviewer "expert reviewer" \
  --json
```

Each command produced plain CSV, JSON, or HTML that could be opened directly.
That made failures easy to inspect and successes easy to trust.

### We Made Counts Part Of The Definition Of Done

The roadmap, issues, PRs, and closeout comments recorded concrete counts:

* P19 first sweep: 115 species, 345 attributes, 115 supplier rows, 0 mowability
  rows, 17 existing PoC matches, 98 new candidates.
* P20 detail extraction: 115 species, 2,086 attributes, 115 supplier rows, 0
  mowability rows, 2,316 draft approval rows.

Those counts made the product change legible. They also made regressions easy
to spot.

### We Let User Testing Steer The Next Slice

The best follow-up work came from opening the generated HTML and asking what
was missing:

* The first source sweep showed only title/type/tag attributes.
* A manually inspected Satinflower page showed `Plant Details` and
  `Seed Details`.
* P20 added body HTML parsing and regenerated the same review surface.
* The batch-review request came after the approval UI worked but repetitive
  approval was too slow.

This is a strong pattern: get to a tangible interface quickly, then let real
review pain define the next task.

### We Closed With The UBC-FRESH Ledger

The work did not become trustworthy only because the app looked good. It became
trustworthy because each phase closed through:

* roadmap issue numbers and task checklists;
* PR descriptions with hygiene boundaries;
* local acceptance commands;
* CI and docs verification;
* GitHub issue closeout comments;
* changelog and roadmap updates.

That made the success reproducible by another agent or collaborator.

## Repeatable Dunk Pattern

Use this pattern for future high-leverage product work:

1. Start from a concrete user-facing outcome.
2. Name the exact real-world input or entrypoint.
3. Keep raw acquisition, normalized sandbox, human review, and product
   promotion as separate artifacts.
4. Build the smallest inspectable interface that lets the expert evaluate the
   output.
5. Export a durable manifest instead of letting the browser or scraper mutate
   tracked product data directly.
6. Validate the manifest before applying it.
7. Apply first to ignored preview outputs.
8. Record counts before and after each major transformation.
9. Use user testing to identify the next missing layer.
10. Close the phase through roadmap, issues, PR, CI, docs, and changelog.

## Product Loop Template

For provider-style workflows, the preferred loop is:

```text
real provider entrypoint
  -> ignored raw fetch cache
  -> normalized sandbox CSVs
  -> static review bundle
  -> expert approval manifest
  -> manifest validation
  -> ignored applied preview
  -> optional tracked reviewed input
  -> regenerated tracked product artifacts
```

The same shape can be reused for PDF/media extraction, GIS context, raster
context, and other evidence-adapter workflows.

## Guardrails To Preserve

* Do not track raw provider HTML, scrape caches, screenshots, or generated
  review bundles.
* Do not import scraped observations directly as facts.
* Keep provider-derived ecological values `pending_review` until reviewed.
* Keep supplier availability separate from plant identity.
* Keep mowability provisional and blocked from UNI, PSI, and RVI readiness until
  a later scoring review explicitly changes that rule.
* Prefer static, dependency-light review surfaces before adding servers or
  databases.
* Keep every "this worked" claim attached to a command, count, file, issue, or
  PR.

## Anti-Patterns To Avoid

* Jumping from scrape output directly into tracked PoC data.
* Letting generated HTML be the only durable record of a review decision.
* Treating provider descriptions as reviewed native-status or ecological-score
  evidence by default.
* Building a general scraper before proving one provider-specific path works.
* Calling a phase complete because the interface looks good, without validation
  and closeout evidence.
* Hiding generated-output counts from roadmap and issue closeout comments.

## Next Places To Apply This

* Promote the reviewed Satinflower manifest into a tracked reviewed-input path
  after intentional expert approval.
* Repeat the provider source-sweep loop for Premier Pacific, Northwest
  Meadowscapes, and West Coast Seeds.
* Add provider-specific overlays only after the base loop continues to validate.
* Use the same sandbox-review-approval pattern for future figrecover, LMH77,
  BCDC, HectaresBC, or FreshForge adapter outputs.
