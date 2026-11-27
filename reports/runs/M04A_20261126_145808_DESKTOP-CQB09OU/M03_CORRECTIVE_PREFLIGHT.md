# M03 Corrective Preflight Report (Pre-Training Verification)

- **Run ID:** `M04A_20261126_145808_DESKTOP-CQB09OU`
- **Outcome:** **PASS** (All mandatory Section 2 corrective checks completed before any real-data training)

## 2.1 Dataset Schema Reconciliation (`510` vs `512` columns)
- **Raw CSV (`data/raw/krkCMd_table.csv`):** Verified shape `(19098, 510)`, SHA-256 `CCCA7965B225F77D35567573BB557A6E0476122C381E14AB1BDA898DF9F9B909`.
- **Exact Column Order:** `['No', 'Profile', 'Series', 'Image', 'Gridline', 'Stage']` (6 metadata) + `x1..x501` (501 brightness features) + `['MANwidth', 'DLMwidth', 'AEDwidth']` (1 target + 2 comparison-only baselines) = **510 columns**.
- **Explanation of `512` in `M03_SPLIT_AUDIT.json`:** The M03 audit script added two derived grouping columns (`group_id`, `image_group`) in memory before recording `shape[1] = 512`. Raw CSV was never modified.
- **Verified Counts:** `3,183` gridline groups (every group has `min=6, max=6` observations), `36` `Series + Image` groups, `4,900` exact zero-width targets (`MANwidth == 0.0`), `0` missing values in `x1..x501` and `MANwidth`.
- **Historical Split (`reports/tables/group_split_manifest.csv`):** `19,098` unique `source_row_id` (`0..19097`); `train=12,216` (`2,036` groups), `validation=3,060` (`510` groups), `test=3,822` (`637` groups); pairwise group overlap = `0`.

## 2.2 Target Contract Correction
- Corrected `M03_MODEL_CONFIGURATION_REGISTER.yaml` placeholder `target: MANwidth_um` -> **`target: MANwidth`**, **`target_unit: um`** in `M04A_SCIENTIFIC_CONFIGURATIONS.yaml`.

## 2.3 Readiness Evidence Reconciliation (32 IDs)
- Retained all 32 registry IDs (`6` M00 historical + `17` additional synthetic L2C PASS = `23` M04A candidates; `2` `BLOCKED_LICENSE`; `2` reference pending `RF03`/`RF04`; `5` custom `DESIGN_REQUIRED`).
- Removed unsupported effective `500`-feature limit assertions from `FM01` / `FM02` (`UNKNOWN / UNVERIFIED` until token-authorized checkpoint inspection).

## 2.4 Configuration Identity & Signature Verification
- Separated `compat_v1` (M02 synthetic), `scientific_v1` (M04A prespecified), `official_default`, and `tuned_v1` (deferred to M05).
- **LightGBM (`ML05`):** Probed `LGBMRegressor.__init__` signature; added explicit `subsample_freq: 1` so `subsample: 0.8` is active (otherwise silently ignored when `subsample_freq=0`).
- **InceptionTime (`SG03`) & LITETime (`SG04`):** Probed `aeon==1.6.0` signatures; official default `n_regressors=5`. Explicitly labeled `n_regressors=1` in `scientific_v1` as a **single-member configuration** (`single_member_config: true`), not official default.
- **DLM Retrained (`RF05`):** Reconciled proposed `100` epochs in M03 register vs `50` epochs in `M03_REFERENCE_REPRODUCTION_PROTOCOL.md` (paper Table 3 SGDM schedule); standardized `scientific_v1` to `max_epochs: 50`, `batch_size: 128`, `SGD(lr=0.001, momentum=0.9)`, train-only zero-centering, `pi2mi=3.96875`.

## 2.5 & 2.6 Primary Metric & Prediction Policy
- Primary ranking metric: **Raw validation MAE (µm)** (`y_pred_raw_um`), with **RMSE (µm)** and **Lin's CCC** as tie-breakers (`D-009F`, `D-009I`).
- Nonnegative-clipped predictions (`y_pred_nonnegative_um = max(0, y_pred_raw_um)`) and negative raw prediction counts/magnitudes are computed and reported separately.

## 2.7 Robustness Register Reconciliation
- Reconciled `M03_PERTURBATION_REGISTER.yaml` and `src/features/perturbations.py`: **16 conditions across 9 families** (`brightness_shift`, `contrast_scale`, `gaussian_noise`, `gaussian_smoothing`, `gamma`, `illumination_gradient`, `impulse_noise`, `downsample_interp`, `combined`). `spatial_shift` and `local_dropout` are NOT implemented and are not claimed.
- Fixed empty-condition handling in `src/evaluation/metrics.py::compute_robustness_summary` to return `None` instead of fabricating `clean_mae` when `corrupted_preds` is empty.
- No actual-data robustness sweeps are executed in M04A (`D-009J`).

## 2.8 Statistical Analysis Policy
- Future Protocol B confirmatory inference uses `Series + Image` clusters (`n=36`) as primary paired unit and `gridline` clusters as sensitivity; no significance-driven model selection in M04A.
