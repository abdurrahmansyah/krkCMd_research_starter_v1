# Laporan Provisioning Foundation Models & Pemulihan Kandidat M02C

**Proyek:** `krkCMd_research_starter`  
**Run ID:** `M02C_20261125_203053_DESKTOP-CQB09OU`  
**Tanggal:** 2026-11-25/26  
**Workstation:** `DESKTOP-CQB09OU` (Core i9-10900KF 20T, `127,92 GiB` RAM, **NVIDIA Quadro RTX 6000** `24 GiB` VRAM Turing `sm_75`, Windows native, Python `3.11.9`)  

---

## 1. Lingkungan Baru, Verifikasi GPU & Kernel Jupyter

- **`.venv-foundation`** (`krkcmd-foundation`, `pip check` bersih): `torch==2.9.1+cu128`, `tabpfn==10.2.0`, `tabicl==2.2.0`, `tabdpt==1.3.2`, `huggingface_hub`, `numpy==2.4.6`, `pandas==3.1.1`, `scikit-learn==1.9.1`.
- **`.venv-tabr`** (`krkcmd-tabr`, `pip check` bersih): `torch==2.9.1+cu128`, `faiss-cpu==1.16.0`, `delu==0.0.26`, `tomli-w==1.2.0`, `tensorboard==2.21.0`, `yandex-research/tabular-dl-tabr` (`17baa9082506f8e7a0f8d11bb1e08212926a1507`).
- **Verifikasi GPU Aktual ([gpu_runtime_verification_M02C.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02C_20261125_203053_DESKTOP-CQB09OU/gpu_runtime_verification_M02C.json)):** **`GPU_PASS`** (`matmul_finite=true`, `fp32_finite=true`, `grads_finite_post_backward=true`, `params_finite_post_step=true`, `device_placed="cuda:0"`, `peak_cuda_allocated_mb=20,062`).
- **6 Lingkungan Tervalidasi Sebelumnya** (`.venv`, `.venv-boost`, `.venv-signal-cpu`, `.venv-deep`, `.venv-signal-tf`, `.venv-signal-hydra`) **tetap 100% utuh** ([before_after_integrity_M02C.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02C_20261125_203053_DESKTOP-CQB09OU/before_after_integrity_M02C.json)).

---

## 2. Hasil 7 Kandidat Target M02C (Data Sintetis `seed=42`, `D=501`)

### Track A — Foundation Models (`.venv-foundation`)
| ID | Model & Checkpoint | Akses / Lisensi | Device | L0 | L1 (100→20) | L2A (1000→200) | L2B (4096→1024) | L2C (12216→3822) | Status & Catatan |
|---|---|---|---|---|---|---|---|---|---|
| **FM01** | `TabPFNRegressor` (`tabpfn-v3.5-20260909.safetensors`) | `TabPFNLicenseError` (perlu persetujuan PriorLabs + `TABPFN_TOKEN`) | `cuda:0` | `PASS` | **`BLOCKED_LICENSE`** | `NOT_EXECUTED` | `NOT_EXECUTED` | `NOT_EXECUTED` | **`BLOCKED_LICENSE`** (tanpa token peneliti; batas 500 fitur v2 tidak berlaku untuk v3.5) |
| **FM02** | `TabPFNRegressor` `V3_5_FAST` (`tabpfn-v3.5-fast-20260909.safetensors`) | `TabPFNLicenseError` (perlu persetujuan PriorLabs + `TABPFN_TOKEN`) | `cuda:0` | `PASS` | **`BLOCKED_LICENSE`** | `NOT_EXECUTED` | `NOT_EXECUTED` | `NOT_EXECUTED` | **`BLOCKED_LICENSE`** |
| **FM03** | `TabICLRegressor` v2 (`tabicl-regressor-v2-20260212.ckpt`, `batch_size=1`, `use_fa3=False`) | Terbuka (**BSD-3-Clause**), `SHA-256: 0DB9CB53...` (`109,03 MB`) | `cuda:0` | `PASS` | `PASS` (`414 MiB` VRAM) | `PASS` (`2.094 MiB` VRAM) | `PASS` (`8.307 MiB` VRAM, `19,53 s`) | **`FAILED`** (`13,42 s`, watchdog VRAM reserve) | **Lulus s/d L2B `(4096, 501)`**; L2C butuh CPU/disk offloading |
| **FM04** | `TabDPTRegressor` (`tabdpt1_3.safetensors`, `retrieval`, `context_size=2048`, `batch_size=128`, `use_flash=False`, `compile=False`) | Terbuka (**Apache-2.0**), `SHA-256: 97DC3B60...` (`240,55 MB`) | `cuda:0` | `PASS` | `PASS` (`486 MiB` VRAM) | `PASS` (`486 MiB` VRAM) | `PASS` (`8.164 MiB` VRAM, `623,58 s`) | **`FAILED`** (timeout L2C) | **Lulus s/d L2B `(4096, 501)`**; *krkCMd pretraining overlap* = `UNKNOWN` |

