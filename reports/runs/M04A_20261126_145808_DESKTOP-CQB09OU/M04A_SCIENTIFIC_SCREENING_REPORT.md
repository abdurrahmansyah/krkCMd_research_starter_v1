# M04A Scientific Screening Report

- **Run ID:** `M04A_20261126_145808_DESKTOP-CQB09OU`
- **Milestone:** Run 11 — M04A First Scientific Model Screening on Actual `krkCMd` Data
- **Governance:** Protocol A (`train=12,216` / `2,036` groups; `validation=3,060` / `510` groups; `seed=42`). Historical `test` (`3,822` / `637` groups) strictly sealed and excluded (`test_rows_exposed_to_worker = 0`).

---

## 1. Execution Summary
- **Targeted Roster:** `23` eligible candidates (`D-009E`). All `32` registry IDs retained.
- **Succeeded (`20 / 23`):** `ML01–ML07`, `DL01–DL05`, `FM03`, `SG01`, `SG04`, `SG05`, `SG06`, `RF01`, `RF02`, `RF05`. Every successful model produced exact `3,060` finite validation predictions with `0.0` MAE/RMSE recomputation discrepancy (`M04A_METRIC_RECOMPUTATION.json`).
- **Failed (`3 / 23`):**
  - `SG02` (`ResNetRegressor`, `.venv-signal-tf` CPU-only): `WALL_CLOCK_TIMEOUT (3600s)`.
  - `SG03` (`InceptionTimeRegressor`, `.venv-signal-tf` CPU-only, `n_regressors=1` single-member): `WALL_CLOCK_TIMEOUT (3600s)`.
  - `FM04` (`TabDPTRegressor`, `.venv-foundation`): Attempt 1 failed `TypeError` (`seed` in `predict`, not `__init__`); Attempt 2 (`_r2`) failed `GPU_VRAM_BUDGET_EXCEEDED (22339.0 MiB > 19291.6 MiB)` with `batch_size=None`; Attempt 3 (`_r3`, `batch_size=128`) hit `WALL_CLOCK_TIMEOUT (3600s) [SUSPEND_DETECTED]` at `3601.484s`.

---

## 2. Validation Leaderboard (Raw Predictions, `n=3,060`)

| Rank | Model | Raw MAE (µm) | Raw RMSE (µm) | Lin's CCC | R² | Clipped MAE (µm) | Neg. Preds | Total Time (s) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `ML01` Extra Trees | **14.25** | 28.94 | 0.9796 | 0.9606 | 14.25 | 0 | 32.20 |
| 2 | `FM03` TabICLv2 (zero-shot) | **14.39** | 29.17 | 0.9794 | 0.9600 | 14.38 | 291 | 83.25 |
| 3 | `ML02` Random Forest | **14.56** | 29.87 | 0.9783 | 0.9580 | 14.56 | 0 | 95.88 |
| 4 | `ML04` XGBoost | **14.74** | 29.68 | 0.9786 | 0.9586 | 14.62 | 256 | 20.74 |
| 5 | `ML06` CatBoost | **14.98** | 29.05 | 0.9796 | 0.9603 | 14.86 | 203 | 29.48 |
| 6 | `ML05` LightGBM | **15.00** | 29.65 | 0.9787 | 0.9586 | 14.86 | 255 | 9.39 |
| 7 | `ML03` HistGradientBoosting | **15.24** | 30.15 | 0.9779 | 0.9572 | 15.16 | 143 | 9.19 |
| 8 | `DL03` RealMLP | **16.66** | 31.41 | 0.9762 | 0.9536 | 16.66 | 0 | 119.34 |
| 9 | `DL02` FT-Transformer | **16.73** | 31.36 | 0.9768 | 0.9537 | 16.26 | 578 | 188.22 |
| 10 | `RF05` DLM retrained | **17.49** | 33.68 | 0.9728 | 0.9466 | 17.45 | 25 | 22.95 |
| 11 | `SG06` MultiROCKET-HYDRA | **22.33** | 33.46 | 0.9730 | 0.9473 | 20.61 | 340 | 347.88 |
| 12 | `DL05` TabM | **23.52** | 41.36 | 0.9583 | 0.9195 | 23.12 | 184 | 24.02 |
| 13 | `DL04` TabR | **23.95** | 42.81 | 0.9548 | 0.9137 | 23.28 | 479 | 430.01 |
| 14 | `DL01` MLP | **24.21** | 46.34 | 0.9489 | 0.8990 | 24.15 | 89 | 15.83 |
| 15 | `SG05` ROCKET | **26.25** | 38.83 | 0.9631 | 0.9291 | 24.20 | 312 | 51.98 |
| 16 | `SG04` LITETime (n_reg=1) | **27.72** | 38.43 | 0.9638 | 0.9305 | 27.28 | 117 | 739.40 |
| 17 | `ML07` SVR RBF | **29.72** | 49.86 | 0.9366 | 0.8830 | 28.69 | 293 | 58.14 |
| 18 | `SG01` Vanilla 1D-CNN | **41.88** | 56.21 | 0.9168 | 0.8513 | 40.52 | 129 | 28.11 |
| 19 | `RF02` Linear Regression | **52.45** | 70.37 | 0.8722 | 0.7670 | 46.02 | 439 | 1.54 |
| 20 | `RF01` Dummy Mean | **120.27** | 145.79 | ~0.0000 | -0.0001 | 120.27 | 0 | 1.30 |

## 3. Historical Reference Comparison (Separate Provenance)
On the exact same `3,060` Protocol A validation rows:
- **`DLMwidth` (historical stored output):** `MAE = 14.59 µm`, `RMSE = 27.14 µm`, `Lin's CCC = 0.9820`, `R² = 0.9653`.
- **`AEDwidth` (historical stored output):** `MAE = 33.21 µm`, `RMSE = 52.19 µm`, `Lin's CCC = 0.9288`, `R² = 0.8718`, `Bias = -23.28 µm`.
- **Provenance Warning:** These stored CSV outputs are historical and potentially non-independent (the original pretrained MATLAB DLM may have been trained on overlapping images/series prior to the `group_split_manifest.csv` split). Under fair Protocol A retraining (`RF05`), DLM achieves `MAE = 17.49 µm` / `RMSE = 33.68 µm`.

## 4. Key Scientific Insights
1. **Zero-shot Foundation Model Competitiveness:** `FM03` (`TabICLv2` with `offload_mode="cpu"`) ranked **#2 overall (`MAE = 14.39 µm`)** without any dataset-specific hyperparameter tuning, outperforming XGBoost, CatBoost, LightGBM, Random Forest, and all tabular/signal deep learning baselines.
2. **Tree & Boosting Dominance on Raw 501-Point Profiles:** `ML01–ML06` occupy 6 of the top 7 spots (`MAE = 14.25–15.24 µm`) with fast CPU execution (`9–96 s`).
3. **Value of `Protocol B` Next:** Because Protocol A splits by `gridline` rather than `image`, within-image spatial correlation may favor memorization-capable tree/kNN/in-context models. Protocol B (`Series + Image`, `D-009B`) is essential to verify generalization across unseen images.
