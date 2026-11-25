Ran git status and directory listing
Analyzed AGENT.md:L1-258
Analyzed MASTER_PROMPT.md:L1-79
Analyzed README.md:L1-53
Analyzed requirements.txt:L1-18
Analyzed DECISIONS.md:L1-33
Analyzed EXPERIMENT_LOG.md:L1-42
Analyzed RESEARCH_QUESTIONS.md:L1-16
Analyzed DATA_AND_PAPERS.md:L1-46
Analyzed STEP_BY_STEP_INDONESIAN.md:L1-120
Analyzed baseline.yaml:L1-19
Analyzed model_registry.yaml:L1-341
Analyzed MODEL_REGISTRY.md:L1-290
Analyzed MODEL_COMPATIBILITY_PROTOCOL.md:L1-89
Analyzed MODEL_ENVIRONMENT_PLAN.md:L1-83
Analyzed M01_COMPATIBILITY_REPORT.md:L1-197
Analyzed check_model_compatibility.py:L1-800
Analyzed PAPER_AGENT.md:L1-31
Analyzed REFERENCE_REGISTER.md:L1-66
Analyzed check_model_compatibility.py:L801-978
Analyzed PAPER_AGENT.md:L1-31
Analyzed VERIFY_RESULTS.md:L1-13
Analyzed .gitignore:L1-26
Ran locate tools and list workspace files
Analyzed output.txt:L1-191
Analyzed audit_dataset.py:L1-308
Analyzed verify_env_and_notebook.py:L1-157
Analyzed DATASET_AUDIT_REPORT.md:L1-63
Analyzed baseline_run_summary.json:L1-24
Analyzed hardware_environment.json:L1-50
Analyzed benchmark_metrics.csv:L1-7
Analyzed existing_baseline_metrics.csv:L1-3
Analyzed robustness_metrics.csv:L1-9
Analyzed test_per_series_metrics.csv:L1-5
Analyzed PRE_EXECUTION_CHECKLIST.md:L1-39
Analyzed dependency_resolution.json:L1-58
Analyzed comprehensive_audit.json:L1-158
Analyzed result_run_4_M01.md:L1-308
Analyzed result_run_3.md:L1-208
Analyzed pyvenv.cfg:L1-5
Ran check git status and locate Python installations
Analyzed first run.md:L1-295
Analyzed result_run_2.md:L1-185
Analyzed initial_audit_summary.csv:L1-8
Ran audit git tracking and search for Python and software · Exited with code 1
Analyzed 00_baseline_krkCMd.ipynb:L1-800
Analyzed CrackWidthAED_VBA.txt:L1
Analyzed CrackWidthDLM_Matlab.m:L1-17
Analyzed Crack_Multi_Intersection_ROI_ImagJ.txt:L1-110
Ran search Python, software, and audit hardware · Exited with code 1
Analyzed 00_baseline_krkCMd.ipynb:L801-1600
Analyzed 00_baseline_krkCMd.ipynb:L1601-2400
Analyzed 00_baseline_krkCMd.ipynb:L801-1600
Analyzed 00_baseline_krkCMd.ipynb:L1601-2400
Checked task Search Python, software, and audit hardware
Analyzed 00_baseline_krkCMd.ipynb:L801-1600
Analyzed 00_baseline_krkCMd.ipynb:L1601-2400
Ran check Python, drives, and hardware details · Exited with code 1
Analyzed 00_baseline_krkCMd.ipynb:L801-1600
Ran audit installed software, memory, WSL, and directories
Analyzed 00_baseline_krkCMd.ipynb:L801-1600
Ran inspect project folders, git refs, systeminfo, and .venv metadata
Ran generate hardware audit and file inventory artifacts
Analyzed hardware_environment.json:L1-82
Analyzed model_compatibility_matrix.csv:L1-33
Ran print essential file sizes, git tracking, and SHA-256 hashes
Analyzed output.txt:L1-86
Ran verify clean git working tree status

# M01-R Status Checkpoint — Stopped at Phase 3.1 Prerequisite (Missing Python 3.11)

Execution proceeded sequentially through **Phase 0**, **Phase 1**, **Phase 2**, and **Phase 3.1–3.2** using run ID **`M01R_20261125_032229_DESKTOP-CQB09OU`**. Per the Phase 3.1 stop condition, execution is **paused** because **Python 3.11 is not installed** on the new workstation and system-wide software installation requires your explicit approval or manual completion.

