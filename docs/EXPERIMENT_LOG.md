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
