# Experiment Log

Append-only log. Do not rewrite old results.

## EXP-000 — Starter package created
- Date: 2026-11-20
- Status: NOT RUN
- Scope: Project scaffold, baseline notebook, environment instructions.
- Dataset status: user reports krkCMd_table.csv and krkCMd_scripts.zip downloaded; krkCMd_images.zip still downloading.
- Results: none. No model has been trained.
- Next: place CSV/scripts in data/raw, create environment, run notebook audit cells.

## EXP-001 — Schema correction and comprehensive dataset audit
- Date: 2026-11-23
- Status: COMPLETED
- Scope: Environment setup (Python 3.11.9, .venv, ipykernel), dataset schema audit on krkCMd_table.csv, script inspection on krkCMd_scripts.zip, and metadata column alignment.
- Dataset status:
  - 19,098 rows, 510 columns, 0 missing cells, 0 duplicate rows.
  - Column name correction: `Gridline` verified (template previously used `Grid`).
  - Feature count: exactly 501 features (`x1` to `x501`), all numeric in [0, 255].
  - Target: `MANwidth` verified (19,098 values, range [0.0, 813.59] um, mean 148.88 um).
  - Baselines: `DLMwidth` and `AEDwidth` present for comparison.
  - Grouping validation: `Series + Image + Gridline` yields exactly 3,183 unique physical groups, each with exactly 6 observations matching Stage 1 through 6.
- Scripts examined:
  - `CrackWidthDLM_Matlab.m` + `krknet.mat` (DLM 1D-CNN, 6400 dpi conversion: 3.96875 um/px).
  - `CrackWidthAED_VBA.txt` (AED analytical local extrema method).
  - `Crack_Multi_Intersection_ROI_ImagJ.txt` (ImageJ2 ROI extraction: 500 px length yielding 501 points).
- Results: No machine learning model was trained. Notebook safety guard halted before training due to `Grid` vs `Gridline` discrepancy. Schema corrected in code and config.
- Next: Run benchmark models (Ide 1) after user approval.

## EXP-002 — Milestone M01: Model Registry and Compatibility Assessment
- Date: 2026-11-25
- Status: COMPLETED (Exploratory / Compatibility Audit Only)
- Scope: Hardware & environment audit, 32-candidate model registry, dependency resolution analysis, synthetic profile L0/L1 smoke testing, DLM and AED reproduction feasibility study.
- Key Findings:
  - System: Windows 11, Intel Core i7 (14C/20T), 31.7 GB RAM, NVIDIA RTX 3050 Laptop (4GB VRAM), 37.5 GB free disk space.
  - MATLAB R2026b is installed, but Deep Learning Toolbox is absent.
  - 8 installed models passed synthetic 501-feature L0/L1 smoke tests (0 errors, 100% finite predictions).
  - 24 remaining models registered with primary citations, licenses, and environment isolation plans.
  - Feasibility of faithful Python port for AED confirmed. Table 3 of 2024 paper provides exact 15-layer architecture for DLM retrained.
- Results: Zero machine learning models were trained on actual krkCMd data. No baseline notebooks or manuscript results were altered.
- Next: Await user approval on environment plan and model selection before installing packages or executing L2 progressive capacity tests.

