# Research Decisions

## D-001 — Research sequence (2026-11-20)
- Status: APPROVED
- Decision: Start with Ide 1 (model benchmark) + Ide 2 (synthetic robustness); consider Ide 4 only if initial results justify it.
- Rationale: CPU-friendly, reproducible, uses existing public tabular dataset, and avoids waiting for 38.6 GB images archive.
- Consequence: Ide 4 is gated; no implementation before review.

## D-002 — Primary target and features (provisional; verify schema)
- Status: PROVISIONAL
- Target: MANwidth.
- Features: x1..x501.
- DLMwidth/AEDwidth are external baselines only, not model inputs.
- Consequence: Must validate exact CSV columns before modeling.

## D-003 — Grouping key (provisional; must verify)
- Status: PENDING VALIDATION
- Candidate group key: Series + Image + Grid, excluding Stage, to keep repeated location observations together across stages.
- Rationale: avoid leakage between repeated measurements across time stages.
- Consequence: Verify semantics from data descriptor/scripts before final split.
