# M03 Foundation Model Readiness Closure Report

- **Run ID:** `M03_20261126_132016_DESKTOP-CQB09OU`
- **Status:** COMPLETE (Synthetic-Only Closure Executed; `FM03` & `FM04` PASSED L2C; `FM01` & `FM02` remain `BLOCKED_LICENSE`)
- **Workstation:** `DESKTOP-CQB09OU` (Quadro RTX 6000 24 GB VRAM, 127.92 GB RAM, `.venv-foundation` Python 3.11)
- **Constraint:** Strictly synthetic data (`D=501`, `seed=42`); zero real `krkCMd_table.csv` / `MANwidth` training; zero automated license acceptance or token creation.

---

## 1. PriorLabs Token & TabPFN-3.5 Status (`FM01`, `FM02`)

- `TABPFN_TOKEN` / `HF_TOKEN` present in environment: `false`.
- `FM01` (`TabPFN-3.5`) & `FM02` (`TabPFN-3.5-Fast`): **`BLOCKED_LICENSE`**.
- **Governance:** Per M03 authorization rules, the agent did NOT accept any license or generate any token automatically. `FM01` and `FM02` remain excluded from M04 execution unless the researcher personally accepts the PriorLabs terms at `https://ux.priorlabs.ai` and sets `TABPFN_TOKEN` locally.

---

## 2. TabICLv2 (`FM03`) — CPU Offload Closure (`offload_mode="cpu"`)

In M02C, `FM03` (`TabICLRegressor`, `tabicl==2.2.0`, `n_estimators=8`, `batch_size=1`, `use_fa3=False`) passed L2B (`4,096 -> 1,024`) but failed L2C (`12,216 -> 3,822`) due to VRAM exhaustion without CPU offloading.

In M03, we tested `offload_mode="cpu"` (verified API parameter of `TabICLRegressor`):

| Attempt ID | Scale | Status | Fit (s) | Predict (s) | Subprocess Wall (s) | Peak CUDA Alloc (MiB) | Peak CUDA Res (MiB) | VRAM Delta (MiB) | Peak RSS (MiB) | Suspend Detected |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `M03_FM03_L1_offload_cpu` | `(100, 501) -> (20,)` | **PASS** | — | — | `9.61` | `414.329` | `524.0` | `522.0` | `1450.75` | `false` |
| `M03_FM03_L2C_offload_cpu` | `(12216, 501) -> (3822,)` | **PASS** | `7.211` | `39.946` | `52.719` | `11917.214` | `18418.0` | `18569.0` | `9720.547` | `false` |

- **Result:** **`SCALE_CHECK_PASS`** at full L2C (`12,216` context -> `3,822` test) in **52.719 s** subprocess wall time with `all_finite=True`, zero suspend gaps (`max_poll_gap_sec=0.407`), and `18.1 GiB` peak CUDA reservation (within the `20 GiB` policy cap and `24 GiB` card).
- **Contract Implication:** Full-context (`12,216` rows, `501` features) evaluation of `FM03` on Quadro RTX 6000 is **feasible and fast (~53 s/split)** when `offload_mode="cpu"`, `batch_size=1`, `use_fa3=False`.

---

## 3. TabDPT (`FM04`) — Batch Consistency & 3,600s L2C Closure

In M02C, `FM04` (`TabDPTRegressor`, `tabdpt==1.3.2`) passed L2B (`4,096 -> 1,024`) and hit the `48,477.078 s` sleep/suspend anomaly during L2C (investigated in `WATCHDOG_ANOMALY_INVESTIGATION_M03.md`).

In M03, we ran:
1. **`M03_FM04_L1_batch_consistency`**: Compared batched (`batch_size=128`) vs unbatched (`batch_size=1`) predictions on synthetic `(100, 501) -> (20,)` data.
   - `status`: **PASS** (`subprocess_elapsed_sec=8.406`, `vram_delta=723.0 MiB`, `peak_rss_mb=1374.27`)
   - `max_abs_diff_batched_vs_unbatched`: `3.0517578125e-05` (`invariant=true`, FP16/BF16 numerical precision tolerance)
   - `max_features_native`: `128` (TabDPT internally applies PCA feature reduction when `D=501 > 128`).
2. **`M03_FM04_L2C_retry`**: Full-scale `(12216, 501) -> (3822,)` with `context_size=2048`, `n_ensembles=8`, `use_flash=False`, `compile=False`, `timeout=3600s`.
   - `status`: **PASS** (`all_finite=true`, `shape=[3822]`)
   - `load_sec`: `1.413`
   - `fit_sec`: `0.228`
   - `predict_sec`: `2354.673` (~39.2 min)
   - `subprocess_elapsed_sec`: **`2361.703`** (~39.4 min, no suspend: `suspend_detected=false`, `max_poll_gap_sec=0.797`)
   - `peak_cuda_alloc_mb`: `8169.624`, `peak_cuda_res_mb`: `10864.0`, `vram_delta_mb`: `11454.0`, `peak_rss_mb`: `1763.988`

- **Result:** **`SCALE_CHECK_PASS`** at full L2C (`12,216` -> `3,822`) with `10.6 GiB` peak CUDA reservation and ~39.4 min wall-clock runtime.
- **Contract Implication:** `FM04` can process the full `12,216`-row training context natively via retrieval (`context_size=2048`), but its ~39.4 min per-split inference time requires budgeting ~40 min per split/fold in M04 (e.g., running `FM04` on Clean Test / Protocol A & primary folds without excessive multi-severity robustness sweeps unless batched/prioritized).

---

## 4. Highest Successful Stage Rule

Per M03 governance, `foundation_context_contracts.json` records the **highest successful stage** strictly (`L2C` for `FM03` and `FM04`; `L0_ONLY` / `BLOCKED_LICENSE` for `FM01` and `FM02`). No failed `L2C` falls back to `L1` (and both `FM03` and `FM04` have now legitimately passed `L2C`).
