# Laporan Provisioning, Validasi Runtime & Uji Kapasitas M02A

**Proyek:** `krkCMd_research_starter`  
**Run ID:** `M02A_20261125_074616_DESKTOP-CQB09OU`  
**Tanggal:** 2026-11-25  
**Workstation:** `DESKTOP-CQB09OU`  
**Git HEAD Awal:** `d48510636da2fd62d355174d15aa1226c1b0c621`  

---

## 1. Hasil Preflight M01.1

Pemeriksaan preflight tersimpan di [M01_1_PREFLIGHT_VERIFICATION.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/M01_1_PREFLIGHT_VERIFICATION.json):
- **Terverifikasi PASS:** `32` ID unik di `configs/model_registry.yaml`, pembagian historis `12.216 / 3.060 / 3.822`, `501` fitur `x1..x501`, target `MANwidth`, kolom pembanding `DLMwidth` & `AEDwidth`, pemisahan status `DL01` (`SMOKE_TEST_PASS_PROTOTYPE`) dan `RF03` (`CONDITIONAL`), pelestarian bukti M00/M01/M01-R/M01.1, `EXP-003` di `docs/EXPERIMENT_LOG.md`, serta `terminate_process_tree` di `scripts/resource_policy.py`.
- **Unit test awal (.venv baseline):** `13/13` tests lulus sebelum provisioning.
- **Catatan non-blocking M01.1:** `scripts/check_model_compatibility.py` historis masih memiliki daftar kandidat Python *hardcoded* (sedangkan matriks M01.1 dan M02A membaca `configs/model_registry.yaml` secara langsung).

---

## 2. Pengukuran Hardware & Anggaran Sumber Daya (GiB)

Tersimpan di [hardware_environment_M02A.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/hardware_environment_M02A.json):
- **CPU:** Intel Core i9-10900KF (`10` physical cores, `20` logical threads), batas M02A `max_cpu_threads = 16`, `max_concurrent_workers = 1`.
- **RAM:** `127.921 GiB` total, `107.08 GiB` tersedia $\to$ `ram_budget_gib = 64.0 GiB` (`65.536 MiB`).
- **Disk (`C:`):** `1,906.739 GiB` total, `1,746.22 GiB` bebas $\to$ `env_cache_budget_gib = 30.0 GiB`.
- **Mode Eksekusi M02A:** `CPU_ONLY` (GPU Quadro RTX 6000 `24.0 GiB` tidak diinisialisasi pada M02A).

---

## 3. Lingkungan Terisolasi & Paket yang Diinstal

Kedua lingkungan dibuat menggunakan interpreter dasar **Python 3.11.9** (`C:\Users\Nur Ridho A\AppData\Local\Programs\Python\Python311\python.exe`) setelah *dry-run* transitif ([dependency_resolution_boost.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/dependency_resolution_boost.json), [dependency_resolution_signal_cpu.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/dependency_resolution_signal_cpu.json)):

1. **`.venv-boost`** ([requirements_boost.lock.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/requirements_boost.lock.txt), [requirements_boost.freeze.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/requirements_boost.freeze.txt)):
   - `50` paket diinstal dalam `108,56 s`, `lock_match = true`, `pip check`: `No broken requirements found.`
   - Versi inti: `xgboost==3.2.0`, `lightgbm==4.7.0`, `catboost==1.2.10`, `numpy==2.4.6`, `pandas==3.1.1`, `scipy==1.17.1`, `scikit-learn==1.9.1`, `joblib==1.6.0`, `psutil==7.2.2`, `PyYAML==6.0.4`, `ipykernel==7.4.0`, `threadpoolctl==3.8.0`.
2. **`.venv-signal-cpu`** ([requirements_signal_cpu.lock.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/requirements_signal_cpu.lock.txt), [requirements_signal_cpu.freeze.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/requirements_signal_cpu.freeze.txt)):
   - `42` paket diinstal dalam `90,31 s`, `lock_match = true`, `pip check`: `No broken requirements found.`
   - Versi inti: `aeon==1.6.0`, `numba==0.63.1`, `llvmlite==0.46.0`, `numpy==2.3.5` (dipertahankan sesuai constraint Numba tanpa dipaksa ke `2.4.6`), `pandas==3.0.6`, `scipy==1.17.1`, `scikit-learn==1.9.1`, `ipykernel==7.4.0`.

---

## 4. Verifikasi Kernel Jupyter

