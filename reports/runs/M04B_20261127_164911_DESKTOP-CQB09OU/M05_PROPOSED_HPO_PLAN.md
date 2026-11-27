# M05 Proposed Hyperparameter Optimization (HPO) Plan (Planning Only)

- **Run ID:** `M04B_20261127_164911_DESKTOP-CQB09OU`
- **Status:** `PROPOSED_AWAITING_RESEARCHER_APPROVAL` (Zero HPO trials executed in M04B; `D-009G` & `D-010D` enforced)

---

## 1. Objective & Optimization Target
- **Primary Optimization Objective:** Group-aware inner validation **MAE (µm)** (`y_pred_raw_um`), with RMSE (µm) and Lin's CCC as secondary diagnostics.
- **No Test-Partition Leakage:** All HPO trials MUST run inside Protocol A `train` (`12,216` rows / `2,036` gridline groups) using `3`-fold or `5`-fold group-aware inner cross-validation (grouped by `Series + Image` or `group_id` as approved by the researcher), or inside Protocol B inner training folds. Historical `test` (`3,822` rows) remains strictly sealed.
- **Selection Bias Disclosure:** Because Protocol A `validation` (`3,060` rows) was used for M04A/M04B screening, Protocol B (`Series + Image`) is an internal stricter grouped evaluation rather than an untouched external dataset. Selected configurations MUST be frozen before any Protocol B/C outer evaluation.

## 2. Paradigm-Specific Tuning Rules
1. **Classical & Boosting (`ML01`, `ML02`, `ML04`, `ML05`, `ML06`):** Conventional hyperparameter search (`Optuna` TPE or `RandomizedSearchCV` with `seed=42`). For `ML05` (`LightGBM`), enforce conditional `subsample_freq >= 1` whenever `subsample < 1.0`.
2. **Tabular Deep Learning (`DL02`, `DL03`, `DL05`, `DL01`, `DL04`):** Tune architecture (`n_blocks`, `d_block`, `hidden_dims`, `k_ensemble_size`, `context_size`) and optimization (`lr`, `weight_decay`, `dropout`) with group-aware inner early stopping (`patience=15`).
3. **Tabular Foundation Models (`FM03` TabICLv2, `FM04` TabDPT if recovered):** **Zero weight fine-tuning.** Only discrete inference/context configuration search (`n_estimators`, `context_size`, `n_ensembles`, `normalizer`) within approved VRAM/wall-clock caps (`offload_mode="cpu"` required for `FM03`).
4. **Spatial Signal (`SG06` MultiROCKET-HYDRA, `SG04` LITETime, `SG02`/`SG03` if recovered):** Account for high host RAM (`~26.5 GiB` for `SG06`) and CPU-only TF runtime (`SG02`–`SG04`); do NOT assume equal trial count equals equal compute budget.
5. **Fixed Reference Anchors (`RF01`, `RF02`, `RF05`):** Excluded from HPO (`0` trials) to preserve fixed benchmark/paper comparability.
