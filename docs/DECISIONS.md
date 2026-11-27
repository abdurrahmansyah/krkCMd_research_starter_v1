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

## D-007 — M02A & M02B Isolated Environment Provisioning Governance (2026-11-25)
- Status: ADMINISTRATIVE (RECORDED; ZERO MODELS APPROVED FOR REAL TRAINING)
- Context: Provisioned `.venv-boost` (`krkcmd-boost`), `.venv-signal-cpu` (`krkcmd-signal-cpu`), `.venv-deep` (`krkcmd-deep`), `.venv-signal-tf` (`krkcmd-signal-tf`), and `.venv-signal-hydra` (`krkcmd-signal-hydra`) while preserving frozen `.venv` (`krkcmd-research-newpc`).
- Administrative Record:
  - Deprecated legacy hardcoded `scripts/check_model_compatibility.py` in favor of registry-driven `scripts/build_compatibility_matrix.py` reading `configs/model_registry.yaml`.
  - Enforced GiB-consistent subprocess watchdog in `scripts/resource_policy.py` (64 GiB RAM cap, 20 GiB VRAM cap, 16 GiB RAM reserve, 2.5 GiB VRAM reserve, log-file stdout/stderr, process-tree termination).
- Strict Constraint: D-001 through D-004 remain unchanged; 0/32 candidates are `APPROVED` for actual krkCMd experiments.

## D-008 — M02C Foundation Model & Deferred Recovery Governance (2026-11-26)
- Status: ADMINISTRATIVE (RECORDED; ZERO MODELS APPROVED FOR REAL TRAINING)
- Context: Provisioned `.venv-foundation` (`krkcmd-foundation`) and `.venv-tabr` (`krkcmd-tabr`); recovered `DL04`, `RF05` (with train-only zero-center + `pi2mi`), and `SG06` (`1,800s` cap) through L2C; validated `FM03` & `FM04` through L2B; recorded `FM01` & `FM02` as `BLOCKED_LICENSE` pending researcher PriorLabs license acceptance.
- Strict Constraint: D-001 through D-004 remain unchanged; 0/32 candidates are `APPROVED` for actual krkCMd experiments.

## D-009 — M03 Scientific Evaluation Protocol & Foundation Closure Governance (2026-11-26)
- Status: PROPOSED (AWAITING RESEARCHER APPROVAL FOR M04; ZERO REAL TRAINING EXECUTED)
- Context: Closed synthetic L2C readiness for `FM03` (`TabICLv2` with `offload_mode="cpu"`, `52.719 s`) and `FM04` (`TabDPT`, `2,361.703 s`); audited `19,098` rows (`4,900` zero-width observations, `36` `Series + Image` groups); proposed leakage-free `Protocol B` (3-fold primary, 5-fold sensitivity) and `Protocol C` (LOSO) alongside historical `Protocol A`; prohibited global `MAPE` as a primary metric; defined statistical, robustness, HPO, and reference reproduction (`RF03` `k=6`, `RF04` `krknet.mat`, `RF05` Table 3) protocols.
- Strict Constraint: D-001 through D-004 remain unchanged; all 8 `.venv*` environments remain unmodified; `0/32` candidates are `APPROVED` until explicit researcher sign-off on `M03_EVALUATION_PROTOCOL.md` and `M04_EXECUTION_PLAN.md`.

## D-009A — Protocol A Legacy Exploratory Benchmark (2026-11-26)
- Status: APPROVED BY RESEARCHER (M04A screening only; historical test partition remains sealed)
- Decision: Protocol A is designated as the legacy exploratory benchmark. Initial screening (M04A) must use the historical `train` (12,216 rows / 2,036 groups) and `validation` (3,060 rows / 510 groups) partitions only; `test` (3,822 rows / 637 groups) remains excluded.

## D-009B — Protocol B Three-Fold Series + Image Primary Internal Evaluation (2026-11-26)
- Status: APPROVED BY RESEARCHER (Methodological protocol approved; execution deferred beyond M04A)
- Decision: Three-fold `Series + Image` grouped evaluation (`max_folds_per_image_group = 1`) is approved as the primary stricter internal evaluation protocol for subsequent phases.

## D-009C — Five-Fold Series + Image Sensitivity Analysis (2026-11-26)
- Status: APPROVED BY RESEARCHER (Methodological protocol approved; execution deferred beyond M04A)
- Decision: Five-fold `Series + Image` sensitivity analysis is restricted to selected finalists.

## D-009D — Protocol C Leave-One-Series-Out (LOSO) Evaluation (2026-11-26)
- Status: APPROVED BY RESEARCHER (Methodological protocol approved; execution deferred beyond M04A)
- Decision: Protocol C Leave-One-Series-Out evaluation is approved for finalists and representative model families; full domain adaptation remains deferred.

## D-009E — Initial Screening Model Roster & Registry Preservation (2026-11-26)
- Status: APPROVED BY RESEARCHER (M04A screening scope: 23 candidates)
- Decision: Twenty-three initial screening candidates (`ML01–ML07`, `DL01–DL05`, `FM03`, `FM04`, `SG01–SG06`, `RF01`, `RF02`, `RF05`) are approved for M04A clean-data screening. All 32 registered candidate IDs (`FM01`, `FM02`, `RF03`, `RF04`, `HY01–HY05` retained) remain preserved in `configs/model_registry.yaml`.

## D-009F — Primary & Tie-Break Validation Metrics (2026-11-26)
- Status: APPROVED BY RESEARCHER
- Decision: Primary metric is **MAE** (µm), followed by **RMSE** (µm) and **Lin's CCC** as secondary tie-break criteria. Global MAPE remains prohibited due to 4,900 zero-width observations.

## D-009G — Hyperparameter Optimization Deferral (2026-11-26)
- Status: APPROVED BY RESEARCHER
- Decision: Hyperparameter optimization (HPO) is deferred to M05. No HPO is permitted during M04 screening; prespecified `scientific_v1` configurations must be used.

## D-009H — Separate Reference Reproduction Track (2026-11-26)
- Status: APPROVED BY RESEARCHER
- Decision: Original AED (`RF03`) and pretrained DLM (`RF04`) exact reproductions shall proceed separately and shall not block initial M04A model screening.

## D-009I — Dual Prediction Policy (Raw & Nonnegative-Clipped) (2026-11-26)
- Status: APPROVED BY RESEARCHER
- Decision: Preserve raw predictions (`y_pred_raw_um`) and nonnegative-clipped predictions (`y_pred_nonnegative_um = max(0, y_pred_raw_um)`) separately. Raw validation MAE is used as the primary screening ranking implementation, with clipped metrics reported separately.

## D-009J — Comparative Robustness Sequence (2026-11-26)
- Status: APPROVED BY RESEARCHER (Execution deferred until after screening and tuning)
- Decision: Full comparative robustness experiments shall follow screening and tuning; no actual-data corruption sweeps are executed in M04A.