## EXP-003 — Milestone M01-R: New Workstation Migration, Clean Environment Rebuild & M00 Reproduction
- Date: 2026-11-25
- Run ID: `M01R_20261125_032229_DESKTOP-CQB09OU`
- Status: COMPLETED (Migration, Exact Baseline Rebuild, M00 Reproduction & Compatibility Reassessment; NO New Model Training)
- Host: `DESKTOP-CQB09OU` (Windows Pro 24H2 Build `26100.9711`, Intel Core i9-10900KF 20T, 127.92 GB RAM, 1,752.80 GB free C:, NVIDIA Quadro RTX 6000 24 GB VRAM, Driver 621.24 / CUDA UMD 13.5).
- Environment:
  - Installed official Python 3.11.9 (64-bit) with researcher approval; preserved copied `.venv` as `.venv_old_pc_backup`.
  - Rebuilt `.venv` with exact historical package versions (`numpy 2.4.6`, `pandas 2.3.3`, `scipy 1.17.1`, `scikit-learn 1.9.1`, `matplotlib 3.11.2`, `seaborn 0.13.2`, `joblib 1.6.0`, `pyyaml 6.0.4`, `openpyxl 3.1.5`, `pypdf 7.1.1`, `ipykernel 6.31.0`, `nbconvert 7.17.2`, `nbclient 0.11.0`, `psutil 7.2.2`); `pip check` passed.
  - Registered Jupyter kernel `krkcmd-research-newpc` (`Python (krkCMd Research - New PC)`).
- Dataset & Split Verification:
  - `data/raw/krkCMd_table.csv` SHA-256 `CCCA7965B225F77D35567573BB557A6E0476122C381E14AB1BDA898DF9F9B909` (19,098 rows, 510 cols, 3,183 groups, Stage 1..6 complete).
  - Historical `group_split_manifest.csv` reproduced row-for-row and order-for-order identically (12,216 train / 3,060 val / 3,822 test; zero group overlap).
- M00 Reproduction (Isolated Workspace, `212.272s` total via `nbclient`):
  - `Dummy_mean`, `LinearRegression`, `HistGradientBoosting`, `SVR_RBF`: bitwise identical predictions across all 3,822 test rows (`max_abs_diff = 0.0`).
  - `ExtraTrees` (`max_abs_diff = 1.71e-13` µm) and `RandomForest` (`max_abs_diff = 2.27e-13` µm): numerical agreement within `< 3e-13` µm (MAE `14.311523` µm and `14.407363` µm; `ExtraTrees` 2.12x faster: `17.74s` vs `37.56s`; `RandomForest` 1.72x faster: `59.76s` vs `102.99s`).
  - Robustness & per-Series metrics reproduced within `< 6e-15` µm; `ExtraTrees` remains validation-selected model.
- M01 Reassessment:
  - All 32 candidates preserved; 8 installed baseline candidates passed synthetic L0/L1 smoke tests (`ML01-03`, `ML07`, `DL01` [sklearn], `RF01-02`, `RF03` [simplified AED prototype]); transitive `pip install --dry-run` resolved for all 6 proposed environments.
  - Known M01.1 issues documented separately without premature implementation.
- Next: Await researcher review of `reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/M01_R_MIGRATION_REPORT.md` and approval before proceeding to M01.1 or M02.

## EXP-004 — Milestone M02A: Boosting & CPU Signal Provisioning and Synthetic Capacity Assessment
- Date: 2026-11-25
- Run ID: `M02A_20261125_074616_DESKTOP-CQB09OU`
- Status: PARTIAL (4/5 candidates SCALE_CHECK_PASS through L2C; SG06 BLOCKED at L0 due to missing `torch` soft dependency in CPU-only env; ZERO real krkCMd training)
- Environments Created:
  - `.venv-boost` (Python 3.11.9, kernel `krkcmd-boost`): `xgboost==3.2.0`, `lightgbm==4.7.0`, `catboost==1.2.10`, `numpy==2.4.6`, `pandas==3.1.1`, `scikit-learn==1.9.1`; `pip check` clean; lock 100% matched.
  - `.venv-signal-cpu` (Python 3.11.9, kernel `krkcmd-signal-cpu`): `aeon==1.6.0`, `numba==0.63.1`, `llvmlite==0.46.0`, `numpy==2.3.5`, `pandas==3.0.6`, `scikit-learn==1.9.1`; `pip check` clean; lock 100% matched.
