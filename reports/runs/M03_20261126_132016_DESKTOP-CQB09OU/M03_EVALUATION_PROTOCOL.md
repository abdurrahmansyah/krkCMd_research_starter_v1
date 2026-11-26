# M03 Comprehensive Scientific Evaluation Protocol (PROPOSED)

- **Run ID:** `M03_20261126_132016_DESKTOP-CQB09OU`
- **Status:** `PROPOSED` (Awaiting Researcher Review & Authorization prior to M04)
- **Research Scope:**
  - **Idea 1:** Comprehensive Multi-Paradigm AI Benchmark (Classical/Boosting, Tabular Deep Learning, Tabular Foundation Models, Spatial/1D Signal Regression, Reference Benchmarks).
  - **Idea 2:** Comparative Robustness Benchmark & Robustness Enhancement (`krkCMd` optical/imaging/crack-profile perturbations).
  - **Idea 4 (Incorporated Subgroup Analysis):** Cross-series & subgroup generalization via Leave-One-Series-Out (LOSO) and per-series diagnostics (`CMd_0.23_2mths`, `CMd_0.23_20mths`, `CMd_0.28_2mths`, `CMd_0.28_20mths`).

---

## 1. Master Protocol Architecture

This document integrates the modular M03 specifications into a single governance and experimental protocol:

1. **Research Questions & Hypotheses:** [M03_RESEARCH_QUESTIONS.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_RESEARCH_QUESTIONS.md)
2. **Dataset & Split Governance:** [M03_SPLIT_PROTOCOL.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_SPLIT_PROTOCOL.md) & [M03_SPLIT_AUDIT.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_SPLIT_AUDIT.json)
   - **Protocol A (Historical Anchor):** `train=12,216` (`2,036` gridline groups), `val=3,060` (`510` groups), `test=3,822` (`637` groups) — preserved unmodified for continuity with M00.
   - **Protocol B (Leakage-Free `Series + Image` CV):** 3-fold primary (`6,246 / 6,444 / 6,408` rows, all 4 Series represented in every fold; `max_folds_per_image_group=1`) + 5-fold sensitivity (`3,786–3,834` rows/fold, noting `CMd_0.28_20mths` has only `4` image groups).
   - **Protocol C (LOSO Cross-Series):** 4-fold Leave-One-Series-Out (`CMd_0.23_20mths`, `CMd_0.23_2mths`, `CMd_0.28_20mths`, `CMd_0.28_2mths`) for domain-shift / Idea 4 subgroup generalization.
3. **Metric Register & Zero-Width Handling:** [M03_METRIC_REGISTER.yaml](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_METRIC_REGISTER.yaml) & [metrics.py](file:///c:/PROJECT/krkCMd_research_starter_v1/src/evaluation/metrics.py)
   - Primary: `RMSE` (µm), `MAE` (µm), `R2`.
   - Stratified & Non-Negative: `zero_width_mae` (`y_true == 0`, `4,900` rows / `25.66%`), `positive_width_rmse` (`y_true > 0`), `positive_width_mape` (`y_true > 0` only), `spearman_rho`, `p95_abs_error`, `max_abs_error`.
   - Global `MAPE` is **prohibited** as a primary metric due to division-by-zero on the `4,900` exact zero-width observations.
4. **Statistical Analysis Plan:** [M03_STATISTICAL_ANALYSIS_PLAN.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_STATISTICAL_ANALYSIS_PLAN.md)
   - Group-aware paired bootstrap (`B=2000` over `image_group` clusters) + Wilcoxon signed-rank / Holm-Bonferroni correction + Friedman/Nemenyi multi-model ranking.
5. **Robustness Protocol:** [M03_ROBUSTNESS_PROTOCOL.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_ROBUSTNESS_PROTOCOL.md), [M03_PERTURBATION_REGISTER.yaml](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_PERTURBATION_REGISTER.yaml), & [perturbations.py](file:///c:/PROJECT/krkCMd_research_starter_v1/src/features/perturbations.py)
   - 7 intensity/spatial perturbation families across 3–5 severity levels, evaluated via clean-vs-perturbed degradation (`delta_rmse`, `retention_ratio`, `aurc_rmse`).
6. **HPO & Compute Budget Governance:** [M03_HPO_BUDGET_PLAN.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_HPO_BUDGET_PLAN.md) & [M03_MODEL_CONFIGURATION_REGISTER.yaml](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_MODEL_CONFIGURATION_REGISTER.yaml)
   - Strict inner group-aware validation HPO; zero test-set tuning; zero HPO on fixed references (`RF01`, `RF02`, `RF05`) and zero-shot foundation models (`FM03`, `FM04`).
7. **Reference Reproduction & Fairness:** [M03_REFERENCE_REPRODUCTION_PROTOCOL.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_REFERENCE_REPRODUCTION_PROTOCOL.md) & [M03_DLM_AED_FAIRNESS_REVIEW.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_DLM_AED_FAIRNESS_REVIEW.md)
   - `RF03` (`AED original`) requires exact `k=6` group-sequential VBA port (`j_upper`/`j_lower` propagation from Stage 1); `RF04` (`DLM pretrained`) requires `krknet.mat` PyTorch port; `RF05` (`DLM retrained`) requires train-only zero-centering + `pi2mi=3.96875`.
8. **Model Eligibility & Readiness Reconciliation:** [M03_MODEL_ELIGIBILITY.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_MODEL_ELIGIBILITY.csv) & [model_compatibility_matrix_M03.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/model_compatibility_matrix_M03.csv)
   - 32 total candidates: `6` M00 historical + `17` additional synthetic L2C PASS (`23` eligible) + `2` `BLOCKED_LICENSE` (`FM01`, `FM02`) + `2` reference pending implementation (`RF03`, `RF04`) + `5` custom `DESIGN_REQUIRED` (`HY01–HY05`); `0` `APPROVED` until researcher sign-off.
9. **Cross-Environment Runner Interface:** [experiment_runner.py](file:///c:/PROJECT/krkCMd_research_starter_v1/src/evaluation/experiment_runner.py)
   - Enforces `authorize_real_data_training=True` guard (`PermissionError` otherwise) and routes each model to its verified isolated `.venv*` via `scripts/resource_policy.py`.

---

## 2. Stop-Gate Criteria Before M04 Execution

M04 training MUST NOT start until the researcher explicitly approves:
1. The primary CV scheme (`Protocol B` 3-fold `Series + Image` vs 5-fold sensitivity) alongside `Protocol A` and `Protocol C` (LOSO).
2. The eligible 23-model roster (and whether `FM01`/`FM02` PriorLabs tokens or `RF03`/`RF04` ports should be completed before or alongside M04).
3. The compute and HPO budget in `M04_EXECUTION_PLAN.md`.
