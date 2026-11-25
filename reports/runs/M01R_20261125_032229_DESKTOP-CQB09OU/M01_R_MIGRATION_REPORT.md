# Laporan Migrasi, Rekonstruksi Lingkungan, Reproduksi M00 & Reassessment M01 (M01-R)

**Proyek:** `krkCMd_research_starter`  
**Run ID:** `M01R_20261125_032229_DESKTOP-CQB09OU`  
**Tanggal:** 2026-11-25  
**Workstation Baru:** `DESKTOP-CQB09OU`  
**Repositori Git:** `https://github.com/abdurrahmansyah/krkCMd_research_starter_v1.git` (`main` @ `201aa50b8b97e789d7eb855609b027bd02904539`)  

---

## 1. Ringkasan Eksekutif

Proyek penelitian `krkCMd_research_starter` telah dimigrasikan dan diverifikasi secara menyeluruh pada workstation baru (`DESKTOP-CQB09OU`) tanpa mengubah metodologi penelitian, dataset asli, artefak historis, maupun naskah manuskrip.

- **Rekonstruksi Lingkungan:** Dengan persetujuan peneliti, **Python 3.11.9 (64-bit)** resmi diinstal secara per-user. Lingkungan `.venv` salinan dari PC lama (yang rusak karena mengarah ke path user lama `NurRidhoA`) diamankan sebagai `.venv_old_pc_backup`, dan `.venv` baru dibangun ulang dengan **100% versi paket historis yang identik** (`112` paket pustaka ilmiah & Jupyter; `pip check` bersih).
- **Reproduksi Eksperimen M00 (Terisolasi):** Eksekusi ulang `notebooks/00_baseline_krkCMd.ipynb` pada kernel baru `krkcmd-research-newpc` dalam ruang kerja terisolasi selesai **100% sukses dalam 212,272 detik**. Pembagian data `group_split_manifest.csv` ter-reproduksi **persis baris-demi-baris dan urutan-demi-urutan**, serta seluruh prediksi pada `3.822` baris uji identik secara bit untuk 4 model (`Dummy_mean`, `LinearRegression`, `HistGradientBoosting`, `SVR_RBF`) dan berada dalam toleransi numerik IEEE-754 `< 2,3 × 10⁻¹³ µm` untuk `ExtraTrees` dan `RandomForest`.
- **Reassessment M01:** Seluruh **32 kandidat model** dipertahankan; 8 kandidat baseline yang terpasang di `.venv` lulus uji asap sintetis L0/L1 (`seed=42`, 501 fitur, 0 prediksi negatif/NaN); uji *dry-run* resolusi dependensi transitif berhasil untuk keenam skema lingkungan usulan; dan rencana kapasitas baru disusun berdasarkan **127,92 GB RAM**, **Quadro RTX 6000 24 GB VRAM**, serta **1.752,80 GB disk bebas**.
- **Stop Gate:** Seluruh fase M01-R berhenti di sini. Tidak ada implementasi M01.1, instalasi paket M02, HPO, uji skala L2, pengunduhan bobot *gated*, ataupun `git commit`/`push` yang dijalankan.

---

## 2. Temuan Rekonsiliasi Repositori (Fase 1)

| Item Pemeriksaan | Hasil Aktual Terukur |
|---|---|
| **Direktori Kerja & Git Root** | `C:\PROJECT\krkCMd_research_starter_v1` (satu-satunya folder proyek di `C:\PROJECT`; hasil clone Git dan file salinan lokal berada pada direktori kanonik yang sama) |
| **Origin URL** | `https://github.com/abdurrahmansyah/krkCMd_research_starter_v1.git` |
| **Branch & Remote Tracking** | `main` melacak `origin/main` |
| **Commit SHA Saat Ini** | `201aa50b8b97e789d7eb855609b027bd02904539` (`feat: M01`) |
| **Riwayat 8 Commit Terbaru** | `201aa50` (`feat: M01`), `80279cd` (`feat: manuscript generator & reference`), `80f0745` (`feat: run ipynb and result .html`), `3bab799`, `fb82139`, `4b449ac`, `1986ab6`, `7694f8d` |
| **Status Tree Awal** | Bersih (0 modifikasi tracked sebelum M01-R; 0 staged changes) |
| **Keamanan Git Tracking** | **20 file PDF** di `papers/` berstatus *tracked* sejak commit starter; 31 file PDF tambahan di `papers/` berstatus *ignored* oleh `.gitignore`. `data/raw/*`, `.venv/`, `artifacts/models/*`, `artifacts/results/*`, dan `reports/{figures,tables,logs}/*` berstatus *ignored* (hanya `.gitkeep` yang dilacak). |

---

## 3. Inventaris Berkas & Status Artefak

