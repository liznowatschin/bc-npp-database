Roadmap
=======

The authoritative roadmap lives in ``ROADMAP.md`` at the repository root.

Phase 0 establishes the public-safe project scaffold, package skeleton,
documentation, CI workflows, source policy checks, schema seeds, and traceable
legacy workbook snapshots.

Phase 1 completed the seed archive inventory and normalization-contract phase.
It inventoried ignored seed archives and workbook snapshots, defined the
normalization contract, added read-only workbook inspection helpers, and
expanded validation records.

Phase 2 defines source attribution, evidence records, source materialization
manifests, and review-gated media extraction manifests.

Phase 3 implements the canonical data pipeline: schema-backed species rows,
lookup rows, source-attribution validation, bloom-calendar import, deterministic
CSV export, and a dependency-free FreshForge workflow shape.

Phase 4 implements evidence-aware score records, provisional weighted
calculation, diagnostics, CLI reporting, and a dependency-free FreshForge
workflow shape for UNI, PSI, and RVI.

Phase 5 prepares the v1.0.0a foundation scaffold: schema freeze manifest, one
reviewed `Achillea millefolium` example record, source-attribution and
score-input sidecars, release checklist artifacts, and dry-run workflow shapes.

Phase 6 produced the first usable PoC artifact: a tracked, caveated
20-species Vancouver/CDF plant list with stable BC-NPPD IDs, source records,
source-attribution rows, validation diagnostics, and inspection docs.

Phase 7 hardens evidence for the Vancouver PoC list. It adds a tracked
field-level hardening layer with reviewed identity/native-range fields, evidence
gap reports, explicit score-readiness blocks, diagnostics, CLI validation, and
inspection docs.

Phase 8 adds a static usability layer for the Vancouver PoC list. It generates
self-contained inspection HTML, a display table, candidate use-case views,
view summaries, diagnostics, CLI validation, and docs while preserving P7
evidence caveats.

Phase 11 adds a pollinator evidence-review module. It materializes the
Vancouver PoC pollinator review queue as review rows, evidence gaps, source
requirements, diagnostics, and CLI validation while keeping PSI ``not_ready``.

Phase 12 expanded the tracked Vancouver PoC product to 52 species by
adding unreviewed user-submitted expansion candidates, recording a request
audit, and regenerating evidence-hardening, usability, and pollinator artifacts
without treating the request as ecological evidence.

Phase 13 adds ``Matricaria discoidea`` as an additional unreviewed
user-requested expansion candidate and regenerates the current PoC product to
53 species.

Phase 15 introduces the source-provider registry and provider sandbox
contracts for future supplier website scraping. P15 validates provider records,
Vancouver eligibility rules, supplier rows, and provisional mowability
observations without live scraping or PoC integration.
