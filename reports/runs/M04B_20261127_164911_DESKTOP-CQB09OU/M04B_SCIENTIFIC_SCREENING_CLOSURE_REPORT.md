# M04B Scientific Screening Closure Report

- **Run ID:** `M04B_20261127_164911_DESKTOP-CQB09OU`
- **Status:** **COMPLETE (23 / 23 Authorized Screening Candidates `PASS`; `70,380` Validation Predictions; Exploratory Bootstrap `B=10,000` Complete)**
- **Governance:** `D-009A`–`D-009J` + `D-010A`–`D-010E`. Zero test-partition access (`test_rows_exposed_to_workers=0`); zero HPO; zero robustness sweeps; zero `.venv*` modifications.

## 1. Consolidated 32-Model Registry Status
- **23 Scientific `PASS`:** `ML01–ML07` (7), `DL01–DL05` (5), `FM03` & `FM04` (2), `SG01–SG06` (6), `RF01`, `RF02`, `RF05` (3).
- **2 `BLOCKED_LICENSE`:** `FM01` (`TabPFN-3.5`), `FM02` (`TabPFN-3.5-Fast`).
- **2 `REFERENCE_PENDING_IMPL`:** `RF03` (`AED original`), `RF04` (`DLM pretrained`).
- **5 `DESIGN_REQUIRED`:** `HY01–HY05`.
- **0 `APPROVED` for M05 HPO** until researcher sign-off.

## 2. Key Consolidated Findings
1. **Top-7 Cluster (`14.25–15.24 µm` MAE):** `ML01` Extra Trees (`14.25`), `FM03` TabICLv2 zero-shot (`14.39`, 95% CI `[10.63, 19.08]`, paired ΔMAE vs `ML01` `+0.14 [-0.48, +0.88]`), `ML02` Random Forest (`14.56`), `ML04` XGBoost (`14.74`), `ML06` CatBoost (`14.98`, `#2` lowest RMSE `29.05`), `ML05` LightGBM (`15.00`), `ML03` HGB (`15.24`).
2. **Recovered Candidates (`D-010A`, `D-010B`):**
   - `FM04` TabDPT: `MAE=23.90 µm`, `RMSE=40.65 µm`, `CCC=0.9591` (`1,862.9s`).
   - `SG02` ResNet-1D: `MAE=56.42 µm`, `RMSE=78.84 µm`, `CCC=0.8999` (`5,082.4s` CPU-only TF).
   - `SG03` InceptionTime (`n_reg=1`): `MAE=75.03 µm`, `RMSE=108.22 µm`, `CCC=0.8418` (`5,890.9s` CPU-only TF).
3. **Zero-Width Regime (`n=796` / `26.01%` of validation):** `DL03` RealMLP (`8.55 µm` MAE, `0%` negative), `DL02` FT-Transformer (`9.58 µm` raw / `7.85 µm` clipped, `68.8%` negative), `ML04` (`10.10 µm`), `FM03` (`10.19 µm`).
4. **Effective Training Data Audit (`M04B_TRAINING_DATA_FAIRNESS_AUDIT.csv`):** Early-stopping neural models (`DL01`, `DL02`, `DL04`, `DL05`, `SG01`, `RF05`) optimized on `9,774` inner-train rows (`1,629` groups) and monitored `2,442` inner-val rows (`407` groups); trees/boosting/`DL03`/`SG02–SG06`/`FM03`/`FM04` used all `12,216` train rows.
5. **Notebook Execution Blocker:** `jupyter nbconvert --execute` was blocked by Windows Application Control on `_zmq` (`ImportError: DLL load failed while importing _zmq`). All 8 publication figures were rendered via `matplotlib` directly into `figures/`, and `M04B_NOTEBOOK_EXECUTION_LOG.txt` preserves the exact blocker.