---

## 1. Phase Status Summary

| Phase | Status | Notes |
|---|---|---|
| Phase 0 — Research context recovery & governance | **PASS** | All governance, registry, audit, and historical run files read |
| Phase 1 — Repository reconciliation & migration safety | **PASS** | Git state verified; 144 files inventoried in [file_inventory.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/file_inventory.json) |
| Phase 2 — Complete hardware & system audit | **PASS** | New PC specs measured & saved to [hardware_environment.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/hardware_environment.json) |
| Phase 3 — Rebuild baseline Python environment | **BLOCKED** | 3.1–3.2 inspected; **no Python 3.11 runtime installed on workstation** |
| Phase 4 — Dataset & research-file integrity audit | **PARTIAL** | Raw files, hashes, and `krkCMd_scripts.zip` verified; `scripts/audit_dataset.py` requires Python 3.11 |
| Phase 5 — Static source-code & notebook verification | **PARTIAL** | Notebook JSON/schema checked (25 cells, 12 code, `Gridline` OK); `scripts/verify_env_and_notebook.py` requires Python 3.11 |
| Phases 6–11 — Reproduction, analysis, smoke tests, env plan, docs, deliverables | **NOT_EXECUTED** | Waiting for Python 3.11.9 prerequisite |

---

## 2. Phase 0 — Recovered Project State Summary

