# M04B Scientific Recovery Report (Track A)

- **Run ID:** `M04B_20261127_164911_DESKTOP-CQB09OU`
- **Approved Decisions:** `D-010A` (`SG02`, `SG03` up to `10,800s`), `D-010B` (`FM04` up to `7,200s`)
- **Outcome:** **3 / 3 Recovery Candidates PASSED** (exactly 1 attempt each; `suspend_detected=False`)

## Recovery Summary

| Model | Decision | Env & Device | Timeout Cap (s) | Wall Time (s) | Status | Raw MAE (µm) | Raw RMSE (µm) | Lin's CCC | Notes |
|---|---|---|---:|---:|---|---:|---:|---:|---|
| `FM04` TabDPT | `D-010B` | `.venv-foundation` (`cuda:0`) | 7,200 | `1862.938` | **PASS** | `23.9026` | `40.6506` | `0.9591` | `tabdpt==1.3.2`, `tabdpt1_3.safetensors` (`97DC3B...`), `batch_size=128`, `context_size=2048`, `n_ensembles=8` |
| `SG02` ResNet-1D | `D-010A` | `.venv-signal-tf` (CPU-only TF) | 10,800 | `5082.375` | **PASS** | `56.4174` | `78.8366` | `0.8999` | `aeon` `ResNetRegressor`, `n_epochs=50`, `batch_size=64` |
| `SG03` InceptionTime | `D-010A` | `.venv-signal-tf` (CPU-only TF) | 10,800 | `5890.922` | **PASS** | `75.0297` | `108.2175` | `0.8418` | `aeon` `InceptionTimeRegressor`, `n_regressors=1` (single-member), `n_epochs=50`, `batch_size=64` |

All three recovered models produced exact `3,060` finite validation predictions with `test_rows_exposed_to_worker=0`, passing all 16 strengthened validation checks.
