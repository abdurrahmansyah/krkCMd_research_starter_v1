# M04 Proposed Execution Plan (Awaiting Researcher Approval)

- **Run ID:** `M03_20261126_132016_DESKTOP-CQB09OU`
- **Status:** `PROPOSED` (`0` real-data experiments executed in M03)
- **Target Workstation:** `DESKTOP-CQB09OU` (i9-10900KF, 127.92 GB RAM, Quadro RTX 6000 24 GB VRAM)
- **Watchdog Policy:** `scripts/resource_policy.py` (64 GiB RAM cap, 20 GiB VRAM cap, suspend detection active)

---

## Phase 1 — Protocol A Historical Continuity & Reference Porting
- **Objective:** Establish exact apples-to-apples baseline on `Protocol A` (`12,216 / 3,060 / 3,822`) across all `23` eligible models (`6` M00 baselines + `17` synthetic L2C PASS models).
- **Optional Reference Gate:** If researcher approves, implement and unit-test `RF03` (`k=6` VBA port) and `RF04` (`krknet.mat` PyTorch port) before running Phase 1.
- **Estimated Runtime:**
  - `ML01–ML07`, `RF01`, `RF02`, `DL01–DL05`, `SG01–SG05`, `RF05`: ~15–25 min total.
  - `SG06` (CPU): ~6 min.
  - `FM03` (`offload_mode="cpu"`): ~1 min.
  - `FM04` (`TabDPT`): ~40 min.
  - **Phase 1 Total:** ~65–75 min.

## Phase 2 — Protocol B Leakage-Free `Series + Image` CV (3-Fold Primary + 5-Fold Sensitivity)
- **Objective:** Eliminate gridline-stack / within-image spatial leakage (`max_folds_per_image_group=1`) and run group-aware inner HPO (within `M03_HPO_BUDGET_PLAN.md` trial caps).
- **Scope:**
  - All `22` fast/medium eligible models across 3-fold primary (`3` folds) and 5-fold sensitivity (`5` folds).
  - `FM04` (`TabDPT`, ~40 min/split) proposed for **Protocol A** and optionally **Protocol B 3-fold** (`~2 hours`) if researcher approves the 2-hour compute slot; excluded from 5-fold + multi-severity robustness sweeps to keep runtime bounded.
- **Estimated Runtime:** ~3–5 hours (including inner HPO for `ML01–ML07`, `DL01–DL05`, `SG01–SG05`).

## Phase 3 — Protocol C Leave-One-Series-Out (LOSO) Cross-Series Generalization
- **Objective:** Quantify Idea 4 subgroup / domain-shift generalization across the 4 casting/age series (`CMd_0.23_2mths`, `CMd_0.23_20mths`, `CMd_0.28_2mths`, `CMd_0.28_20mths`).
- **Scope:** Top-performing and representative models across all 5 paradigms (`22` fast/medium eligible models; `FM04` optional).
- **Estimated Runtime:** ~45–60 min.

## Phase 4 — Idea 2 Comparative Robustness Evaluation
- **Objective:** Evaluate clean-vs-perturbed degradation across all 7 perturbation families (`gaussian_noise`, `brightness_shift`, `contrast_scale`, `gaussian_blur`, `spatial_shift`, `local_dropout`, `salt_pepper`) at `3`–`5` severity levels on `Protocol B` 3-fold test sets (and `Protocol A` test set).
- **Scope:** All `22` fast/medium eligible models (`FM03` included at ~53s/eval on clean + primary severities; `FM04` excluded from exhaustive 7x5=35 robustness sweeps due to ~40 min/eval).
- **Estimated Runtime:** ~2–3 hours.

## Phase 5 — Statistical Testing & Manuscript Tables
- **Objective:** Compute group-clustered paired bootstrap CIs (`B=2000`), Holm-Bonferroni p-values, Friedman/Nemenyi ranks, and export publication-ready tables/figures.