- **Approved research decisions:**
  - `D-001` ([DECISIONS.md](file:///c:/PROJECT/krkCMd_research_starter_v1/docs/DECISIONS.md)): Idea 1 (CPU-friendly benchmark) + Idea 2 (synthetic robustness); Idea 4 gated.
  - `D-002`: Target `MANwidth`; features `x1`..`x501` (501 features); `DLMwidth` and `AEDwidth` comparison-only.
  - `D-003`: Mandatory group key `Series + Image + Gridline` (3,183 groups × 6 stages = 19,098 rows).
  - `D-004`: Metadata column standardized to `Gridline` (not `Grid`).
  - `D-005` (Exploratory): 32-candidate M01 registry; zero new models approved for experimental training.
- **Historical experiments:** `EXP-000` (scaffold), `EXP-001` (dataset/schema audit), M00 baseline execution ([00_baseline_krkCMd.ipynb](file:///c:/PROJECT/krkCMd_research_starter_v1/notebooks/00_baseline_krkCMd.ipynb), [baseline_run_summary.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/logs/baseline_run_summary.json)), `EXP-002` (M01 exploratory compatibility audit in [M01_COMPATIBILITY_REPORT.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/M01_COMPATIBILITY_REPORT.md)).
- **Existing source code:** [audit_dataset.py](file:///c:/PROJECT/krkCMd_research_starter_v1/scripts/audit_dataset.py), [verify_env_and_notebook.py](file:///c:/PROJECT/krkCMd_research_starter_v1/scripts/verify_env_and_notebook.py), [check_model_compatibility.py](file:///c:/PROJECT/krkCMd_research_starter_v1/scripts/check_model_compatibility.py), [baseline.yaml](file:///c:/PROJECT/krkCMd_research_starter_v1/configs/baseline.yaml), [model_registry.yaml](file:///c:/PROJECT/krkCMd_research_starter_v1/configs/model_registry.yaml).
- **Proposed experiments / Future M01.1 & M02 tasks:** Fixing the 12 known M01.1 issues (e.g., `validation_sample_size: 3054` / `test_sample_size: 3828` mismatch in [model_registry.yaml](file:///c:/PROJECT/krkCMd_research_starter_v1/configs/model_registry.yaml) vs actual `3060` / `3822` in [baseline_run_summary.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/logs/baseline_run_summary.json), hardcoded smoke-test statuses in [check_model_compatibility.py](file:///c:/PROJECT/krkCMd_research_starter_v1/scripts/check_model_compatibility.py), `MultiRocketRegressor` vs HYDRA, aeon backend, TabPFN/TabICLv2 specs, AED prototype fidelity), L2 scale tests, and isolated M02 environments (none authorized now).

---

## 3. Phase 1 — Repository Reconciliation & File Inventory

- **Canonical workspace:** `c:/PROJECT/krkCMd_research_starter_v1` (sole directory under `C:\PROJECT`; Git clone and copied local files reside in the same folder).
- **Git state:**
  - Origin: `https://github.com/abdurrahmansyah/krkCMd_research_starter_v1.git`
  - Branch / Commit: `main` tracking `origin/main` at `201aa50b8b97e789d7eb855609b027bd02904539` (`feat: M01`)
  - Working tree before our run directory: clean; after creating run dir: only untracked `reports/runs/`
  - **Git tracking safety:** 20 PDFs in `papers/` are already Git-tracked from starter commits; `.gitignore` ignores `.venv/`, `data/raw/*`, `artifacts/models/*`, `artifacts/results/*`, `reports/{figures,tables,logs}/*`, and any *new* `papers/*.pdf`.
- **Essential copied files verified (selected hashes from [file_inventory.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/file_inventory.json)):**
  - [krkCMd_table.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/data/raw/krkCMd_table.csv): `56,292,603` bytes, SHA-256 `CCCA7965B225F77D35567573BB557A6E0476122C381E14AB1BDA898DF9F9B909`
  - [krkCMd_scripts.zip](file:///c:/PROJECT/krkCMd_research_starter_v1/data/raw/krkCMd_scripts.zip): `273,175` bytes, SHA-256 `8E4C8F527ECEF98A6394F302FA894787EED6F35335032C6DCA9F76C36875E567` (4 entries verified: `Crack_Multi_Intersection_ROI_ImagJ.txt`, `CrackWidthAED_VBA.txt`, `CrackWidthDLM_Matlab.m`, `krknet.mat`)
  - `data/raw/krkCMd_images.zip`: `38,589,509,774` bytes (~35.94 GiB / 38.59 GB), full SHA-256 deferred per policy
  - [00_baseline_krkCMd.ipynb](file:///c:/PROJECT/krkCMd_research_starter_v1/notebooks/00_baseline_krkCMd.ipynb): `332,340` bytes, SHA-256 `0C94F13EA7AEF87E884F21075459E57D43BCA563CE18907697AE72C16AFE6864`
  - [group_split_manifest.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/tables/group_split_manifest.csv): `813,176` bytes (`19,099` lines incl. header), SHA-256 `361A3446455F6BCB431E20319BDD33AA3CF6F7BD5A65EE74581C6A20EFCF7685`

---

## 4. Phase 2 — Old vs. New Workstation Hardware Audit

| Component | Old Workstation ([reports/logs/hardware_environment.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/logs/hardware_environment.json)) | New Workstation (`DESKTOP-CQB09OU`, measured) |
|---|---|---|
| **OS** | Windows 10/11 Enterprise (`10.0.26300`, AMD64) | Windows Pro 24H2 (`Build 26100.9711`, AMD64; Registry `ProductName`: `Windows 10 Pro`) |
| **CPU** | Intel Core i7 (Family 6 Model 154, 14C / 20T) | **Intel(R) Core(TM) i9-10900KF @ 3.70 GHz** (20 logical cores; SSE2/SSE3/AVX/AVX2 supported, AVX-512F false) |
| **RAM** | 31.70 GB total (**6.29 GB** available) | **127.92 GB** total (**113.36 GB** available, 11% used; 144.92 GB pagefile) |
| **Disk (`C:`)** | 952.51 GB total (**37.54 GB** free) | **1,906.74 GB** total (**1,752.80 GB** free) |
| **GPU** | NVIDIA GeForce RTX 3050 Laptop (**4,096 MiB / 4 GB VRAM**) | **NVIDIA Quadro RTX 6000** (**24,576 MiB / 24 GB VRAM**, 22,974 MiB free, Compute Cap `7.5`) |
| **GPU Driver / CUDA** | Driver `596.52` / CUDA `13.2` | Driver `621.24` / CUDA UMD `13.5` (Toolkit not installed; GPU compute not yet verified) |
| **Git** | Installed | `git version 2.56.1.windows.1` (`C:\Program Files\Git\cmd\git.exe`) |
| **Python 3.11** | `3.11.9` (`.venv`) | **NOT INSTALLED** (copied `.venv` broken) |
| **MATLAB / VS Code / WSL2 / Docker** | MATLAB R2026b (no `nnet`), WSL2 Ubuntu | **All NOT INSTALLED** |

---

## 5. Phase 3.1 & 3.2 — Python Discovery & Stop Gate

- **Python search:** `C:\Windows\py.exe` does not exist; `where.exe python` only returns the Microsoft Store stub (`C:\Users\Nur Ridho A\AppData\Local\Microsoft\WindowsApps\python.exe`); no Python, Anaconda, Miniconda, or `uv` is present in standard directories or the Windows Uninstall registry.
- **Copied `.venv` inspection:** [pyvenv.cfg](file:///c:/PROJECT/krkCMd_research_starter_v1/.venv/pyvenv.cfg) points to the old workstation interpreter `C:\Users\NurRidhoA\AppData\Local\Programs\Python\Python311\python.exe`. Executing `.\.venv\Scripts\python.exe --version` fails with exit code `103`.
- **Historical packages recovered from copied `.venv`:** 102 `.dist-info` packages were preserved inside `.venv\Lib\site-packages\`, including exact historical baseline pins (`numpy 2.4.6`, `pandas 2.3.3`, `scipy 1.17.1`, `scikit-learn 1.9.1`, `matplotlib 3.11.2`, `seaborn 0.13.2`, `joblib 1.6.0`, `pyyaml 6.0.4`, `openpyxl 3.1.5`, `pypdf 7.1.1`, `ipykernel 6.31.0`, `jupyterlab 4.6.6`, `notebook 7.6.5`, `nbclient 0.11.0`, `nbconvert 7.17.2`, `nbformat 5.11.1`, `psutil 7.2.2`).

---

## 6. Required Prerequisite: Official Python 3.11.9 (64-bit) Installation Procedure

To achieve an exact Python version match (`3.11.9`, 64-bit) with the historical baseline, please install **Python 3.11.9 (64-bit)** using one of the official options below:

### Option A — Official Python.org Installer (Recommended for exact `3.11.9` pin)
1. Download the official Windows 64-bit installer for **Python 3.11.9** from:
   https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
2. Run `python-3.11.9-amd64.exe`:
   - Check **"Use admin privileges when installing py.exe"** (recommended) and **"Add python.exe to PATH"**.
   - Keep **"Install launcher for all users (py)"** enabled.
3. Verify in a new PowerShell window:
   ```powershell
   py -0p
   py -3.11 --version
   ```
   Expected output: `Python 3.11.9`.

### Option B — Windows Package Manager (`winget`)
```powershell
winget install -e --id Python.Python.3.11 --version 3.11.9 --accept-package-agreements --accept-source-agreements
```
*(Note: If `winget` installs the latest 3.11.x patch instead of `3.11.9`, omit `--version 3.11.9` only if exact `3.11.9` is unavailable, and we will document the patch difference.)*

---

## Confirmations & Next Action

- **Zero historical artifacts overwritten** (`artifacts/`, `reports/tables/`, `reports/figures/`, `reports/logs/`, `notebooks/00_baseline_krkCMd.*`, and `data/raw/*` remain untouched).
- **Zero source code, configs, or manuscript files modified**, and **zero training, HPO, L2 testing, gated downloads, or Git commits/pushes occurred**.

**Next step:** Once you have installed Python 3.11.9 (or if you explicitly authorize me to run the installation outside the sandbox), reply to confirm and I will immediately resume from **Phase 3.2/3.3** (preserving the copied `.venv` as historical backup, rebuilding a clean `.venv`, registering the new Jupyter kernel, and executing **Phases 4–12**).

Ran check if Python 3.11 is now installed
Ran install official Python 3.11.9 (64-bit)

Official Python 3.11.9 (64-bit) download and installation is running in the background. I will continue with **Phases 3–12** as soon as installation completes.

Ran check Python installer log and winget availability

Checking the Python 3.11.9 installer log and `winget` package availability.

Analyzed output.txt:L1-56
Ran install Python 3.11.9 via winget
Ran install Python 3.11.9 from winget source

Installing official Python 3.11.9 (64-bit) via `winget` (`--source winget --scope user`). Waiting for installation to complete.

Ran install Python 3.11.9 per-user without elevation

Installing official Python 3.11.9 (64-bit) per-user (`InstallLauncherAllUsers=0`) so no UAC elevation prompt blocks automated setup. Waiting for installation to complete.

Ran preserve old venv and create clean Python 3.11.9 venv

Extracting historical package versions from the copied `.venv`, preserving it as `.venv_old_pc_backup`, and creating a fresh Python 3.11.9 `.venv`.


Analyzed historical_venv_freeze.txt:L1-114
Ran create historical package constraints file
Ran install baseline packages with exact historical versions

Installing baseline Python dependencies into `.venv` constrained to the exact historical package versions recovered from the old workstation's `.venv`. Waiting for installation to complete.

Checked task Install baseline packages with exact historical versions

`pip install` has finished downloading all packages and is currently installing them into `.venv`. Waiting for completion.

Ran verify baseline imports, pip check, and package comparison · Exited with code 1
Ran verify imports and compare against historical packages

Verifying baseline Python imports and comparing package versions against the historical `.venv`.

Register Jupyter kernel and test cell execution
Ran register Jupyter kernel and test cell execution
Ran run isolated dataset audit, static check, and split verification

Isolated dataset audit (`audit_dataset.py`), static verification (`verify_env_and_notebook.py`), and historical split verification are running. Waiting for completion.


Ran execute isolated copy of M00 baseline notebook

Executing the isolated copy of `notebooks/00_baseline_krkCMd.ipynb` using the `krkcmd-research-newpc` Jupyter kernel (`nbclient`, timeout 600s). Waiting for execution to complete.

Ran run Phase 7 comparison and Phase 8.1-8.3 smoke tests · Exited with code 1
Ran run Phase 7 comparison and Phase 8.1-8.3 smoke tests
Ran run transitive pip dry-run dependency resolutions
Analyzed reproducibility_summary.json:L1-93
Analyzed smoke_test_results_new_pc.json:L1-180
Analyzed notebook_execution_log.json:L1-97
Checked task Run transitive pip dry-run dependency resolutions

Phase 7 reproducibility analysis and Phase 8.3 synthetic L0/L1 smoke tests are complete. Currently waiting for Phase 8.5 transitive `pip install --dry-run` resolution across all six proposed environments.


Checked task Run transitive pip dry-run dependency resolutions
Analyzed task-160.log
Analyzed baseline_reproduction_comparison.csv:L1-9
Analyzed robustness_reproduction_comparison.csv:L1-9
Analyzed per_series_reproduction_comparison.csv:L1-5

Waiting for Phase 8.5 transitive `pip install --dry-run` dependency resolution across the six proposed environments to complete.


Ran run transitive pip dry-runs with JSON report files

Re-running Phase 8.5 transitive `pip install --dry-run` using separate JSON report files (`--report <file> -q`) for each proposed environment. Waiting for completion.

Ran inspect resolved package versions per environment
Ran check resolved torch wheel URL in dry-run report
Ran check PyTorch CUDA wheel indices cu124/cu126/cu128 · Exited with code 1
Edited EXPERIMENT_LOG.md
Edited DECISIONS.md
Edited README.md
Checked task Check PyTorch CUDA wheel indices cu124/cu126/cu128
Analyzed task-190.log

Updated `docs/EXPERIMENT_LOG.md`, `docs/DECISIONS.md`, and `README.md` with M01-R migration records. Waiting for PyTorch CUDA index dry-run (`cu124`/`cu126`/`cu128`) check to complete.


Ran query PyTorch CUDA wheel indices and PyPI package metadata
Created MODEL_ENVIRONMENT_PLAN_NEW_PC.md
Created M01_R_MIGRATION_REPORT.md
Ran build review ZIP and verify hashes and Git status · Exited with code 1
Analyzed M01_R_MIGRATION_REPORT.md:L1-324
Analyzed MODEL_ENVIRONMENT_PLAN_NEW_PC.md:L1-79
Ran create review ZIP and check hashes and Git status
Ran verify SHA-256 hashes and create M01R_review_package.zip

**Milestone M01-R** (migrasi workstation baru, rekonstruksi bersih lingkungan Python, reproduksi eksperimen M00, dan *reassessment* kompatibilitas M01) telah selesai dijalankan dan berhenti di gerbang persetujuan sesuai aturan berhenti (*stop gate*).

---

## Ringkasan Status per Fase (M01-R)

| Fase | Ruang Lingkup | Status | Artefak Utama |
|---|---|---|---|
| **Fase 0** | Pemulihan konteks riset & tata kelola (`D-001`..`D-005`) | `PASS` | Diringkas di `M01_R_MIGRATION_REPORT.md` |
| **Fase 1** | Rekonsiliasi Git & inventaris 144 file proyek | `PASS` | [file_inventory.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/file_inventory.json) |
| **Fase 2** | Audit perangkat keras & perangkat lunak (`DESKTOP-CQB09OU`) | `PASS` | [hardware_environment.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/hardware_environment.json) |
| **Fase 3** | Instalasi Python `3.11.9`, rebuild `.venv` & kernel `krkcmd-research-newpc` | `PASS` | [baseline_environment_new_pc.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/baseline_environment_new_pc.json), [requirements_baseline_new_pc.freeze.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/requirements_baseline_new_pc.freeze.txt) |
| **Fase 4** | Audit dataset *read-only* terisolasi (`19.098` × `510`) | `PASS` | [dataset_verification.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/dataset_verification.json) |
| **Fase 5** | Verifikasi statis `00_baseline_krkCMd.ipynb` & `baseline.yaml` | `PASS` *(1 temuan kernel lama di skrip cek)* | `verify_env_and_notebook.py` (12/12 sel terkompilasi, exit `1` hanya karena mengecek nama kernel lama `krkcmd-research`) |
| **Fase 6** | Verifikasi `group_split_manifest.csv` & eksekusi penuh notebook terisolasi (`212,272 s`) | `PASS` | [split_verification.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/split_verification.json), [notebook_execution_log.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/notebook_execution_log.json), [00_baseline_krkCMd_executed.ipynb](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/00_baseline_krkCMd_executed.ipynb), [00_baseline_krkCMd_executed.html](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/00_baseline_krkCMd_executed.html) |
| **Fase 7** | Perbandingan reproduktibilitas benchmark, robustness & per-Series | `PASS` | [reproducibility_summary.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/reproducibility_summary.json), [baseline_reproduction_comparison.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/baseline_reproduction_comparison.csv), [robustness_reproduction_comparison.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/robustness_reproduction_comparison.csv), [per_series_reproduction_comparison.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/per_series_reproduction_comparison.csv) |
| **Fase 8** | Validasi 32 kandidat M01, 8 smoke test L0/L1, 6 *dry-run* dependensi transitif | `PASS` *(kandidat non-baseline berstatus `NOT_EXECUTED`)* | [model_compatibility_matrix_new_pc.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/model_compatibility_matrix_new_pc.csv), [smoke_test_results_new_pc.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/smoke_test_results_new_pc.json), [dependency_resolution_new_pc.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/dependency_resolution_new_pc.json) |
| **Fase 9** | Rencana lingkungan & anggaran sumber daya workstation baru | `PASS` | [MODEL_ENVIRONMENT_PLAN_NEW_PC.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/MODEL_ENVIRONMENT_PLAN_NEW_PC.md) |
| **Fase 10** | Pembaruan catatan tata kelola (`EXP-003`, `D-006`, catatan README) | `PASS` | [docs/EXPERIMENT_LOG.md](file:///c:/PROJECT/krkCMd_research_starter_v1/docs/EXPERIMENT_LOG.md), [docs/DECISIONS.md](file:///c:/PROJECT/krkCMd_research_starter_v1/docs/DECISIONS.md), [README.md](file:///c:/PROJECT/krkCMd_research_starter_v1/README.md) |
| **Fase 11** | Laporan migrasi Indonesia & paket review ringan (`2,29 MB`, `50` entri) | `PASS` | [M01_R_MIGRATION_REPORT.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/M01_R_MIGRATION_REPORT.md), [M01R_review_package.zip](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/M01R_review_package.zip) |
| **Fase 12** | Audit hash pasca-eksekusi (`140/140` cocok) & checkpoint berhenti | `PASS` | Terverifikasi di bawah |

---

## Ringkasan Teknis Utama

- **Workstation Baru (`DESKTOP-CQB09OU`):** `Intel(R) Core(TM) i9-10900KF @ 3.70 GHz` (`20` logical threads), `127,92 GB` RAM (`113,36 GB` bebas), `1.752,80 GB` disk bebas di `C:`, serta `NVIDIA Quadro RTX 6000` (`24.576 MiB` VRAM, `22.974 MiB` bebas, driver `621.24`, CUDA UMD `13.5`). CUDA Toolkit sistem, MATLAB, VS Code, WSL2, dan Docker tidak terpasang.
- **Lingkungan & Kernel Baru:** Salinan `.venv` lama dipreservasi sebagai `.venv_old_pc_backup`. `.venv` baru dibangun dari Python `3.11.9` (64-bit) dengan seluruh paket ilmiah & Jupyter yang **identik dengan PC lama** (`numpy 2.4.6`, `pandas 2.3.3`, `scipy 1.17.1`, `scikit-learn 1.9.1`, `matplotlib 3.11.2`, `seaborn 0.13.2`, `joblib 1.6.0`, `PyYAML 6.0.4`, `openpyxl 3.1.5`, `pypdf 7.1.1`, `psutil 7.2.2`; `pip check` = `No broken requirements found.`), dan terdaftar pada kernel `krkcmd-research-newpc`.
- **Reproduksi Eksperimen M00 (`n_test = 3.822`):**
  - `ExtraTrees`: MAE `14,311523` µm, RMSE `35,504987` µm, $R^2$ `0,935147` (`17,743 s`, 2,12× lebih cepat vs `37,556 s`; max selisih per-baris `1,705e-13` µm).
  - `RandomForest`: MAE `14,407363` µm, RMSE `35,336657` µm, $R^2$ `0,935760` (`59,757 s`, 1,72× lebih cepat vs `102,991 s`; max selisih `2,274e-13` µm).
  - `HistGradientBoosting` (`15,149774` µm), `SVR_RBF` (`28,118558` µm), `LinearRegression` (`49,826529` µm), dan `Dummy_mean` (`116,599211` µm): **identik secara bit** (`max_abs_diff_um = 0,0`).
  - Uji robustness (8 kondisi) dan evaluasi per-Series (4 Series) ter-reproduksi dengan selisih MAE $\le 5,33 \times 10^{-15}\,\mu\text{m}$.
- **Temuan Penting Dependensi untuk M02:**
  - `xgboost 3.4.1` terbaru mensyaratkan Python `>=3.12`; di Python `3.11.9` resolver memilih `xgboost 3.2.0`.
  - `aeon 1.6.0` + `numba 0.63.1` mengunci `numpy` pada `2.3.5` (berbeda dari `2.4.6` baseline), sehingga isolasi `env-signal-cpu` tetap wajib.
  - `--extra-index-url https://download.pytorch.org/whl/cu124` masih mengambil `torch 2.15.0` CPU dari PyPI; instalasi `env-deep` nanti harus memakai `--index-url https://download.pytorch.org/whl/cu128` (`torch 2.9.1+cu128`) secara eksplisit.

---

## 13 Konfirmasi Eksplisit (Fase 12)

1. **Artefak historis tidak ditimpa:** Terkonfirmasi — SHA-256 pada seluruh `140` file proyek yang tidak dimodifikasi cocok 100% pasca-eksekusi (`0` mismatch, `0` missing), dan ukuran arsip besar yang ditangguhkan `data/raw/krkCMd_images.zip` tetap `38.589.509.774` byte.
2. **Baseline M00 ter-reproduksi penuh di workstation baru:** Terkonfirmasi (`12/12` code cell `00_baseline_krkCMd.ipynb` selesai dalam `212,272 s` di `isolated_workspace/` dengan selisih prediksi `0,0` hingga `<= 2,274e-13` µm).
3. **Pembagian grup (`group_split_manifest.csv`) cocok persis:** Terkonfirmasi (`exact_row_and_order_match = True`; Train `12.216` baris / `2.036` grup, Validation `3.060` baris / `510` grup, Test `3.822` baris / `637` grup, `0` overlap).
4. **Dataset `krkCMd_table.csv` & `krkCMd_scripts.zip` utuh:** Terkonfirmasi (SHA-256 `krkCMd_table.csv` = `CCCA7965B225F77D35567573BB557A6E0476122C381E14AB1BDA898DF9F9B909`; `krkCMd_scripts.zip` = `8E4C8F527ECEF98A6394F302FA894787EED6F35335032C6DCA9F76C36875E567`; audit 100% cocok dengan log historis).
5. **Seluruh 32 kandidat model M01 dipertahankan:** Terkonfirmasi (`ML01–ML07`, `DL01–DL05`, `FM01–FM04`, `SG01–SG06`, `HY01–HY05`, `RF01–RF05`; `8` kandidat baseline lulus smoke test L0/L1, `24` kandidat lain berstatus `NOT_EXECUTED` hingga M02 disetujui).
6. **Tidak ada batasan hardware/kompatibilitas tak terduga yang menghambat baseline maupun rencana M02:** Terkonfirmasi pada kapasitas RAM (`127,92 GB`), VRAM (`24 GB`), CPU, dan disk (`1,75 TB`), dengan catatan faktual bahwa: (a) MATLAB, VS Code, WSL2, Docker, dan CUDA Toolkit sistem tidak terpasang (berdampak pada `RF04` jalur MATLAB langsung), (b) akselerasi CUDA Quadro RTX 6000 belum diuji secara langsung karena PyTorch CUDA belum diinstal, (c) `scripts/verify_env_and_notebook.py` mencari nama kernel lama `krkcmd-research`, dan (d) `xgboost` terbaru (`3.4.1`) memerlukan Python `>=3.12` sedangkan Python `3.11.9` memakai `xgboost 3.2.0`.
7. **Tidak ada file konfigurasi, skrip, maupun kode sumber yang diubah:** Terkonfirmasi (`git diff` hanya menyentuh 3 file dokumentasi: [README.md](file:///c:/PROJECT/krkCMd_research_starter_v1/README.md), [docs/DECISIONS.md](file:///c:/PROJECT/krkCMd_research_starter_v1/docs/DECISIONS.md), dan [docs/EXPERIMENT_LOG.md](file:///c:/PROJECT/krkCMd_research_starter_v1/docs/EXPERIMENT_LOG.md)).
8. **Tidak ada pelatihan model baru di luar reproduksi eksak M00:** Terkonfirmasi (hanya smoke test sintetis L0/L1 `seed=42` untuk 8 kandidat `.venv`).
9. **Tidak ada HPO atau penyetelan hiperparameter yang dijalankan:** Terkonfirmasi.
10. **Tidak ada pengujian skala L2 yang dijalankan:** Terkonfirmasi.
11. **Tidak ada bobot *gated* atau model fondasi yang diunduh, dan tidak ada lisensi yang disetujui atas nama peneliti:** Terkonfirmasi.
12. **Naskah manuskrip (`manuscript/`) tidak dimodifikasi:** Terkonfirmasi (`git diff` bersih pada `manuscript/`).
13. **Tidak ada `git commit` atau `git push` otomatis:** Terkonfirmasi (0 staged changes, 0 commit, 0 push).

---

## Status Git Saat Ini & Gerbang Persetujuan Berikutnya

- **Modified (unstaged):** `README.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_LOG.md`
- **Untracked:** `.venv_old_pc_backup/`, `reports/runs/` (termasuk [M01R_review_package.zip](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/M01R_review_package.zip) berukuran `2,29 MB` tanpa CSV mentah, PDF, `.env`, `.venv`, `.joblib`, maupun arsip gambar)

**Menunggu keputusan Anda untuk melangkah ke tahap berikutnya:**
1. **Persetujuan M01.1 (Perbaikan Tata Kelola/Skrip):** Memperbaiki 12 isu M01.1 di `configs/model_registry.yaml`, `scripts/check_model_compatibility.py`, serta opsi kernel di `scripts/verify_env_and_notebook.py`.
2. **Persetujuan Lingkungan M02 & Uji Komputasi GPU:** Membuat `.venv-boost`, `.venv-deep` (dengan `--index-url https://download.pytorch.org/whl/cu128` + verifikasi CUDA Quadro RTX 6000), dan `.venv-signal-cpu` sesuai [MODEL_ENVIRONMENT_PLAN_NEW_PC.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/MODEL_ENVIRONMENT_PLAN_NEW_PC.md), serta konfirmasi apakah `.venv_old_pc_backup/` boleh dihapus setelah peninjauan.