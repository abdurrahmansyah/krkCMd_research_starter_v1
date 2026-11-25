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

## D-005 — Model Registry and Compatibility Assessment (2026-11-25)
- Status: EXPLORATORY (M01 COMPLETE; AWAITING IMPLEMENTATION APPROVAL)
- Context: Evaluated 32 candidate models across 6 paradigms for potential extension of Idea 1 (benchmark) and Idea 2 (robustness).
- Outcome: 8 models passed L0/L1 smoke testing in existing .venv; 12 static reviews completed; 7 conditional constraints identified; 5 custom designs cataloged.
- Strict Constraint: No model is approved for new experimental training until resource budgets, environment plans, and selection criteria receive explicit user authorization. Previous decisions D-001 through D-004 remain fully in force.

## D-006 — New Workstation Migration & Reproduction Environment Governance (2026-11-25)
- Status: PROPOSED (ADMINISTRATIVE; M01-R MIGRATION & M00 REPRODUCTION VERIFIED)
- Context: Project migrated to workstation `DESKTOP-CQB09OU` (Intel Core i9-10900KF, 127.92 GB RAM, Quadro RTX 6000 24 GB VRAM, 1,752.80 GB free C:).
- Administrative Record:
  - Python 3.11.9 (64-bit) installed with researcher authorization; copied `.venv` preserved as `.venv_old_pc_backup`; clean `.venv` rebuilt with exact historical package pins (`reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/requirements_baseline_new_pc.freeze.txt`).
  - Dedicated Jupyter kernel registered as `krkcmd-research-newpc` (`Python (krkCMd Research - New PC)`).
  - M00 baseline notebook reproduced identically in isolated workspace (`max_abs_diff <= 2.27e-13` µm across all 3,822 test predictions).
  - Updated environment budget proposal recorded in `reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/MODEL_ENVIRONMENT_PLAN_NEW_PC.md`.
- Strict Constraint: D-001 through D-004 and exploratory D-005 remain unmodified. No M01.1 edits, M02 environment installations, L2 tests, or new model training are authorized without separate researcher approval.
