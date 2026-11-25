# SG06_RECOVERY_REPORT.md — MultiRocketHydraRegressor Dependency Recovery (M02B)

**Candidate:** `SG06` — MultiROCKET-HYDRA Regression (`aeon.regression.convolution_based.MultiRocketHydraRegressor`)  
**Previous Status (M02A):** `BLOCKED` at L0 in `.venv-signal-cpu` (`ModuleNotFoundError: MultiRocketHydraRegressor requires package 'torch'`).  
**M02B Resolution Strategy:** Preserved `.venv-signal-cpu` completely untouched and provisioned a dedicated isolated environment **`.venv-signal-hydra`** (Jupyter kernel: `krkcmd-signal-hydra`) combining:
- `aeon==1.6.0`
- `numba==0.63.1` & `llvmlite==0.46.0`
- `numpy==2.3.5` (Numba-compatible; isolated from `.venv-deep`'s `numpy==2.4.6` and `.venv`'s `numpy==2.4.6`)
- `torch==2.9.1+cu128` (official Windows `cp311-win_amd64` wheel)
- `scikit-learn==1.9.1`, `pandas==3.0.6`, `scipy==1.17.1`

---

## Key Technical Findings

1. **Exact Class Identity Preserved:** `aeon.regression.convolution_based.MultiRocketHydraRegressor` is used directly (no substitution with `MultiRocketRegressor` or `HydraRegressor`).
2. **CPU vs GPU Execution:** Although `MultiRocketHydraRegressor` requires `torch` to be importable (HYDRA uses PyTorch `nn.Conv1d` / `unfold` operations internally for dictionary kernel transform), `aeon`'s `MultiRocketHydraRegressor` executes on **CPU** by default in `aeon 1.6.0` rather than moving training/data to `cuda:0`. Therefore, its execution device is explicitly labeled `CPU` (not `GPU_PASS`).
3. **Runtime Results:** L0, L1, and progressive L2A/L2B/L2C outcomes are recorded in `smoke_test_results_M02B.json`, `capacity_test_results_M02B.json`, and `model_compatibility_matrix_M02B.csv`.