- Synthetic L0/L1/L2 Results (strictly synthetic `seed=42`, `D=501`, max `12,216` train / `3,822` test rows):
  - `ML04` (`XGBRegressor`), `ML05` (`LGBMRegressor`), `ML06` (`CatBoostRegressor`), `SG05` (`RocketRegressor`): PASS L0, L1 (incl. joblib reload parity), L2A, L2B, and L2C within dynamic RAM budget and 300s timeout.
  - `SG06` (`MultiRocketHydraRegressor`): FAILED/BLOCKED at L0 because `aeon 1.6.0` requires `torch` (soft dependency), which is prohibited in M02A; deferred to M02B without substituting `MultiRocketRegressor` or `HydraRegressor`.
- Baseline `.venv` and M00/M01/M01-R/M01.1 historical artifacts remain completely unchanged.
- Next: Await researcher review of `reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/M02A_PROVISIONING_REPORT.md` before M02B.

## EXP-005 — Milestone M02B: Deep Learning, GPU, Neural Signal & SG06 Provisioning
- Date: 2026-11-25
- Run ID: `M02B_20261125_081433_DESKTOP-CQB09OU`
- Status: PARTIAL (8/11 targets SCALE_CHECK_PASS through L2C; RF05 L0/L1 PASS / L2A FAILED non-finite SGDM loss; SG06 L0..L2B PASS / L2C 300s timeout; DL04 CONDITIONAL repo-only; ZERO real krkCMd training)
- GPU Verification (`Quadro RTX 6000`, Turing `sm_75`, `torch==2.9.1+cu128`): `GPU_PASS` (FP32 matmul + Conv1d + backward, FP16 AMP, and SDPA `math`/`mem_efficient` all finite).
- Environments Created:
  - `.venv-deep` (`krkcmd-deep`): `torch==2.9.1+cu128`, `rtdl-revisiting-models==0.0.2`, `rtdl-num-embeddings==0.0.12`, `tabm==0.0.3`, `pytabkit==1.8.0`, `delu==0.0.26`, `einops==0.8.2`, `numpy==2.4.6`; `pip check` clean; `nbclient` PASS.
  - `.venv-signal-tf` (`krkcmd-signal-tf`): `aeon==1.6.0`, `tensorflow==2.21.0`, `keras==3.15.1`, `numba==0.63.1`, `numpy==2.3.5`; `pip check` clean; `nbclient` PASS (`CPU_ONLY`).
  - `.venv-signal-hydra` (`krkcmd-signal-hydra`): `aeon==1.6.0`, `torch==2.9.1+cu128`, `numba==0.63.1`, `numpy==2.3.5`; `pip check` clean; `nbclient` PASS (`CPU`).
- Synthetic L0/L1/L2 Results (`seed=42`, `D=501`):
  - `DL01`, `DL02`, `DL03`, `DL05` (`k=8`), `SG01`: `SCALE_CHECK_PASS` on `cuda:0` through L2C (`12,216` -> `3,822`).
  - `SG02` (`ResNetRegressor`), `SG03` (`InceptionTimeRegressor`), `SG04` (`LITETimeRegressor`): `SCALE_CHECK_PASS` on `CPU_ONLY` through L2C.
  - `RF05` (`DLM15LayerCNN_Table3`, SGDM): L0/L1 `PASS` on `cuda:0`; L2A `FAILED` (`FloatingPointError: Non-finite training loss` on unnormalized `[0, 255]` inputs).
  - `SG06` (`MultiRocketHydraRegressor`): L0/L1/L2A/L2B (`15.73 GiB` RSS) `PASS` on `CPU`; L2C `FAILED` (`WALL_CLOCK_TIMEOUT (300s)` at `26.35 GiB` RSS).
  - `DL04` (`TabR`): `CONDITIONAL` (non-PyPI repo `yandex-research/tabular-dl-tabr` @ `17baa908`).
- Next: Await researcher review of `reports/runs/M02B_20261125_081433_DESKTOP-CQB09OU/M02B_PROVISIONING_REPORT.md` before M02C or any real data experiments.