### Track B — Pemulihan Kandidat Tertunda
| ID | Model & Lingkungan | Device | L0 | L1 | L2A | L2B | L2C (12216→3822) | Status Akhir |
|---|---|---|---|---|---|---|---|---|
| **DL04** | `bin.tabr.Model` (`17baa908`, `.venv-tabr`) | `CPU (faiss-cpu IndexFlatL2)` | `PASS` | `PASS` (`0,13 s`, diff `0,0`) | `PASS` (`0,95 s`) | `PASS` (`6,94 s`) | `PASS` (`52,11 s`, `861,95 MiB` RSS) | **`SCALE_CHECK_PASS`** |
| **RF05** | `DLM15LayerCNN_Table3_Normalized` (`.venv-deep`, train-only zero-center + `pi2mi=3,96875`) | `cuda:0` | `PASS` | `PASS` (diff `0,0`) | `PASS` (`5,78 s`) | `PASS` (`6,78 s`) | `PASS` (`9,59 s`, `1.131,49 MiB` RSS, `111,15 MiB` VRAM) | **`SCALE_CHECK_PASS`** |
| **SG06** | `aeon...MultiRocketHydraRegressor` (`.venv-signal-hydra`, `1.800 s` cap) | `CPU` | `PASS` | `PASS` | `PASS` | `PASS` | `PASS` (`344,86 s`, `26.234,87 MiB` RSS) | **`SCALE_CHECK_PASS`** |

---

## 3. Unit Test, Integritas & Status 32 Kandidat

- **Unit Tests ([unit_test_results_M02C.txt](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02C_20261125_203053_DESKTOP-CQB09OU/unit_test_results_M02C.txt)):** **`32/32` tests `OK`** dalam `1,537 s`.
- **Matriks 32 Kandidat ([model_compatibility_matrix_M02C.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02C_20261125_203053_DESKTOP-CQB09OU/model_compatibility_matrix_M02C.csv)):** `19` kandidat `SCALE_CHECK_PASS` (termasuk `ML01–03, ML07, RF01–02` M00 + `ML04–06, SG05` M02A + `DL01–03, DL05, SG01–04` M02B + `DL04, RF05, SG06` M02C), `2` lulus s/d L2B (`FM03`, `FM04`), `2` `BLOCKED_LICENSE` (`FM01`, `FM02`), `2` `CONDITIONAL` (`RF03`, `RF04`), `5` `DESIGN_REQUIRED` (`HY01–05`), `0` `APPROVED`.

---

### TINDAKAN MANUAL PENELITI

- **Autentikasi & Lisensi TabPFN (`FM01` / `FM02`):** Jika ingin mengaktifkan `FM01`/`FM02` di tahap berikutnya:
  1. Buka `https://ux.priorlabs.ai`, login/daftar, dan setujui lisensi pada tab **Licenses**.
  2. Salin token dari `https://ux.priorlabs.ai/account` dan atur secara lokal di sesi PowerShell Anda: `$env:TABPFN_TOKEN = "<token-anda>"` (jangan tempelkan token ke prompt/laporan).
- **Instalasi Software Manual:** **Tidak ada.**
- **Eksekusi Notebook Manual:** **Tidak diperlukan.**
- **Kernel Jupyter Tersedia:** `krkcmd-research-newpc`, `krkcmd-boost`, `krkcmd-signal-cpu`, `krkcmd-deep`, `krkcmd-signal-tf`, `krkcmd-signal-hydra`, `krkcmd-foundation`, `krkcmd-tabr`.
- **Tindakan Git yang Disarankan:** Tinjau `git status`; pastikan `.venv-*` dan `.cache/` tetap diabaikan `.gitignore` sebelum `git commit`/`git push` manual.
- **Berkas yang Harus Diunggah ke ChatGPT untuk Review:**
  1. `result_run_9_M02C.md` — hasil ekspor percakapan Antigravity.
  2. `M02C_review_package.zip` — paket review ringan di `reports/runs/M02C_20261125_203053_DESKTOP-CQB09OU/M02C_review_package.zip`.
