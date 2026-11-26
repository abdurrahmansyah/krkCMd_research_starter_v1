# PROPOSED_M03_EVALUATION_PLAN.md — Proposed Scientific Evaluation Protocol (Post-M02C)

**Prepared at:** End of M02C (`M02C_20261125_203053_DESKTOP-CQB09OU`)  
**Status:** **PROPOSED ONLY — AWAITING RESEARCHER APPROVAL**

1. **Strict Data & Split Contract (Unchanged):**
   - Dataset: `data/raw/krkCMd_table.csv` (`19,098` rows, `x1..x501`, target `MANwidth`).
   - Group-aware split: `reports/tables/group_split_manifest.csv` (`12,216` train / `3,060` val / `3,822` test; `Series + Image + Gridline`; zero group overlap).
   - `DLMwidth` and `AEDwidth` remain external comparison baselines only.
2. **Candidate Tiers for M03 Screening (Idea 1 + Idea 2 Synthetic Robustness):**
   - **Verified `SCALE_CHECK_PASS` (`16` models):**
     - Baseline (`.venv`): `ML01`, `ML02`, `ML03`, `ML07`, `RF01`, `RF02`
     - Boosting (`.venv-boost`): `ML04`, `ML05`, `ML06`
     - Signal CPU (`.venv-signal-cpu` / `.venv-signal-hydra`): `SG05`, `SG06`
     - Deep GPU (`.venv-deep`): `DL01`, `DL02`, `DL03`, `DL05`, `SG01`, `RF05` (train-only normalized)
     - Signal TF CPU (`.venv-signal-tf`): `SG02`, `SG03`, `SG04`
     - Retrieval TabR CPU (`.venv-tabr`): `DL04`
   - **Foundation Models (`.venv-foundation`):**
     - `FM03` (`TabICLv2`) & `FM04` (`TabDPT`): include per verified M02C capacity.
     - `FM01` (`TabPFN-3.5`) & `FM02` (`TabPFN-3.5-Fast`): include only after researcher accepts PriorLabs license & provides `TABPFN_TOKEN` locally.
   - **Deferred / Conditional Tracks:** `RF03` (faithful VBA parity port), `RF04` (`krknet.mat` external MATLAB export), `HY01–HY05` (`DESIGN_REQUIRED`).
3. **Evaluation Metrics & Governance:**
   - Report `MAE`, `RMSE`, `R²`, `MedianAE`, `Bias`, wall-clock fit/predict times, and Idea 2 synthetic perturbation deltas on `test` (`n=3,822`), keeping Idea 4 (`per-Series` adaptation) gated until Idea 1–2 review.
