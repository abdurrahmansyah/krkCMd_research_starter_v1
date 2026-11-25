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
