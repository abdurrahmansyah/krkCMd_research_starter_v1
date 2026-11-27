# M04B Researcher Authorization Snapshot

- **Run ID:** `M04B_20261127_164911_DESKTOP-CQB09OU`
- **Authorization Date:** 2026-11-27
- **Preceding Milestone:** `M04A_20261126_145808_DESKTOP-CQB09OU`
- **Approved Decisions (`docs/DECISIONS.md`):** `D-009A`–`D-009J` (preserved) + `D-010A`–`D-010E` (`APPROVED BY RESEARCHER`)

## Newly Approved Decisions (`D-010A`–`D-010E`)
1. **`D-010A`:** One recovery attempt each for `SG02` (`ResNet-1D`) and `SG03` (`InceptionTime`, `n_regressors=1` single-member) with `10,800s` max timeout per model, preserving exact `scientific_v1` config, implementation, and CPU-only TensorFlow/Keras backend.
2. **`D-010B`:** One recovery attempt for `FM04` (`TabDPT`) with `7,200s` max timeout, preserving the last M04A config (`context_size=2048`, `n_ensembles=8`, `batch_size=128`, `context_reduction=retrieval`, `feature_reduction=pca`, `use_flash=false`, `compile=false`).
3. **`D-010C`:** Exploratory paired `Series + Image` cluster bootstrap with 95% CIs on Protocol A validation predictions (exploratory only).
4. **`D-010D`:** Close Protocol A initial screening and prepare proposed finalist rosters and M05 HPO plan without executing HPO, robustness sweeps, or Protocol B/C outer evaluation.
5. **`D-010E`:** Raw validation MAE (`y_pred_raw_um`) is primary ranking criterion; nonnegative-clipped metrics (`y_pred_nonnegative_um = max(0, y_pred_raw_um)`) reported separately.
