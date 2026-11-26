# M03_HPO_BUDGET_PLAN.md — M04 Screening Funnel & M05 Budget-Controlled HPO Plan

1. **M04 Validation-Based Screening Funnel:**
   - Evaluate all eligible candidates (`6` M00 baseline + `15` synthetic L2C PASS + `FM03`/`FM04` if feasible) on **Protocol A (train/val)** and **Protocol B (3-fold/5-fold grouped CV)** using default scientific configurations.
   - **Primary Metric:** `mae_um`; **Tie-break:** `rmse_um`, then `lins_ccc`; **Secondary:** Idea 2 `mean_corrupted_mae_um` & inference latency.
   - Retain representation across paradigms (trees/boosting, deep tabular, retrieval, 1D-CNN/signal, foundation).
2. **M05 Budget-Controlled HPO:**
   - **Scope:** Top finalists from M04 (`<= 6`–`8` models), comparing default vs. tuned configurations on inner grouped CV (`Series + Image`).
   - **Limits:** Max `25`–`30` Optuna/random trials per model OR wall-clock cap (`30 min` classical/boosting, `60 min` deep/signal), early stopping (`patience=10`), fixed seed list `[42, 100, 2026]`, and Pareto analysis (`MAE` vs. `mean_corrupted_mae_um` vs. `fit+predict time`).
   - Distinguish equal trial counts from equal computational wall-clock budgets.
