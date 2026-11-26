# M03_DLM_AED_FAIRNESS_REVIEW.md — Benchmark Fairness Review (M03)

1. **Three Strictly Distinct Reference Categories:**
   - **Category 1 (`DLMwidth` / `AEDwidth` CSV columns):** Historical author outputs on clean `krkCMd_table.csv` rows. Valid ONLY for clean Protocol A comparison. **Invalid for Idea 2 corrupted profiles** because they were not recomputed on perturbed inputs.
   - **Category 2 (Faithful Original Inference — `RF03` / `RF04`):** Recomputing `AED` (group-sequential `k=6`) or `krknet.mat` (`RF04`) on perturbed test profiles. Note: `DLM` (`krknet.mat`) was trained by Jakubowski & Tomczak (2024) on the full `19,098`-row development dataset (`krkCMd_table.csv`), meaning `DLMwidth` on our `3,822` test rows is **in-sample** relative to the original DLM training provenance!
   - **Category 3 (Architecture-Based Retraining — `RF05`):** Training the 15-layer Table 3 1D-CNN from scratch strictly on our group-aware training split (`12,216` rows / Protocol B folds) for fair out-of-sample comparison.