Total **144 file** (di luar `.git/`, `.venv/`, dan `reports/runs/`) diinventarisasi dalam [file_inventory.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/file_inventory.json):
- **Data Mentah (`data/raw/`):** `krkCMd_table.csv` (`56.292.603` byte), `krkCMd_scripts.zip` (`273.175` byte), `krkCMd_images.zip` (`38.589.509.774` byte / ~38,59 GB; hashing SHA-256 penuh ditangguhkan sesuai otorisasi agar tidak menduplikasi arsip).
- **Skrip Ekstraksi (`data/interim/krkCMd_scripts/`):** `CrackWidthAED_VBA.txt`, `CrackWidthDLM_Matlab.m`, `Crack_Multi_Intersection_ROI_ImagJ.txt`, `krknet.mat`.
- **Dokumen Tata Kelola, Konfigurasi, Skrip, Notebook, Manuskrip, Literatur:** Lengkap (`AGENT.md`, `MASTER_PROMPT.md`, `README.md`, `requirements.txt`, `configs/baseline.yaml`, `configs/model_registry.yaml`, 9 file di `docs/`, 3 skrip di `scripts/`, `00_baseline_krkCMd.ipynb` & `.html`, 2 draf DOCX + 8 gambar/DOT di `manuscript/`, 51 PDF di `papers/`, 6 model `.joblib` + `benchmark_predictions.csv` historis di `artifacts/`).
- **Artefak yang belum ada (bukan kesalahan migrasi):** Folder `src/*`, `tests/`, dan `data/processed/` hanya berisi `.gitkeep` karena desain modular M01.1/M02 belum dimulai.

---

## 4. Perbandingan Spesifikasi Hardware: Workstation Lama vs. Baru (Fase 2)

| Komponen | PC Lama (`reports/logs/hardware_environment.json`) | Workstation Baru (`DESKTOP-CQB09OU`, terukur) |
|---|---|---|
| **OS** | Windows 10/11 Enterprise (`10.0.26300`, AMD64) | Windows Pro 24H2 Build `26100.9711` (AMD64; Registry `ProductName`: `Windows 10 Pro`) |
| **PowerShell / Git** | — | PowerShell `5.1.26100.9711`; Git `2.56.1.windows.1` (`C:\Program Files\Git\cmd\git.exe`) |
| **CPU** | Intel Core i7 (Family 6 Model 154, 14C / 20T) | **Intel(R) Core(TM) i9-10900KF @ 3.70 GHz** (`3696 MHz`, 20 logical threads; `SSE2=True`, `SSE3=True`, `AVX=True`, `AVX2=True`, `AVX512F=False`) |
| **RAM** | 31,70 GB total (**6,29 GB** tersedia, 80,2% terpakai) | **127,92 GB total** (**113,36 GB** tersedia, 11% terpakai; Pagefile total 144,92 GB, bebas 128,73 GB) |
| **Storage (`C:`)** | 952,51 GB total (**37,54 GB** bebas) | **1.906,74 GB** NTFS (**1.752,80 GB** bebas, 153,94 GB terpakai) |
| **GPU** | NVIDIA GeForce RTX 3050 Laptop (**4.096 MiB / 4 GB VRAM**) | **NVIDIA Quadro RTX 6000** (**24.576 MiB / 24 GB VRAM**, `22.974 MiB` bebas, `1.282 MiB` terpakai display, Compute Capability `7.5`, PCI `00000000:01:00.0`) |
| **Driver & CUDA** | Driver `596.52` \| CUDA `13.2` | Driver `621.24` \| CUDA UMD `13.5` \| **CUDA Toolkit tidak terpasang** \| **Komputasi GPU belum diverifikasi (belum ada framework CUDA)** |
| **Software Opsional** | MATLAB R2026b (tanpa `nnet`), WSL2 Ubuntu | **VS Code, MATLAB, WSL2, Docker: Tidak terpasang** |

---

## 5. Hasil Rekonstruksi Python, Virtual Environment & Kernel Jupyter (Fase 3)