Tersimpan di [kernel_verification_M02A.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/kernel_verification_M02A.json):
- **`krkcmd-boost`** (`Python (krkCMd - Boosting)`): mengarah ke `.venv-boost\Scripts\python.exe`, uji `nbclient` **PASS** (`NB_OK ... 3.2.0`).
- **`krkcmd-signal-cpu`** (`Python (krkCMd - CPU Signal)`): mengarah ke `.venv-signal-cpu\Scripts\python.exe`, uji `nbclient` **PASS** (`NB_OK ... 1.6.0`).
- Kernel baseline `krkcmd-research-newpc` tetap utuh.

---

## 5. Hasil Uji L0, L1, L2A, L2B, L2C & Penggunaan Sumber Daya

Seluruh pengujian dijalankan pada data sintetis deterministik (`seed=42`, `501` fitur; **tanpa data `krkCMd` asli**) dalam subprocess terisolasi dengan batas `16` thread dan timeout `300 s` ([smoke_test_results_M02A.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/smoke_test_results_M02A.json), [capacity_test_results_M02A.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/capacity_test_results_M02A.json), [resource_usage_M02A.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/resource_usage_M02A.csv)):

| ID | Estimator & Konfigurasi Uji Terbatas | L0 | L1 (100→20) + Serialisasi `joblib` | L2A (1.000→200) | L2B (4.096→1.024) | L2C (12.216→3.822) | Peak RSS L2C | Status Akhir M02A |
|---|---|---|---|---|---|---|---|---|
| **ML04** | `xgboost.sklearn.XGBRegressor` (`n_estimators=20, max_depth=4, hist, cpu`) | `PASS` | `PASS` (`0,178 s`, diff `0,0`, 0 neg) | `PASS` (`0,34 s`) | `PASS` (`0,47 s`) | `PASS` (`0,80 s` fit / `0,002 s` pred) | `375,25 MB` | **`SCALE_CHECK_PASS`** |
| **ML05** | `lightgbm.sklearn.LGBMRegressor` (`n_estimators=20, max_depth=6, cpu`) | `PASS` | `PASS` (`0,029 s`, diff `0,0`, 0 neg) | `PASS` (`0,23 s`) | `PASS` (`0,32 s`) | `PASS` (`0,53 s` fit / `0,002 s` pred) | `250,82 MB` | **`SCALE_CHECK_PASS`** |
| **ML06** | `catboost.core.CatBoostRegressor` (`iterations=20, depth=6, CPU`) | `PASS` | `PASS` (`0,366 s`, diff `0,0`, 0 neg) | `PASS` (`0,68 s`) | `PASS` (`0,72 s`) | `PASS` (`0,90 s` fit / `0,007 s` pred) | `309,60 MB` | **`SCALE_CHECK_PASS`** |
| **SG05** | `aeon...RocketRegressor` (`n_kernels=2000`, reshape `(n,1,501)`, dim transformasi=`4.000`) | `PASS` | `PASS` (`0,290 s` JIT / `0,121 s` post-JIT, diff `0,0`, 0 neg) | `PASS` (`1,41 s`) | `PASS` (`22,56 s`) | `PASS` (`46,01 s` fit / `4,09 s` pred) | `1.808,91 MB` | **`SCALE_CHECK_PASS`** *(konfigurasi terbatas 2.000 kernel)* |
| **SG06** | `aeon...MultiRocketHydraRegressor` (`n_kernels=8`) | **`FAILED`** | `NOT_EXECUTED` | `NOT_EXECUTED` | `NOT_EXECUTED` | `NOT_EXECUTED` | — | **`BLOCKED`** *(membutuhkan `torch`)* |

### Temuan Kegagalan `SG06` (`MultiRocketHydraRegressor`)
- Kelas `aeon.regression.convolution_based.MultiRocketHydraRegressor` tersedia di `aeon==1.6.0`, tetapi inisialisasi L0 melempar `ModuleNotFoundError`: `MultiRocketHydraRegressor requires package 'torch' to be present in the python environment`.
- Sesuai batasan otorisasi M02A (larangan instalasi PyTorch dan larangan substitusi estimator ke `MultiRocketRegressor`/`HydraRegressor`), **`SG06` dibiarkan berstatus `BLOCKED` pada lingkungan CPU-only ini dan ditangguhkan ke M02B (`.venv-deep` / env bertorch).**

---

## 6. Hasil Unit Test & Status 32 Kandidat

