# Mowability Score Ideas

Date: 2026-07-03

## Purpose

BC-NPPD needs a candidate "mowability" signal for lawn-compatible native or
near-lawn plantings. This score should help reviewers compare provider claims,
not make final recommendations automatically.

Mowability is separate from UNI, PSI, and RVI. It should not affect score
readiness until later review creates explicit, accepted score-input rows.

## Candidate Scale

Use a provisional 0-5 candidate score in provider sandbox outputs:

* 0: not mowable or inappropriate for mowing.
* 1: very low tolerance; mowing likely damages persistence or ecological use.
* 2: occasional high cut only; not suitable for regular lawn-like use.
* 3: moderate; establishment-period, seasonal, or infrequent high mowing may be
  acceptable.
* 4: lawn-compatible with limits; can tolerate repeated mowing under stated
  height/frequency constraints.
* 5: strong lawn or repeated-mowing candidate.

`Unknown` or blank should be used when provider text does not support a score.

## Evidence Cues

Potential positive cues:

* provider labels the species or mix as lawn, eco-lawn, lawn replacement,
  pathway, low-growing, traffic-tolerant, or mowable;
* provider gives explicit mowing height, mowing frequency, or establishment
  mowing guidance;
* species is described as low, creeping, stoloniferous, rhizomatous, mat-forming,
  or persistent under cutting.

Potential negative cues:

* provider warns not to mow, cut, or traffic the planting;
* species is tall, meadow-only, fragile, strongly flowering-stem dependent, or
  intended for habitat where mowing removes ecological value;
* mowing is described only as a one-time establishment or annual cleanup action.

## Provider Sandbox Rules

P16 should treat mowability as an observation, not a plant fact. Provider
adapters may emit `mowability.csv` rows with:

* provider ID;
* botanical name;
* provisional score;
* source URL;
* evidence text or notes where available;
* review status;
* caveat that the score is candidate-only.

Rows with inferred scores should be marked `pending_review`. If a provider page
only contains weak cues, prefer a note with blank score over false precision.

## Review Boundary

P17 may import approved mowability observations into a tracked Vancouver
supplier/mowability artifact, but approval should not make the value reviewed
for UNI, PSI, or RVI. P18 may display mowability in the web app only with clear
candidate/provisional labeling and source provenance.

Open review questions:

* Whether score 5 should be reserved for species-level claims, or whether
  provider mix-level claims can qualify.
* Whether mowability should account for ecological tradeoffs, such as mowing
  reducing bloom and pollinator resources.
* Whether mowing height/frequency should become normalized fields in P17.