1. **Penemuan Python & Persetujuan Instalasi:** Sebelum instalasi, tidak ada Python 3.11 maupun `py.exe` pada `DESKTOP-CQB09OU`, dan `.venv` salinan gagal dijalankan (exit code `103`) karena [pyvenv.cfg](file:///c:/PROJECT/krkCMd_research_starter_v1/.venv/pyvenv.cfg) mengarah ke `C:\Users\NurRidhoA\AppData\Local\Programs\Python\Python311\python.exe`. Setelah persetujuan peneliti, installer resmi **Python 3.11.9 (64-bit)** (`python-3.11.9-amd64.exe`, `MSC v.1938 64 bit`) dipasang secara per-user (`InstallLauncherAllUsers=0`) dengan exit code `0`.
2. **Pelestarian `.venv` Lama & Rebuild `.venv` Baru:**
   - Daftar 114 paket dari `.venv` lama diekstrak ke [historical_venv_freeze.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/historical_venv_freeze.txt).
   - Folder `.venv` lama diamankan utuh sebagai `.venv_old_pc_backup`.
   - Lingkungan `.venv` baru dibuat dari Python `3.11.9` dan diinstal menggunakan `requirements.txt` + `psutil==7.2.2` dengan batasan versi eksak ([historical_constraints.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/historical_constraints.txt)). Jenis rekonstruksi: **Exact historical environment reconstruction**.
   - `.\.venv\Scripts\python.exe -m pip check` menghasilkan: **`No broken requirements found.`**
3. **Registrasi Kernel Jupyter:**
   - Kernel terdaftar: `krkcmd-research-newpc` (`"Python (krkCMd Research - New PC)"`) pada `C:\Users\Nur Ridho A\AppData\Roaming\jupyter\kernels\krkcmd-research-newpc`.
   - `argv[0]` terverifikasi mengarah ke `C:\PROJECT\krkCMd_research_starter_v1\.venv\Scripts\python.exe`.
   - Uji eksekusi cell ringan via `nbclient` berhasil (`KERNEL_OK ... 3.11.9 2.4.6 2.3.3 1.9.1`). *(Catatan: pemilihan kernel di GUI editor bergantung pada pengguna; verifikasi dilakukan via CLI/nbclient.)*

---

## 6. Perbandingan Versi Paket Eksak (Lama vs. Baru)

| Paket | PC Lama (`.venv_old_pc_backup`) | PC Baru (`.venv`) | Status |
|---|---|---|---|
| `python` | `3.11.9` | `3.11.9` | **Identik** |
| `numpy` | `2.4.6` | `2.4.6` | **Identik** |
| `pandas` | `2.3.3` | `2.3.3` | **Identik** |
| `scipy` | `1.17.1` | `1.17.1` | **Identik** |
| `scikit-learn` | `1.9.1` | `1.9.1` | **Identik** |
| `matplotlib` | `3.11.2` | `3.11.2` | **Identik** |
| `seaborn` | `0.13.2` | `0.13.2` | **Identik** |
| `joblib` | `1.6.0` | `1.6.0` | **Identik** |
| `PyYAML` | `6.0.4` | `6.0.4` | **Identik** |
| `openpyxl` | `3.1.5` | `3.1.5` | **Identik** |
| `pypdf` | `7.1.1` | `7.1.1` | **Identik** |
| `ipykernel` | `6.31.0` | `6.31.0` | **Identik** |
| `jupyter_core` / `jupyterlab` / `notebook` | `5.9.1` / `4.6.6` / `7.6.5` | `5.9.1` / `4.6.6` / `7.6.5` | **Identik** |
| `nbformat` / `nbconvert` / `nbclient` | `5.11.1` / `7.17.2` / `0.11.0` | `5.11.1` / `7.17.2` / `0.11.0` | **Identik** |
| `psutil` | `7.2.2` | `7.2.2` | **Identik** |
| `pip` / `setuptools` | `26.3` / `65.5.0` | `24.0` (bawaan venv) / tidak diinstal | Perbedaan tooling non-riset yang disengaja agar `pip` tidak di-upgrade otomatis |

Lengkap di [baseline_environment_new_pc.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/baseline_environment_new_pc.json) dan [requirements_baseline_new_pc.freeze.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/requirements_baseline_new_pc.freeze.txt).

---

## 7. Integritas Dataset & Rekaman SHA-256 (Fase 4)

Eksekusi `scripts/audit_dataset.py` dalam ruang kerja terisolasi (`isolated_workspace`) **PASS 100%** dan menghasilkan `comprehensive_audit.json` yang **identik** dengan artefak historis (`audit_exact_match_with_historical: true` di [dataset_verification.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/dataset_verification.json)):

- **SHA-256 `data/raw/krkCMd_table.csv`:** `CCCA7965B225F77D35567573BB557A6E0476122C381E14AB1BDA898DF9F9B909` (`56.292.603` byte).
- **SHA-256 `data/raw/krkCMd_scripts.zip`:** `8E4C8F527ECEF98A6394F302FA894787EED6F35335032C6DCA9F76C36875E567` (`273.175` byte; berisi 4 entri: `Crack_Multi_Intersection_ROI_ImagJ.txt` 3.665 B, `CrackWidthAED_VBA.txt` 11.414 B, `CrackWidthDLM_Matlab.m` 956 B, `krknet.mat` 267.805 B).
- **Validasi Kontrak Data Aktual:** `19.098` baris × `510` kolom; `501` fitur `x1`..`x501` terurut (`[0.0, 255.0]`); 6 kolom metadata (`No`, `Profile`, `Series`, `Image`, `Gridline`, `Stage`); target `MANwidth` (`[0.0, 813.5938]` µm, mean `148.8755` µm); baseline `DLMwidth` & `AEDwidth`; `0` missing values; `0` duplikat; `3.183` kelompok unik (`Series + Image + Gridline`), tepat `6` observasi per kelompok dengan `Stage` `(1, 2, 3, 4, 5, 6)` tepat satu kali.

---

## 8. Verifikasi Group Split (Fase 6.2)

Hasil verifikasi di [split_verification.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/split_verification.json) membuktikan:

| Partisi | Baris Historis | Group Historis | Baris Regenerasi | Group Regenerasi | Overlap |
|---|---:|---:|---:|---:|---|
| **Train** | 12.216 | 2.036 | 12.216 | 2.036 | `train ∩ val = 0` |
| **Validation** | 3.060 | 510 | 3.060 | 510 | `train ∩ test = 0` |
| **Test** | 3.822 | 637 | 3.822 | 637 | `val ∩ test = 0` |
| **Total** | **19.098** | **3.183** | **19.098** | **3.183** | **0 overlap** |

- `unique_source_row_id = True`, `full_row_coverage = True`, `group_id_matches_csv = True`, `all_groups_have_stages_1_to_6 = True`.
- **Kecocokan eksak:** `exact_row_by_row_match_sorted = True` dan `exact_row_and_order_match = True` terhadap [group_split_manifest.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/tables/group_split_manifest.csv) historis.

---

## 9. Verifikasi Statis Notebook & Konfigurasi (Fase 5)

- **Eksekusi `scripts/verify_env_and_notebook.py`:** Lulus pada pemeriksaan Python (`3.11.9`), seluruh 11 modul impor, `pip check`, kompilasi statis `12/12` code cell, serta aturan `.gitignore`; keluar dengan exit code `1` **hanya** karena skrip tersebut mencari nama kernel lama `krkcmd-research` (sedangkan di workstation baru terdaftar `krkcmd-research-newpc`).
- **Pemeriksaan statis [00_baseline_krkCMd.ipynb](file:///c:/PROJECT/krkCMd_research_starter_v1/notebooks/00_baseline_krkCMd.ipynb):**
  - Total `25` cell (`12` code cell, `13` markdown cell); `12/12` code cell lulus `compile(..., mode="exec")`.
  - Menggunakan kolom resmi `Gridline` (`True`); tidak ada skema usang `['Series', 'Image', 'Grid']` (`False`).
  - Memakai path relatif dari `find_project_root()` (yang mencari `AGENT.md` + `data/`); kernel metadata asli notebook adalah `python3` / `.venv`.
  - Catatan kecil pada [baseline.yaml](file:///c:/PROJECT/krkCMd_research_starter_v1/configs/baseline.yaml): entri `No` tanpa tanda kutip pada `metadata_columns` dibaca oleh parser YAML 1.1 `PyYAML` sebagai boolean `False` (tidak berdampak pada notebook karena notebook mendefinisikan daftar kolom metadata langsung di Python).

---

## 10. Hasil Eksekusi Aktual Notebook Baseline M00 (Fase 6.3–6.4)

Salinan terisolasi `notebooks/00_baseline_krkCMd.ipynb` dieksekusi penuh melalui `nbclient` pada kernel `krkcmd-research-newpc` dalam direktori kerja `isolated_workspace/`:
- **Status Eksekusi:** **`SUCCESS`** (seluruh `12/12` code cell selesai berurutan, `0` error, durasi total **`212,272 detik`**).
- **Peringatan runtime:** Hanya `UserWarning` standar scikit-learn (`X does not have valid feature names, but ExtraTreesRegressor was fitted with feature names`) pada Cell 18 (8 kali) dan Cell 22 (4 kali) — identik dengan log eksekusi historis.
- **Keluaran tersimpan:** [00_baseline_krkCMd_executed.ipynb](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/00_baseline_krkCMd_executed.ipynb), [00_baseline_krkCMd_executed.html](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/00_baseline_krkCMd_executed.html), [notebook_execution_log.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/notebook_execution_log.json), serta seluruh artefak tabel/grafik/model di `isolated_workspace/`.

---

## 11. Perbandingan Benchmark M00: Workstation Lama vs. Baru (Fase 7)

Seluruh hasil berasal dari [baseline_reproduction_comparison.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/baseline_reproduction_comparison.csv) dan [reproducibility_summary.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/reproducibility_summary.json) (`n_test = 3.822`):

| Model | MAE Lama (µm) | MAE Baru (µm) | RMSE Baru (µm) | $R^2$ Baru | MedianAE Baru (µm) | Bias Baru (µm) | Max \|$\Delta$\| Prediksi per-Baris (µm) | Tipe Reproduksi |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **ExtraTrees** | 14,311523 | 14,311523 | 35,504987 | 0,935147 | 5,623690 | 1,212636 | `1,71e-13` | Numerik (`< 1e-12` µm) |
| **RandomForest** | 14,407363 | 14,407363 | 35,336657 | 0,935760 | 5,602031 | 0,901033 | `2,27e-13` | Numerik (`< 1e-12` µm) |
| **HistGradientBoosting** | 15,149774 | 15,149774 | 36,794280 | 0,930351 | 6,457064 | 1,158559 | **`0,0`** | **Exact Bitwise** |
| **SVR_RBF** | 28,118558 | 28,118558 | 44,778006 | 0,896847 | 17,136260 | 4,641504 | **`0,0`** | **Exact Bitwise** |
| **LinearRegression** | 49,826529 | 49,826529 | 66,898135 | 0,769760 | 39,113908 | -0,117477 | **`0,0`** | **Exact Bitwise** |
| **Dummy_mean** | 116,599211 | 116,599211 | 139,595829 | -0,002531 | 119,416945 | -7,014014 | **`0,0`** | **Exact Bitwise** |
| **DLMwidth** *(eksternal)* | 13,635201 | 13,635201 | 28,781404 | 0,957384 | 6,442000 | -0,921287 | — | **Exact** |
| **AEDwidth** *(eksternal)* | 35,979388 | 35,979388 | 66,504550 | 0,772461 | 23,812500 | -22,384705 | — | **Exact** |

- **Penjelasan selisih `~1e-13` µm pada `ExtraTrees` & `RandomForest`:** Dengan versi Python (`3.11.9`) dan paket (`scikit-learn 1.9.1`, `numpy 2.4.6`, `scipy 1.17.1`) yang identik, selisih orde $10^{-13}\,\mu\text{m}$ (mean abs diff $\le 9,6 \times 10^{-15}\,\mu\text{m}$) berasal dari urutan reduksi/penjumlahan *floating-point* paralel `n_jobs=-1` (20 thread OpenMP/OpenBLAS Haswell) pada arsitektur CPU berbeda.

---

## 12. Perbandingan Robustness Ide 2: Workstation Lama vs. Baru

Model terpilih oleh validation MAE tetap **`ExtraTrees`** (di-refit pada train + validation = `15.276` baris; dievaluasi pada `3.822` baris uji, sumber: [robustness_reproduction_comparison.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/robustness_reproduction_comparison.csv)):

| Kondisi Perturbasi Sintetis | MAE Lama (µm) | MAE Baru (µm) | Selisih Absolut (µm) | Kenaikan MAE vs Clean (%) |
|---|---:|---:|---:|---:|
| `clean` | 14,047211 | 14,047211 | `-5,33e-15` | 0,00% |
| `brightness_shift_-20` | 25,319835 | 25,319835 | `+3,55e-15` | +80,25% |
| `brightness_shift_+20` | 51,899147 | 51,899147 | `0,0` | +269,46% |
| `contrast_scale_0.8` | 77,144320 | 77,144320 | `0,0` | +449,18% |
| `contrast_scale_1.2` | 25,992077 | 25,992077 | `0,0` | +85,03% |
| `gaussian_noise_sigma5` | 15,246616 | 15,246616 | `-1,78e-15` | +8,54% |
| `gaussian_noise_sigma10` | 19,276669 | 19,276669 | `0,0` | +37,23% |
| `gaussian_smoothing_sigma1` | 14,085716 | 14,085716 | `0,0` | +0,27% |

---

## 13. Perbandingan Reproduksi Per-Series (Ide 4 Screening Gate)

Sumber: [per_series_reproduction_comparison.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/per_series_reproduction_comparison.csv):

| Series | `n` Lama / Baru | MAE Lama (µm) | MAE Baru (µm) | RMSE Baru (µm) | Selisih MAE (µm) |
|---|---:|---:|---:|---:|---:|
| `CMd_0.23_20mths` | 1.308 / 1.308 | 7,261781 | 7,261781 | 13,791389 | `-1,78e-15` |
| `CMd_0.23_2mths` | 780 / 780 | 13,142956 | 13,142956 | 24,786004 | `0,0` |
| `CMd_0.28_20mths` | 402 / 402 | 37,731239 | 37,731239 | 74,899459 | `0,0` |
| `CMd_0.28_2mths` | 1.332 / 1.332 | 14,092019 | 14,092019 | 38,800112 | `0,0` |

*Sesuai tata kelola, hasil per-Series ini adalah skrining awal; adaptasi domain lintas-Series penuh belum dijalankan.*

---

## 14. Perbandingan Waktu Komputasi & Sumber Daya

| Model | Waktu PC Lama (s) | Waktu PC Baru (s) | Perubahan |
|---|---:|---:|---|
| **ExtraTrees** | 37,556 | **17,743** | **2,12× lebih cepat (-52,8%)** |
| **RandomForest** | 102,991 | **59,757** | **1,72× lebih cepat (-42,0%)** |
| **HistGradientBoosting** | 3,865 | **3,243** | **1,19× lebih cepat (-16,1%)** |
| **LinearRegression** | 0,412 | **0,344** | **1,20× lebih cepat (-16,5%)** |
| **SVR_RBF** | 47,366 | **52,135** | +10,1% (LibSVM *single-threaded*; sensitif clock/IPC inti tunggal) |
| **Dummy_mean** | 0,000 | **0,000** | Identik |

---

## 15. Validasi Registry M01 untuk Seluruh 32 Kandidat

- Terverifikasi tepat **32 ID unik** pada [model_registry.yaml](file:///c:/PROJECT/krkCMd_research_starter_v1/configs/model_registry.yaml) dan [model_compatibility_matrix_new_pc.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/model_compatibility_matrix_new_pc.csv): `ML01–ML07` (7), `DL01–DL05` (5), `FM01–FM04` (4), `SG01–SG06` (6), `HY01–HY05` (5), `RF01–RF05` (5).
- Tidak ada kandidat yang dihapus, diganti, atau ditandai `APPROVED`.
- **Implikasi Hardware Workstation Baru:** Quadro RTX 6000 (24 GB VRAM) + 127,92 GB RAM menghilangkan hambatan VRAM 4 GB sebelumnya untuk `DL02` (FT-Transformer), `DL03–DL05`, `SG01–SG04`, `HY03–HY04`, `RF05`, serta `FM01–FM04`, **namun status runtime mereka tetap belum teruji (NOT_EXECUTED) hingga instalasi lingkungan dan uji L0/L1/L2 disetujui.** Sebaliknya, `RF04` via MATLAB lokal tidak tersedia karena MATLAB tidak terpasang di workstation baru.

---

## 16. Hasil Smoke Test Sintetis Aktual (L0/L1 di `.venv`)

Dijalankan terisolasi pada data profil sintetis (`seed=42`, `N_train=100`, `N_test=20`, `D=501` fitur; sumber: [smoke_test_results_new_pc.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/smoke_test_results_new_pc.json)):

| ID | Model & Implementasi Aktual | Versi Paket | Shape | Finite | Prediksi Negatif | Durasi (s) | Status & Catatan |
|---|---|---|---|---|---:|---:|---|
| `ML01` | ExtraTreesRegressor (`n_estimators=10`) | `scikit-learn 1.9.1` | `(20,)` | True | 0 | 0,0644 | `SMOKE_TEST_PASS` |
| `ML02` | RandomForestRegressor (`n_estimators=10`) | `scikit-learn 1.9.1` | `(20,)` | True | 0 | 0,0632 | `SMOKE_TEST_PASS` |
| `ML03` | HistGradientBoostingRegressor (`max_iter=20`) | `scikit-learn 1.9.1` | `(20,)` | True | 0 | 0,1207 | `SMOKE_TEST_PASS` |
| `ML07` | Pipeline(`StandardScaler`, `SVR(C=10, eps=0.1)`) | `scikit-learn 1.9.1` | `(20,)` | True | 0 | 0,0054 | `SMOKE_TEST_PASS` |
| `DL01` | Pipeline(`StandardScaler`, `MLPRegressor(64,32), max_iter=20`) | `scikit-learn 1.9.1` | `(20,)` | True | 0 | 0,0241 | `SMOKE_TEST_PASS` *(catatan: prototype sklearn, berbeda dari PyTorch MLP; 1 ConvergenceWarning)* |
| `RF01` | DummyRegressor(`strategy='mean'`) | `scikit-learn 1.9.1` | `(20,)` | True | 0 | 0,0003 | `SMOKE_TEST_PASS` |
| `RF02` | Pipeline(`StandardScaler`, `LinearRegression`) | `scikit-learn 1.9.1` | `(20,)` | True | 0 | 0,0134 | `SMOKE_TEST_PASS` |
| `RF03` | Prototype analitis 1-profil (`aed_prototype`) | `numpy 2.4.6`, `scipy 1.17.1` | `(20,)` | True | 0 | 0,0002 | `SMOKE_TEST_PASS` *(catatan: output finite dari prototype sederhana TIDAK membuktikan kesetaraan dengan makro VBA multi-stage `CrackWidthAED_VBA.txt`)* |

---

## 17. Temuan Kompatibilitas Dependensi (Transitive Dry-Run Fase 8.5)

Hasil uji `pip install --dry-run --ignore-installed --report` transitif ([dependency_resolution_new_pc.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/dependency_resolution_new_pc.json)):

1. **`env-baseline`:** `RESOLVED_TRANSITIVE` (112 paket) dalam `16,33 s`.
2. **`env-boost`:** `RESOLVED_TRANSITIVE` (25 paket: `xgboost 3.2.0`, `lightgbm 4.7.0`, `catboost 1.2.10`, `numpy 2.4.6`, `scikit-learn 1.9.1`) dalam `61,10 s`. *Temuan:* `xgboost 3.4.1` terbaru mensyaratkan Python `>=3.12`, sehingga pada Python `3.11.9` terpilih `xgboost 3.2.0`.
3. **`env-deep-pytorch-cu124`:** `RESOLVED_TRANSITIVE` (26 paket) dalam `16,57 s`, **namun** `--extra-index-url` mengambil `torch 2.15.0` CPU dari PyPI karena lebih baru daripada `cu124`. Pemeriksaan indeks PyTorch menunjukkan wheel CUDA Python 3.11 Windows x64 tersedia di `cu124` (hingga `2.6.0+cu124`), `cu126`, `cu128`, dan `cu130` (masing-masing hingga **`2.9.1+cu126`/`cu128`/`cu130`**). Untuk instalasi nyata nanti harus memakai `--index-url https://download.pytorch.org/whl/cu128` secara eksplisit untuk `torch`/`torchvision`.
4. **`env-signal-cpu`:** `RESOLVED_TRANSITIVE` (17 paket: `aeon 1.6.0`, `numba 0.63.1`, `llvmlite 0.46.0`, **`numpy 2.3.5`**, `pandas 3.0.6`) dalam `4,88 s`. Memvalidasi kebutuhan isolasi karena `numba` menurunkan `numpy` ke `2.3.5`.
5. **`env-signal-tf`:** `RESOLVED_TRANSITIVE` (45 paket: `aeon 1.6.0`, `tensorflow 2.21.0`, `keras 3.15.1`, `numba 0.63.1`, `numpy 2.3.5`) dalam `167,64 s`.
6. **`env-foundation`:** `RESOLVED_TRANSITIVE` (56 paket: `tabpfn 10.2.0`, `huggingface_hub 2.4.0`, `torch 2.15.0`) dalam `12,86 s`. Metadata PyPI juga mengonfirmasi ketersediaan `tabicl 2.2.0`, `tabdpt 1.3.2`, `tabm 0.0.3`, `rtdl 0.0.13`, `rtdl-num-embeddings 0.0.12`, `pytabkit 1.8.0` pada Python `3.11`. *Kendala lisensi tetap berlaku untuk bobot gated `FM01–FM03`.*

---

## 18. Rencana Lingkungan Workstation Baru yang Diusulkan (Fase 9)

Disajikan lengkap pada dokumen terpisah: [MODEL_ENVIRONMENT_PLAN_NEW_PC.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/MODEL_ENVIRONMENT_PLAN_NEW_PC.md).

---

## 19. Daftar Masalah M01.1 yang Belum Diselesaikan (Dipertahankan Terpisah)

Sesuai instruksi, 12 isu M01.1 berikut **tidak diperbaiki** dalam M01-R dan dicatat untuk fase M01.1 berikutnya:
1. Angka `validation_sample_size: 3054` dan `test_sample_size: 3828` pada [model_registry.yaml](file:///c:/PROJECT/krkCMd_research_starter_v1/configs/model_registry.yaml) tidak sesuai dengan split M00 aktual (`3.060` validation, `3.822` test).
2. Kerancuan versi TabPFN v2 vs. TabPFN-3.5 dan batasan fitur/sampel checkpoint.
3. Spesifikasi `TabICLv2` (`FM03`) pada M01 usang (termasuk klaim `windows_native: False` padahal `tabicl 2.2.0` tersedia di PyPI `>=3.10`).
4. Identitas estimator `SG06` (`MultiROCKET-HYDRA` menunjuk `MultiRocketRegressor` saja).
5. Kerancuan backend TensorFlow/Keras vs. PyTorch pada modul `aeon.regression.deep_learning`.
6. Beberapa path estimator/referensi di registry (mis. `tabbench.RealMLP`, `tabular-dl-tabr`, `tabular-dl-tabm`, `krkcmd.models.*`) belum ada di `src/` atau berbeda dari nama paket PyPI (`pytabkit`, `tabm`).
7. Status `SMOKE_TEST_PASS` yang di-hardcode di [check_model_compatibility.py](file:///c:/PROJECT/krkCMd_research_starter_v1/scripts/check_model_compatibility.py).
8. Hasil runtime dinamis belum terpropagasi secara otomatis ke matriks kompatibilitas.
9. Pemeriksaan dependensi lama memakai `--no-deps` (bukan resolusi transitif penuh).
10. Belum ada pengaman resource subprocess (RAM/VRAM/timeout guard) pada skrip kompatibilitas.
11. Prototype AED sederhana di `check_model_compatibility.py` diperlakukan seolah reproduksi setia `CrackWidthAED_VBA.txt`.
12. Perbedaan varian arsitektur yang diusulkan untuk `HY03` (*Dual-stream multiscale CNN*).
*(Tambahan temuan M01-R: `scripts/verify_env_and_notebook.py` mengecek nama kernel lama `krkcmd-research`, dan `configs/baseline.yaml` memakai `No` tanpa tanda kutip.)*

---

## 20. Berkas yang Dibuat atau Diubah

### Diubah (Dokumentasi Tata Kelola & Setup Saja — 0 kode eksperimen/konfigurasi model/manuskrip diubah)
- [docs/EXPERIMENT_LOG.md](file:///c:/PROJECT/krkCMd_research_starter_v1/docs/EXPERIMENT_LOG.md) — Menambahkan entri `EXP-003`.
- [docs/DECISIONS.md](file:///c:/PROJECT/krkCMd_research_starter_v1/docs/DECISIONS.md) — Menambahkan usulan administratif `D-006`.
- [README.md](file:///c:/PROJECT/krkCMd_research_starter_v1/README.md) — Menambahkan catatan migrasi `M01-R`.

### Dibuat (Di bawah `reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/` + `.venv` / `.venv_old_pc_backup`)
- [hardware_environment.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/hardware_environment.json)
- [file_inventory.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/file_inventory.json)
- [baseline_environment_new_pc.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/baseline_environment_new_pc.json)
- [requirements_baseline_new_pc.freeze.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/requirements_baseline_new_pc.freeze.txt)
- [historical_venv_freeze.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/historical_venv_freeze.txt) & `historical_constraints.txt` & `pip_install_baseline.log`
- [dataset_verification.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/dataset_verification.json)
- [split_verification.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/split_verification.json)
- [notebook_execution_log.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/notebook_execution_log.json)
- [00_baseline_krkCMd_executed.ipynb](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/00_baseline_krkCMd_executed.ipynb) & [00_baseline_krkCMd_executed.html](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/00_baseline_krkCMd_executed.html)
- [baseline_reproduction_comparison.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/baseline_reproduction_comparison.csv)
- [robustness_reproduction_comparison.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/robustness_reproduction_comparison.csv)
- [per_series_reproduction_comparison.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/per_series_reproduction_comparison.csv)
- [reproducibility_summary.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/reproducibility_summary.json)
- [model_compatibility_matrix_new_pc.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/model_compatibility_matrix_new_pc.csv)
- [smoke_test_results_new_pc.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/smoke_test_results_new_pc.json)
- [dependency_resolution_new_pc.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/dependency_resolution_new_pc.json)
- [MODEL_ENVIRONMENT_PLAN_NEW_PC.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/MODEL_ENVIRONMENT_PLAN_NEW_PC.md)
- [M01_R_MIGRATION_REPORT.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/M01_R_MIGRATION_REPORT.md)
- [M01R_review_package.zip](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/M01R_review_package.zip)

---

## 21. Status Git

- **Modified (unstaged):** `README.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_LOG.md`
- **Untracked:** `.venv_old_pc_backup/` (disarankan tidak di-commit atau dihapus hanya setelah konfirmasi Anda bahwa `.venv` baru sudah cukup), `reports/runs/` (berisi bukti run migrasi; pertimbangkan aturan `.gitignore` sebelum commit agar file besar/biner di `isolated_workspace/` tidak ikut ter-stage).
- **Zero staged changes; zero `git commit`; zero `git push`.**

---

## 22. Hambatan Tersisa

1. MATLAB, VS Code, WSL2, Docker, dan CUDA Toolkit sistem tidak terpasang pada workstation baru (bukan hambatan untuk M00; berdampak pada `RF04` via MATLAB langsung).
2. Akselerasi GPU nyata pada `Quadro RTX 6000` belum terverifikasi melalui framework komputasi karena PyTorch CUDA belum diinstal (menunggu persetujuan M02).
3. `scripts/verify_env_and_notebook.py` masih memeriksa nama kernel lama `krkcmd-research` (ditangguhkan untuk M01.1).

---

## 23. Gerbang Persetujuan Langkah Berikutnya

**Berhenti di M01-R sesuai tata kelola.** Tahap selanjutnya menunggu review dan persetujuan eksplisit Anda:
1. **Gerbang A (M01.1 Corrective Implementation):** Persetujuan untuk memperbaiki 12 isu dokumentasi/skrip/registry pada M01.1 (termasuk penyelarasan jumlah sampel di `model_registry.yaml`, identitas estimator, penghapusan status *hardcode* di `check_model_compatibility.py`, serta opsi nama kernel di `verify_env_and_notebook.py`).
2. **Gerbang B (Pembuatan Lingkungan M02 & Uji L2):** Persetujuan untuk membuat `.venv-boost`, `.venv-deep` (PyTorch `cu128` untuk verifikasi komputasi GPU Quadro RTX 6000), dan `.venv-signal-cpu` sesuai [MODEL_ENVIRONMENT_PLAN_NEW_PC.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/MODEL_ENVIRONMENT_PLAN_NEW_PC.md), serta keputusan pembersihan `.venv_old_pc_backup`.