## EXP-006 — Milestone M02C: Tabular Foundation Models & Deferred Candidate Recovery
- Date: 2026-11-25/26
- Run ID: `M02C_20261125_203053_DESKTOP-CQB09OU`
- Status: PARTIAL (Track B: DL04, RF05, SG06 all SCALE_CHECK_PASS through L2C; Track A: FM03 & FM04 PASS through L2B [4,096 rows] / FAILED L2C, FM01 & FM02 BLOCKED_LICENSE pending PriorLabs token; ZERO real krkCMd training)
- Environments Created:
  - `.venv-foundation` (`krkcmd-foundation`): `torch==2.9.1+cu128`, `tabpfn==10.2.0`, `tabicl==2.2.0`, `tabdpt==1.3.2`, `huggingface_hub`, `numpy==2.4.6`; `pip check` clean; `GPU_PASS` (`Quadro RTX 6000`, `matmul_finite=True`, `grads_finite=True`, `params_finite=True`).
  - `.venv-tabr` (`krkcmd-tabr`): `torch==2.9.1+cu128`, `faiss-cpu==1.16.0`, `delu==0.0.26`, `tomli-w==1.2.0`, `tensorboard==2.21.0`, `yandex-research/tabular-dl-tabr` @ `17baa908`.
- Results (strictly synthetic `seed=42`, `D=501`):
  - `DL04` (`bin.tabr.Model`, CPU `faiss-cpu`): L0..L2C `PASS` (`861.95 MiB` RSS, `52.11 s` wall).
  - `RF05` (`DLM15LayerCNN_Table3_Normalized`, train-only zero-center + `pi2mi=3.96875`, `cuda:0`): L0..L2C `PASS` (`1,131.49 MiB` RSS, `111.15 MiB` VRAM, `9.59 s` wall).
  - `SG06` (`MultiRocketHydraRegressor`, `.venv-signal-hydra`, CPU `n_jobs=16`, `1,800s` cap): L2C `PASS` (`344.86 s`, `26,234.87 MiB` RSS).
  - `FM03` (`TabICLv2`, `batch_size=1`, `cuda:0`) & `FM04` (`TabDPT`, `batch_size=128`, `cuda:0`): L0..L2B `PASS` (`8.31 GiB` & `8.16 GiB` VRAM); L2C `FAILED` (VRAM reserve / timeout).
  - `FM01` (`TabPFN-3.5`) & `FM02` (`TabPFN-3.5-Fast`): L0 `PASS`; L1 `BLOCKED_LICENSE` (`TabPFNLicenseError` — requires researcher acceptance at `https://ux.priorlabs.ai`).
- Next: Await researcher review of `reports/runs/M02C_20261125_203053_DESKTOP-CQB09OU/M02C_PROVISIONING_REPORT.md` before M03.

## EXP-007 — Milestone M03: Scientific Evaluation Protocol, Foundation Readiness Closure & Reference Benchmark Planning
- Date: 2026-11-26
- Run ID: `M03_20261126_132016_DESKTOP-CQB09OU`
- Status: COMPLETE (PROPOSED PROTOCOL; ZERO real `krkCMd` training; ZERO `.venv*` modifications; 0/32 `APPROVED`)
- Foundation Readiness Closure (strictly synthetic `seed=42`, `D=501` in `.venv-foundation`):
  - `FM03` (`TabICLRegressor`, `offload_mode="cpu"`, `batch_size=1`, `use_fa3=False`): L1 `PASS` (`9.61 s`), full **L2C `PASS`** (`12,216 -> 3,822` in `52.719 s` wall, `18,418 MiB` peak CUDA res, `18,569 MiB` VRAM delta, `suspend_detected=false`).
  - `FM04` (`TabDPTRegressor`, `context_size=2048`, `n_ensembles=8`): L1 batch consistency `PASS` (`max_abs_diff=3.05e-05`), full **L2C `PASS`** (`12,216 -> 3,822` in `2,361.703 s` / ~39.4 min wall, `10,864 MiB` peak CUDA res, `suspend_detected=false`).
  - `FM01` (`TabPFN-3.5`) & `FM02` (`TabPFN-3.5-Fast`): remain `BLOCKED_LICENSE` (`TABPFN_TOKEN` not set).
