Analyzed AGENT.md:L1-200
Analyzed baseline.yaml:L1-25
Ran list src and scripts directories
Analyzed metrics.py:L1-154
Analyzed experiment_runner.py:L1-80
Analyzed perturbations.py:L1-96
Analyzed M03_PERTURBATION_REGISTER.yaml:L1-25
Created m04a_preflight_probe.py
Ran run M04A preflight probe and create run directory
Analyzed DECISIONS.md:L55-61
Edited DECISIONS.md
Checked task Run M04A preflight probe and create run directory

`D-009A`–`D-009J` have been appended to `docs/DECISIONS.md` (preserving `D-009 PROPOSED`). Waiting for `task-713` (`m04a_preflight_probe.py`) to finish.

Analyzed M04A_SPLIT_VERIFICATION.json:L1-40
Analyzed estimator_signatures_probe.json:L1-250
Analyzed estimator_signatures_probe.json:L250-335
Ran check raw CSV column order
Created M03_APPROVED_DECISION_SNAPSHOT.md
Created M03_CORRECTIVE_PREFLIGHT.md
Created M04A_SCIENTIFIC_CONFIGURATIONS.yaml
Created M04A_EXECUTION_MANIFEST.yaml
Edited metrics.py
Writing experiment_runner.py
Created m04a_data.py
Edited experiment_runner.py
Ran find TabR adapter lines in m02c_adapters.py
Analyzed m02c_adapters.py:L465-560
Analyzed m02c_adapters.py:L595-690
Ran find classes in m02b_adapters.py
Analyzed m02b_adapters.py:L256-300
Analyzed m02b_adapters.py:L391-430
Created m04a_scientific_worker.py
Created run_m04a_screening.py
Canceled run M04A Stage A pipeline pilot (5 models)
Analyzed runner_result.json:L1-14
Killed task Run M04A Stage A pipeline pilot (5 models)
Edited m04a_scientific_worker.py
Edited run_m04a_screening.py
Ran run M04A Stage A pipeline pilot (5 models)

`task-762` is running the M04A Stage A pipeline pilot (`RF01` already `PASS`, continuing with `ML01`, `DL01`, `SG01`, `FM03`). Waiting for completion notification.

Analyzed worker_result.json:L1-41
Analyzed worker_result.json:L1-41
Ran run M04A Stage B (17 models, excluding FM04)

`task-768` is running M04A Stage B (17 models: `RF02`, `ML02–ML07`, `DL02–DL05`, `SG02–SG06`, `RF05`; `FM04` will run separately afterwards). Waiting for completion notification.

Checked task Run M04A Stage B (17 models, excluding FM04)

`task-768` has already passed `RF02`, `ML02–ML07`, and `DL02–DL05`, and is currently running `SG02` (`ResNetRegressor` CPU-only TensorFlow, 50 epochs). Waiting for `task-768` to finish.

Ran run M04A FM04 (TabDPT) under 3600s supervision
Analyzed runner_result.json:L1-14
Ran check TabDPTRegressor init and predict signatures

Checking `TabDPTRegressor` `__init__` and `predict` signatures (`task-782`).

Edited m04a_scientific_worker.py
Ran run M04A FM04 (TabDPT) under 3600s supervision
Created test_m04a_pipeline.py
Created aggregate_m04a_results.py
Checked task Run M04A FM04 (TabDPT) under 3600s supervision
Ran run all unit tests including M04A pipeline tests
Created build_m04a_notebook.py
Ran build M04A analysis notebook
Ran check current GPU VRAM usage
Edited M04A_SCIENTIFIC_CONFIGURATIONS.yaml
Edited m04a_scientific_worker.py
Ran run M04A FM04 (TabDPT) with explicit batch_size=128

`task-804` (`FM04` `TabDPTRegressor` with explicit `batch_size=128`, `context_size=2048`, `n_ensembles=8`) is running under the 3,600s watchdog. Waiting for completion notification before aggregating all M04A results and executing the analysis notebook.

Error: API error (attempt 1): request failed: Post "https://daily-cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse": dial tcp: lookup daily-cloudcode-pa.googleapis.com: no such host (Error ID: e1e2d1db-3c86-4e64-a0c3-29594758cb7b-807)

Checked task Run M04A FM04 (TabDPT) with explicit batch_size=128

`task-804` (`FM04`) is still running (~55 minutes elapsed, under the 3,600s watchdog cap). Waiting for completion notification.

Ran aggregate M04A results and execute analysis notebook

`task-813` aggregated all 20 successful M04A models and is executing `01_M04A_scientific_screening_analysis.ipynb` and exporting its HTML report. Waiting for completion notification.


Analyzed M04A_VALIDATION_METRICS_RAW.csv:L1-21
Analyzed M04A_VALIDATION_METRICS_NONNEGATIVE.csv:L1-21
Analyzed M04A_REFERENCE_VALIDATION_METRICS.csv:L1-3
Analyzed M04A_RESOURCE_USAGE.csv:L1-21
Analyzed M04A_MODEL_STATUS.csv:L1-33
Analyzed M04A_METRIC_RECOMPUTATION.json:L1-20
Created M04A_PROPOSED_FINALIST_SHORTLIST.md
Created M04A_SCIENTIFIC_SCREENING_REPORT.md
Created result_run_11_M04A.md
Edited EXPERIMENT_LOG.md
Created m04a_finalize.py
Ran finalize M04A integrity, unit tests, review ZIP, and git status

