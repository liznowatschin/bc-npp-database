# LMH77 Extraction Plan

Date: 2026-07-01

## Purpose

Plan how BC-NPPD can query and extract relevant information from `LMH77.pdf`
without tracking the source PDF or treating document-derived values as reviewed
database facts too early.

The local PDF currently lives at `tmp/LMH77.pdf`. That path is ignored and
should remain untracked.

## Source Snapshot

Local inspection with PyMuPDF found:

* File size: 33,703,003 bytes.
* Page count: 722 pages.
* PDF outline entries: 238.
* Text extraction: born-digital and generally extractable.
* Title: `A Field Guide to Ecosystem Classification and Identification for
  Coastal British Columbia (excluding Haida Gwaii)`.
* Authors: Heather Klassen, Del Meidinger, William H. MacKenzie, Bob Green,
  Allen Banner, and Sari C. Saunders.
* Creation date: 2026-03-10.
* Modification date: 2026-03-13.

The extracted citation page identifies the work as:

Klassen, H., D. Meidinger, W.H. MacKenzie, B. Green, A. Banner, and S.C.
Saunders. 2026. A field guide to ecosystem classification and identification
for coastal British Columbia (excluding Haida Gwaii). Province of British
Columbia, Victoria, B.C. Land Management Handbook 77.

## Relevant Structure

The PDF outline and text scan show a document structure that is useful for
BC-NPPD:

* introductory material and guide-use instructions;
* biogeoclimatic ecosystem classification background;
* BGC unit sections, including CDF, CWH, MH, and related coastal units;
* forested site units beginning around Chapter 6;
* non-forested and related unit content after the forested site-unit section;
* vegetation tables and site-unit descriptions with common and scientific plant
  names.

Representative outline anchors found locally include:

* Chapter 1, `Introduction`, page 17.
* Chapter 2, `Biogeoclimatic Ecosystem Classification`, page 25.
* Chapter 3, `How to Use the Field Guide`, page 37.
* Chapter 4, `The Environment of Coastal British Columbia`, page 61.
* Chapter 6, `Forested Site Units of Coastal British Columbia`, page 215.
* BGC/site-unit anchors such as `CWHdm1`, `CWHdm2`, `CWHdm3`, `CWHds1`,
  `CWHmm1`, `CWHvm1`, `CWHws1`, `CWHxs`, `IDFww`, `MHmm1`, `MHmm2`, `MHms`,
  and `MHvh`.

## Initial Term Findings

The local scan found these term hits:

* `Achillea`: pages 632, 645, 650, 658.
* `millefolium`: pages 632, 645, 650, 658.
* `yarrow`: pages 630, 632, 643, 644, 645, 650, 656, 658.
* `indicator species`: pages 58, 210, 224, 495, 544, 555, 556, 566, 573, 583,
  594, 596, 597, 608.
* `site series`: 191 pages.
* `vegetation`: 190 pages.
* `CDF`: 56 pages.
* `CWH`: 450 pages.

The `Achillea millefolium` and yarrow hits appear in estuarine, beachland,
rocky headland, and grassland contexts, including vegetation tables and unit
descriptions. These are promising candidate evidence leads for the planned
`Achillea millefolium` foundation record, but they remain unreviewed until P2
source-attribution rules and reviewer acceptance exist.

## Planned Query And Extraction Direction

LMH77 should be treated as a source-document workflow, not as a raw data import.
The first implementation should:

* add an optional PDF dependency group such as `.[pdf]`, likely backed by
  PyMuPDF;
* keep PDF parsing optional and out of core imports;
* build a local page-text and outline index under ignored paths such as
  `local/index/lmh77.sqlite`, `local/index/lmh77.jsonl`, or `outputs/lmh77/`;
* support query by species name, common name, BGC unit, site unit, page range,
  outline anchor, and ecological keyword;
* return source snippets with page number, outline context, match term, and
  extraction method;
* emit candidate source-attribution records only after review.

Possible future CLI surfaces:

* `bc-nppd source index-pdf tmp/LMH77.pdf --source-id LMH77`
* `bc-nppd source query LMH77 "Achillea millefolium"`
* `bc-nppd source query LMH77 "common yarrow CDF"`
* `bc-nppd source extract-lmh77-units --source-id LMH77`
* `bc-nppd source review-extractions PATH`

Possible future FreshForge nodes:

* `source.index_pdf`
* `source.query_index`
* `source.extract_pdf_passages`
* `source.extract_lmh77_units`
* `source.review_extractions`

## Data And Evidence Rules

LMH77-derived outputs should become candidate source-attribution records, not
direct canonical species facts. Each extracted claim should preserve:

* source ID and full citation;
* local or public source path/URL when approved;
* PDF page number and outline heading;
* table, figure, or section label when detectable;
* matched species/common name and normalized target taxon;
* extracted snippet or table row;
* extraction method and tool version;
* review status and reviewer notes;
* evidence confidence separate from review status.

Values extracted from plain born-digital text may use PyMuPDF directly. Values
locked inside images, charts, or visually complex tables should follow the
review-gated figrecover pathway described in
`planning/ecosystem_integration_hooks.md`.

Unknown values should remain unknown. LMH77 should not be used to invent
pollinator, urban tolerance, restoration, or scoring values that the guide does
not explicitly support.

## Public Hygiene

Do not track:

* `tmp/LMH77.pdf`;
* rendered pages;
* full extracted text dumps;
* page images, crops, screenshots, or overlays;
* local search indexes;
* unreviewed extraction tables.

Track only public-safe planning notes, synthetic fixtures, schemas, reviewed
source manifests, or short source summaries approved by the source policy.

## Deferred Implementation

P2 should define the source-document and extraction-manifest records that can
represent LMH77 evidence. P3 can implement an optional PDF index/query API and
accepted extraction imports. P4 should reject unreviewed LMH77-derived values
from score inputs. P5 may use reviewed LMH77 passages as supporting evidence
for the `Achillea millefolium` foundation record if the reviewed claims are
appropriate.