- Readiness Reconciliation (32 candidates): `6` M00 historical + `17` additional synthetic L2C PASS (`23` M04-eligible) + `2` `BLOCKED_LICENSE` + `2` reference pending (`RF03`, `RF04`) + `5` custom `DESIGN_REQUIRED`; `0` `APPROVED`.
- Dataset Audit & Proposed Split Manifests (`data/processed/krkCMd_table.csv`: `19,098` rows, `3,183` gridline groups, `36` `Series + Image` groups, `4,900` exact zero-width observations):
  - Generated `protocol_b_series_image_3fold.csv`, `protocol_b_series_image_5fold.csv`, and `protocol_c_leave_one_series_out.csv` (`max_folds_per_image_group=1`).
- Infrastructure & Code Deliverables:
  - Repaired `scripts/resource_policy.py` (suspend/sleep gap detection, bounded `nvidia-smi` timeout, `clock_fn` injection) and documented M02C `48,477.078 s` anomaly in `WATCHDOG_ANOMALY_INVESTIGATION_M03.md`.
  - Implemented `src/evaluation/metrics.py`, `src/features/perturbations.py`, `src/evaluation/experiment_runner.py` (guarded against real-data training), and `tests/test_m03_metrics_perturbations_watchdog.py` (`37` unit tests `OK`).
- Next: Await researcher review and explicit approval of `reports/runs/M03_20261126_132016_DESKTOP-CQB09OU/M03_EVALUATION_PROTOCOL.md` and `M04_EXECUTION_PLAN.md` before M04.

## EXP-008 — Milestone M04A: First Scientific Model Screening on Actual krkCMd Data (Protocol A Train + Validation)
- Date: 2026-11-26
- Run ID: `M04A_20261126_145808_DESKTOP-CQB09OU`
- Status: PARTIAL (20/23 targeted candidates PASS; 3/23 FAILED 3,600s wall-clock cap [`SG02`, `SG03`, `FM04`]; 0 test-partition exposure; 0 `.venv*` modifications)
- Approved Governance: `D-009A` through `D-009J` (`docs/DECISIONS.md`); `seed=42`, `scientific_v1` prespecified configurations, zero HPO (`D-009G`).
- Top Validation Results (Raw MAE µm, `n=3,060`):
  - #1 `ML01` Extra Trees: `14.2536` (`RMSE=28.9352`, `CCC=0.9796`)
  - #2 `FM03` TabICLv2 (zero-shot): `14.3933` (`RMSE=29.1724`, `CCC=0.9794`)
  - #3 `ML02` Random Forest: `14.5582` (`RMSE=29.8717`, `CCC=0.9783`)
  - #4 `ML04` XGBoost: `14.7437`; #5 `ML06` CatBoost: `14.9827`; #6 `ML05` LightGBM: `14.9981`; #7 `ML03` HGB: `15.2379`
  - Neural/Signal/Ref: `DL03` (`16.6599`), `DL02` (`16.7273`), `RF05` (`17.4926`), `SG06` (`22.3345`), `DL05` (`23.5185`), `DL04` (`23.9516`), `DL01` (`24.2129`), `SG05` (`26.2482`), `SG04` (`27.7206`), `ML07` (`29.7191`), `SG01` (`41.8803`), `RF02` (`52.4496`), `RF01` (`120.2711`).
- Notebook & Verification: Executed `notebooks/01_M04A_scientific_screening_analysis.ipynb` via `krkcmd-research-newpc` (`01_M04A_scientific_screening_analysis_executed.ipynb` + `.html`); `41` unit tests `OK`; independent MAE/RMSE recomputation `max_diff=0.0`.
- Next: Stop after M04A and await researcher review of `for_review/result_run_11_M04A.md` and `M04A_review_package.zip`.