`task-831` is finalizing M04A before/after integrity checks, unit tests, `M04A_review_package.zip` + SHA-256 manifest, and `git status`. Waiting for completion notification.

# Laporan Hasil Run 11 — M04A: Screening Ilmiah Pertama pada Data `krkCMd` Asli

Milestone **M04A** (`M04A_20261126_145808_DESKTOP-CQB09OU`) telah **SELESAI** dan berhenti pada gerbang persetujuan peneliti sebelum M04B/M05.

---

## 1. Status Fase & Ringkasan Kandidat (`20 / 23` `PASS`, `3 / 23` `FAILED`)

- **Preflight Korektif M03:** **PASS** ([M03_CORRECTIVE_PREFLIGHT.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M04A_20261126_145808_DESKTOP-CQB09OU/M03_CORRECTIVE_PREFLIGHT.md)) — mengonfirmasi dataset mentah `19.098 x 510` (selisih `512` di M03 akibat 2 kolom turunan in-memory), `target: MANwidth`, `subsample_freq=1` di LightGBM, pelabelan `single_member_config` (`n_regressors=1`) pada `SG03`/`SG04`, rekonsiliasi `RF05` `max_epochs=50`, serta penghapusan batas `500` fitur yang belum terverifikasi pada `FM01`/`FM02`.
- **Tata Kelola Keputusan:** `D-009A` s.d. `D-009J` dicatat sebagai `APPROVED BY RESEARCHER` di [DECISIONS.md](file:///c:/PROJECT/krkCMd_research_starter_v1/docs/DECISIONS.md) (mempertahankan `D-009 PROPOSED` utuh) dan di [M03_APPROVED_DECISION_SNAPSHOT.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M04A_20261126_145808_DESKTOP-CQB09OU/M03_APPROVED_DECISION_SNAPSHOT.md).
- **20 Kandidat `PASS`** (`3.060` prediksi validasi Protocol A masing-masing, selisih rekomputasi `0.0`):
  `ML01`, `FM03`, `ML02`, `ML04`, `ML06`, `ML05`, `ML03`, `DL03`, `DL02`, `RF05`, `SG06`, `DL05`, `DL04`, `DL01`, `SG05`, `SG04`, `ML07`, `SG01`, `RF02`, `RF01`.
- **3 Kandidat `FAILED` Batas Sumber Daya (`3.600 dtk`):**
  - `SG02` (`ResNetRegressor`, TF CPU-only): `WALL_CLOCK_TIMEOUT (3600s)`
  - `SG03` (`InceptionTimeRegressor`, TF CPU-only, `n_regressors=1`): `WALL_CLOCK_TIMEOUT (3600s)`
  - `FM04` (`TabDPTRegressor`, `.venv-foundation`): Percobaan 1 `TypeError` (`seed` di `predict`), Percobaan 2 (`_r2`) `GPU_VRAM_BUDGET_EXCEEDED (22339.0 MiB > 19291.6 MiB)` saat `batch_size=None`, Percobaan 3 (`_r3`, `batch_size=128`) `WALL_CLOCK_TIMEOUT (3600s) [SUSPEND_DETECTED]` pada `3.601,484 dtk`.
- **9 ID Non-M04A Dipertahankan:** `FM01`, `FM02` (`BLOCKED_LICENSE`), `RF03`, `RF04` (`REFERENCE_PENDING_IMPL`), `HY01–HY05` (`DESIGN_REQUIRED`).

---

## 2. Leaderboard Validasi Protocol A (`n=3.060`, Ranking MAE Raw)

| Peringkat | Model | Raw MAE (µm) | Raw RMSE (µm) | Lin's CCC | R² | Clipped MAE (µm) | Pred. Negatif | Waktu Total (dtk) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `ML01` Extra Trees | **14,25** | 28,94 | 0,9796 | 0,9606 | 14,25 | 0 | 32,20 |
| 2 | `FM03` TabICLv2 (zero-shot) | **14,39** | 29,17 | 0,9794 | 0,9600 | 14,38 | 291 | 83,25 |
| 3 | `ML02` Random Forest | **14,56** | 29,87 | 0,9783 | 0,9580 | 14,56 | 0 | 95,88 |
| 4 | `ML04` XGBoost | **14,74** | 29,68 | 0,9786 | 0,9586 | 14,62 | 256 | 20,74 |
| 5 | `ML06` CatBoost | **14,98** | 29,05 | 0,9796 | 0,9603 | 14,86 | 203 | 29,48 |
| 6 | `ML05` LightGBM | **15,00** | 29,65 | 0,9787 | 0,9586 | 14,86 | 255 | 9,39 |
| 7 | `ML03` HistGradientBoosting | **15,24** | 30,15 | 0,9779 | 0,9572 | 15,16 | 143 | 9,19 |
| 8 | `DL03` RealMLP | **16,66** | 31,41 | 0,9762 | 0,9536 | 16,66 | 0 | 119,34 |
| 9 | `DL02` FT-Transformer | **16,73** | 31,36 | 0,9768 | 0,9537 | 16,26 | 578 | 188,22 |
| 10 | `RF05` DLM retrained | **17,49** | 33,68 | 0,9728 | 0,9466 | 17,45 | 25 | 22,95 |
| 11 | `SG06` MultiROCKET-HYDRA | **22,33** | 33,46 | 0,9730 | 0,9473 | 20,61 | 340 | 347,88 |
| 12–20 | `DL05` (`23,52`), `DL04` (`23,95`), `DL01` (`24,21`), `SG05` (`26,25`), `SG04` (`27,72`), `ML07` (`29,72`), `SG01` (`41,88`), `RF02` (`52,45`), `RF01` (`120,27`) | — | — | — | — | — | — | — |

**Pembanding Historis (Stage C — Provenance Terpisah):** `DLMwidth` (`MAE=14,59 µm`, `RMSE=27,14 µm`, `CCC=0,9820`) dan `AEDwidth` (`MAE=33,21 µm`, `RMSE=52,19 µm`, `CCC=0,9288`).

---

## 3. Artefak & Verifikasi Kualitas

- **Laporan & Shortlist:** [result_run_11_M04A.md](file:///c:/PROJECT/krkCMd_research_starter_v1/for_review/result_run_11_M04A.md), [M04A_SCIENTIFIC_SCREENING_REPORT.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M04A_20261126_145808_DESKTOP-CQB09OU/M04A_SCIENTIFIC_SCREENING_REPORT.md), [M04A_PROPOSED_FINALIST_SHORTLIST.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M04A_20261126_145808_DESKTOP-CQB09OU/M04A_PROPOSED_FINALIST_SHORTLIST.md)
- **Notebook Ter-eksekusi & HTML:** [01_M04A_scientific_screening_analysis.ipynb](file:///c:/PROJECT/krkCMd_research_starter_v1/notebooks/01_M04A_scientific_screening_analysis.ipynb), [01_M04A_scientific_screening_analysis_executed.ipynb](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M04A_20261126_145808_DESKTOP-CQB09OU/01_M04A_scientific_screening_analysis_executed.ipynb), [01_M04A_scientific_screening_analysis.html](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M04A_20261126_145808_DESKTOP-CQB09OU/01_M04A_scientific_screening_analysis.html)
- **Integritas & Unit Test:** `ENVS_UNCHANGED=True` (8 `.venv*`), `FILES_UNCHANGED=True` (7 file terproteksi), `UNIT_TESTS_RC=0` (`41` unit tests `OK`, [M04A_UNIT_TEST_RESULTS.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M04A_20261126_145808_DESKTOP-CQB09OU/M04A_UNIT_TEST_RESULTS.txt)).
- **Review ZIP:** [M04A_review_package.zip](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M04A_20261126_145808_DESKTOP-CQB09OU/M04A_review_package.zip) (`171` file, `6,51 MB`, SHA-256 `F119B824A9616F9232995927B13F7A635FDD494298BF1FE56E1AC64B7D5175F9`, `ZIP_INTEGRITY=OK`).

---

## TINDAKAN MANUAL PENELITI

1. **Instalasi Software:** Tidak diperlukan. Seluruh 8 `.venv*` tidak berubah.
2. **Eksekusi Notebook Manual:** Tidak diperlukan (`01_M04A_scientific_screening_analysis.ipynb` sudah dieksekusi otomatis via `krkcmd-research-newpc`).
3. **Akses Checkpoint:** Jika ingin membuka blokir `FM01`/`FM02` sebelum M04B, setujui lisensi PriorLabs di `https://ux.priorlabs.ai` dan setel `TABPFN_TOKEN`.
4. **Aksi Git Aman:** Tidak ada `git commit`/`git push` otomatis; tinjau perubahan lokal (termasuk 2 file sementara `.keras` di root dari `aeon` TF) sebelum commit manual.
5. **File untuk Diunggah ke ChatGPT:**
   1. `c:\PROJECT\krkCMd_research_starter_v1\for_review\result_run_11_M04A.md`
   2. `c:\PROJECT\krkCMd_research_starter_v1\reports\runs\M04A_20261126_145808_DESKTOP-CQB09OU\M04A_review_package.zip`

---

## Status Akhir Gerbang Penghentian (Stop Gate)

- **M03 Corrective Preflight:** `PASS`
- **M04A Stage A Pilot & Stage B Screening:** `PARTIAL` (`20/23 PASS`, `3/23 FAILED` timeout `3.600 dtk`)
- **M04A Stage C Historical References:** `PASS`
- **Notebook Execution, Unit Tests, Integrity & ZIP:** `PASS`
- **Test-Partition Sealing / Protocol B / LOSO / HPO / Robustness / Custom HY01–05 / Git Commit:** `NOT_EXECUTED` (terkonfirmasi 0 pelanggaran)

**Berhenti setelah M04A** — menunggu tinjauan dan persetujuan peneliti sebelum M04B atau M05.