- **Unit tests ([unit_test_results_M02A.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/unit_test_results_M02A.txt)):**
  - `.venv`: `20/20` tests `OK` (`1,108 s`) — mencakup kontrak YAML, resource policy, verifikasi kernel portabel, serta `tests/test_m02a_adapters.py` (penolakan fitur != 501, NaN/Inf, bentuk prediksi salah, adaptasi 2D→3D dengan pelestarian urutan `x1..x501`, dan identitas `SG06`).
  - `.venv-boost` & `.venv-signal-cpu`: `7/7` tests `test_m02a_adapters.py` `OK` pada masing-masing interpreter.
- **Matriks 32 kandidat:** Tersimpan di [model_compatibility_matrix_M02A.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/model_compatibility_matrix_M02A.csv). `4` kandidat M02A (`ML04`, `ML05`, `ML06`, `SG05`) mencapai `SCALE_CHECK_PASS`, `1` kandidat (`SG06`) berstatus `BLOCKED` (kurang `torch`), `27` kandidat lain dipreservasi, dan **`0` kandidat berstatus `APPROVED`** untuk eksperimen riset.

---

## 7. Pelestarian Lingkungan Baseline, Berkas Terubah & Status Git

- **Baseline `.venv` tetap beku & identik:** `pip check` bersih, `baseline_freeze_sha256` & hash `krkCMd_table.csv` serta `group_split_manifest.csv` terverifikasi tidak berubah.
- **Berkas Baru:** `src/__init__.py`, `src/models/__init__.py`, `src/models/m02a_adapters.py`, `src/evaluation/__init__.py`, `src/evaluation/m02a_compat_worker.py`, `tests/test_m02a_adapters.py`, dan seluruh artefak di `reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/` (termasuk `M02A_review_package.zip`).
- **Berkas Diperbarui:** `configs/model_registry.yaml` (`SG06` status `BLOCKED`), `docs/MODEL_REGISTRY.md`, `docs/MODEL_ENVIRONMENT_PLAN.md`, `docs/EXPERIMENT_LOG.md` (`EXP-004`).
- **Tidak diubah:** `notebooks/00_baseline_krkCMd.ipynb`, `manuscript/*`, `data/raw/*`, `.venv_old_pc_backup/`, dan riwayat M00/M01/M01-R/M01.1. Tidak ada `git commit` atau `git push`.

---

## 8. Usulan Langkah Berikutnya (M02B)

Setelah review M02A, tahap berikutnya adalah **M02B** untuk membuat `.venv-deep` (Python `3.11.9` + `torch==2.9.1+cu128` dengan `--index-url https://download.pytorch.org/whl/cu128`) guna memverifikasi komputasi GPU **Quadro RTX 6000 (`sm_75`)**, menguji kandidat neural/deep learning (`DL01`–`DL05`, `SG01`, `HY03`–`HY04`, `RF05`), serta menguji ulang `SG06` (`MultiRocketHydraRegressor`) yang membutuhkan `torch`.

---

### TINDAKAN MANUAL PENELITI

- **Tindakan manual wajib saat ini:** **Tidak ada.** Seluruh pembuatan lingkungan, instalasi paket, registrasi kernel, uji L0/L1/L2, dan unit test telah dijalankan otomatis.
- **Eksekusi notebook manual:** **Tidak perlu** menjalankan notebook apa pun secara manual untuk menyelesaikan M02A.
- **Pilihan kernel Jupyter (jika ingin membuka notebook di masa depan):**
  - Baseline M00: `krkcmd-research-newpc` (`Python (krkCMd Research - New PC)`)
  - Boosting: `krkcmd-boost` (`Python (krkCMd - Boosting)`)
  - CPU Signal: `krkcmd-signal-cpu` (`Python (krkCMd - CPU Signal)`)
- **Instalasi perangkat lunak yang memerlukan persetujuan terpisah:** Pembuatan `.venv-deep` (PyTorch CUDA `cu128`) dan `.venv-foundation` (M02B/M02C) **belum dijalankan** dan menunggu persetujuan eksplisit Anda. `.venv_old_pc_backup/` juga belum dihapus.
- **Tindakan Git yang disarankan:** Tinjau `git status` dan lakukan `git commit`/`git push` secara manual hanya jika Anda puas dengan hasil M02A (pastikan `.venv-boost/` dan `.venv-signal-cpu/` tetap terabaikan oleh `.gitignore`).
- **Berkas yang harus diunggah ke ChatGPT untuk review:**
  1. `result_run_7_M02A.md` — hasil ekspor percakapan Antigravity.
  2. `M02A_review_package.zip` — paket review ringan lengkap di `reports/runs/M02A_20261125_074616_DESKTOP-CQB09OU/M02A_review_package.zip`.
