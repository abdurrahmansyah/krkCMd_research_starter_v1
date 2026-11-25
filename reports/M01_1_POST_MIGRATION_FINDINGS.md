# M01_1_POST_MIGRATION_FINDINGS.md — Post-M01-R Corrections & Workstation Reassessment

**Date:** 2026-11-25  
**Run Directory:** `reports/runs/M01_1_20261125_064517_DESKTOP-CQB09OU/`  
**Workstation:** `DESKTOP-CQB09OU` (Windows Pro 24H2 Build `26100.9711`, Python `3.11.9`)  
**Prerequisite Evidence:** M01-R completed at `reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/` and uploaded at commit `e2cea5d`. M00 baseline reproduction is **not** repeated in M01.1.

---

## 1. Executive Summary & Governance Record

The researcher reviewed the M01-R migration results and authorized proceeding to **M01.1** to resolve minor technical findings without altering research methodology, raw data, baseline `.venv`, M00 results, or manuscript files.

Key outcomes:
1. **Dynamic Hardware Refresh (`reports/logs/hardware_environment_M01_1.json`):** Measured live `108.62 GiB` available RAM, `22,609 MiB` free VRAM on **NVIDIA Quadro RTX 6000** (Turing `sm_75`, `24,576 MiB` total, driver `621.24`, CUDA UMD `13.5`), and `1,748.79 GiB` free disk on `C:`.
2. **Portable Kernel & Environment Verifier (`scripts/verify_env_and_notebook.py`):** Refactored to remove hardcoded kernel `krkcmd-research`, auto-discover kernels matching `sys.executable`, detect stale/missing `argv[0]` interpreters, support `--kernel`, `--verify-kernel-runtime`, and `--json-out`, and pass `4/4` unit tests plus live runtime check on `krkcmd-research-newpc` (`reports/logs/kernel_verification_M01_1.json`).
3. **YAML Metadata Parsing Correction (`configs/baseline.yaml`):** Quoted `"No"` in `metadata_columns` so `PyYAML` parses it as string `"No"` instead of boolean `False` under YAML 1.1 semantics (configuration parsing fix, not a new research decision). Validated in `reports/logs/config_validation_M01_1.json` and `tests/test_baseline_config_contract.py` (`4/4` pass).
4. **CUDA & M02 Dependency Resolution (`reports/logs/cuda_dependency_resolution_M01_1.json`):** Verified official PyTorch Windows `cp311-win_amd64` CUDA wheels (`cu124` up to `2.6.0+cu124`, `cu126`/`cu128`/`cu130` up to `2.9.1`), identified that PyPI `torch 2.15.0` CPU wheels silently override CUDA wheels unless `torch==2.9.1+cu128` is pinned with `--index-url`/`--extra-index-url`, and generated proposed lock files for `env-boost`, `env-deep-cuda-cu128`, `env-deep-addons-pypi`, `env-signal-cpu`, `env-signal-tf`, and `env-foundation-addons-pypi`.
5. **Provisional Dynamic Resource Safety Policy (`scripts/resource_policy.py`):** Implemented exact formulas capping RAM at `64 GB`, VRAM at `20 GB`, and initial env+cache disk at `30 GB` with `16` CPU threads, `1` worker (`1` GPU exclusively), explicit BLAS/OpenMP env vars, wall-clock timeouts, process-tree termination, and `psutil`/`nvidia-smi` monitoring (`5/5` unit tests pass).
6. **Separated Model Identity & Compatibility Matrix (`configs/model_registry.yaml`, `reports/tables/model_compatibility_matrix_M01_1.csv`):** All **32 candidates** preserved (`0` `APPROVED`), `validation_sample_size=3060` and `test_sample_size=3822` aligned to `group_split_manifest.csv`, `DL01` (`sklearn.neural_network.MLPRegressor` prototype with `ConvergenceWarning` at `max_iter=20`) separated from untested PyTorch MLP, `RF03` simplified analytical prototype separated from conditional `CrackWidthAED_VBA.txt` parity, `DL03`/`DL05`/`FM03`/`SG02–SG04`/`SG06` package/backend definitions corrected, and `scripts/check_model_compatibility.py` updated to propagate dynamic smoke results.
7. **Git & Artifact Safety Audit (`reports/GIT_ARTIFACT_SAFETY_REVIEW.md`):** Verified commit `e2cea5d` (`112` tracked files), confirmed zero `.venv*`, `.cache/`, `__pycache__/`, raw datasets, or `.joblib` binaries are tracked, and proposed `.gitignore` improvements for future runs.

---

## 2. Unresolved Issues Deferred to M02 / Reference Track

1. **GPU Computation Verification:** `torch` CUDA is not yet installed; actual Turing `sm_75` tensor execution (`FP32`, `FP16` AMP, SDPA `mem_efficient`) remains `NOT_EXECUTED` until `.venv-deep` is approved and created.
2. **Pretrained `RF04` (`krknet.mat`):** MATLAB and Deep Learning Toolbox (`nnet`) are not installed on `DESKTOP-CQB09OU`; requires external weight export or PyTorch reconstruction.
3. **Faithful `RF03` (`CrackWidthAED_VBA.txt`):** Full multi-stage Python port and numerical parity validation against `AEDwidth` remain pending.
4. **Foundation Model Gated Access (`FM01–FM03`):** Requires researcher license acceptance on Hugging Face / PriorLabs before weight download.
5. **Legacy `.venv_old_pc_backup/` Cleanup & `.gitignore` Updates:** Retained intact pending researcher approval.

---

## 3. Deliverable Inventory

- Reports: `reports/M01_1_POST_MIGRATION_FINDINGS.md`, `reports/M02_PROVISIONING_PLAN.md`, `reports/GIT_ARTIFACT_SAFETY_REVIEW.md`, `docs/MODEL_REGISTRY.md`, `docs/MODEL_COMPATIBILITY_PROTOCOL.md`
- Structured Logs & Matrix: `reports/logs/hardware_environment_M01_1.json`, `reports/logs/kernel_verification_M01_1.json`, `reports/logs/config_validation_M01_1.json`, `reports/logs/cuda_dependency_resolution_M01_1.json`, `reports/tables/model_compatibility_matrix_M01_1.csv`
- Updated Configs & Scripts: `configs/baseline.yaml`, `configs/model_registry.yaml`, `scripts/verify_env_and_notebook.py`, `scripts/check_model_compatibility.py`, `scripts/resource_policy.py`, `scripts/build_m01_1_matrix.py`
- Unit Tests: `tests/test_verify_env_and_notebook.py`, `tests/test_baseline_config_contract.py`, `tests/test_resource_policy.py`
- Versioned Run Evidence: `reports/runs/M01_1_20261125_064517_DESKTOP-CQB09OU/` (including `pip_reports/`, `proposed_locks/`, and `M01_1_review_package.zip`)
