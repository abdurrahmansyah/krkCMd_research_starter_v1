# Research Decisions

## D-001 — Research sequence (2026-11-20)
- Status: APPROVED
- Decision: Start with Ide 1 (model benchmark) + Ide 2 (synthetic robustness); consider Ide 4 only if initial results justify it.
- Rationale: CPU-friendly, reproducible, uses existing public tabular dataset, and avoids waiting for 38.6 GB images archive.
- Consequence: Ide 4 is gated; no implementation before review.

## D-002 — Primary target and features (verified)
- Status: APPROVED (2026-11-23)
- Target: MANwidth (float, 19,098 non-null observations, min 0.0, max 813.59 um).
- Features: exactly x1..x501 (all 501 numeric, intensities [0, 255], 0 missing values).
- DLMwidth and AEDwidth are external comparison baselines only, never model predictors.
- Consequence: Feature and target contract locked for model training.

## D-003 — Grouping key validation (verified)
- Status: APPROVED (2026-11-23)
- Confirmed group key: `Series + Image + Gridline` (excluding Stage).
- Evidence: Exactly 3,183 unique groups across 19,098 rows. Every single group has exactly 6 observations corresponding strictly to Stage 1 through Stage 6 (3,183 * 6 = 19,098).
- Rationale: Fully eliminates data leakage across repeated self-healing stages for identical crack locations.
- Consequence: GroupShuffleSplit / GroupKFold on `Series + Image + Gridline` is strictly mandatory for all model benchmarks.

## D-004 — Schema correction: Gridline instead of Grid (2026-11-23)
- Status: APPROVED
- Decision: Rename metadata field reference from `Grid` to `Gridline` across all code, configs, and documentation.
- Rationale: The raw dataset `krkCMd_table.csv` officially names this column `Gridline`. The starter template had a typographical discrepancy using `Grid`.
- Consequence: Aligned `baseline.yaml`, `AGENT.md`, `00_baseline_krkCMd.ipynb`, and `audit_dataset.py`.
