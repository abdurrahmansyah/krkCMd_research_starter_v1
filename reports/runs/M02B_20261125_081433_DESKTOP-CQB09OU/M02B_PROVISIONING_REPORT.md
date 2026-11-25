# Laporan Provisioning, Verifikasi GPU & Uji Kapasitas M02B

**Proyek:** `krkCMd_research_starter`  
**Run ID:** `M02B_20261125_081433_DESKTOP-CQB09OU`  
**Tanggal:** 2026-11-25  
**Workstation:** `DESKTOP-CQB09OU` (Core i9-10900KF 20T, `127.92 GiB` RAM, **NVIDIA Quadro RTX 6000** `24 GiB` VRAM Turing `sm_75`, Windows 11 Pro, Python `3.11.9`)  

---

## 1. Perbaikan Infrastruktur Kompatibilitas (Bagian 2)

1. **Matriks Berbasis Registry:** [scripts/build_compatibility_matrix.py](file:///c:/PROJECT/krkCMd_research_starter_v1/scripts/build_compatibility_matrix.py) membaca `configs/model_registry.yaml` sebagai sumber otoritatif dan merekonsiliasi bukti runtime M02A & M02B ke [model_compatibility_matrix_M02B.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02B_20261125_081433_DESKTOP-CQB09OU/model_compatibility_matrix_M02B.csv) (`0` model `APPROVED`).
2. **Depresiasi Skrip Lama:** [scripts/check_model_compatibility.py](file:///c:/PROJECT/krkCMd_research_starter_v1/scripts/check_model_compatibility.py) resmi didepresiasi (keluar dengan kode `2` kecuali `--legacy-allow-overwrite`).
3. **Watchdog Sumber Daya:** [scripts/resource_policy.py](file:///c:/PROJECT/krkCMd_research_starter_v1/scripts/resource_policy.py) kini menegakkan timeout, plafon RSS process-tree (`64 GiB`), cadangan RAM (`16 GiB`), cadangan VRAM (`2,5 GiB` via `nvidia-smi`, dengan catatan keterbatasan pengukuran per-proses di Windows WDDM), file log `stdout`/`stderr` (bebas *pipe deadlock*), dan terminasi *process-tree*.

---

## 2. Lingkungan Terisolasi, Verifikasi GPU & Kernel Jupyter

- **`.venv-deep`** (`krkcmd-deep`, `994,97 s`, `pip check` bersih): `torch==2.9.1+cu128`, `rtdl_revisiting_models==0.0.2`, `rtdl_num_embeddings==0.0.12`, `tabm==0.0.3`, `pytabkit`, `delu==0.0.26`, `einops==0.8.2`, `numpy==2.4.6`, `pandas==3.1.1`, `scikit-learn==1.9.1`.
- **`.venv-signal-tf`** (`krkcmd-signal-tf`, `156,55 s`, `pip check` bersih): `aeon==1.6.0`, `tensorflow==2.21.0`, `keras==3.15.1`, `numba==0.63.1`, `numpy==2.3.5`. Eksekusi **`CPU_ONLY`**.
- **`.venv-signal-hydra`** (`krkcmd-signal-hydra`, `222,74 s`, `pip check` bersih): `aeon==1.6.0`, `torch==2.9.1+cu128`, `numba==0.63.1`, `numpy==2.3.5`. Eksekusi **`CPU`**.
- **Verifikasi GPU Aktual ([gpu_runtime_verification_M02B.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02B_20261125_081433_DESKTOP-CQB09OU/gpu_runtime_verification_M02B.json)):** **`GPU_PASS`** pada `Quadro RTX 6000` (`CC [7, 5]`, CUDA `12.8`, `torch==2.9.1+cu128`): matmul + `Conv1d` FP32 (`1,5638 s`, finite), FP16 AMP (finite), dan SDPA Turing (`math`/`mem_efficient`, finite), peak CUDA allocated `19,312 MiB`.
- **Kernel Jupyter ([kernel_verification_M02B.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02B_20261125_081433_DESKTOP-CQB09OU/kernel_verification_M02B.json)):** `krkcmd-deep`, `krkcmd-signal-tf`, dan `krkcmd-signal-hydra` seluruhnya lulus `nbclient` smoke check.

---

## 3. Hasil Uji 11 Kandidat Target M02B (Data Sintetis `seed=42`, `D=501`)

| ID | Implementasi & Env | Device | L0 | L1 (100→20) + Serialisasi | L2A (1000→200) | L2B (4096→1024) | L2C (12216→3822) | Peak RSS / VRAM L2C | Status Akhir |
|---|---|---|---|---|---|---|---|---|---|
| **DL01** | `torch.nn.Sequential` MLP (`.venv-deep`) | `cuda:0` | `PASS` | `PASS` (diff `0,0`) | `PASS` (`1,60 s`) | `PASS` (`2,35 s`) | `PASS` (`4,31 s` fit) | `991,9 MiB` / `18,9 MiB` | **`SCALE_CHECK_PASS`** |
| **DL02** | `rtdl_revisiting_models.FTTransformer` (`.venv-deep`, `502` token, `bs=32`) | `cuda:0` | `PASS` | `PASS` (diff `0,0`) | `PASS` (`3,28 s`) | `PASS` (`10,74 s`) | `PASS` (`26,59 s` fit) | `1.074,3 MiB` / `534,8 MiB` | **`SCALE_CHECK_PASS`** |
| **DL03** | `pytabkit.RealMLP_TD_Regressor` (`.venv-deep`, `n_epochs=5`) | `cuda:0` | `PASS` | `PASS` (diff `0,0`) | `PASS` (`1,46 s`) | `PASS` (`4,47 s`) | `PASS` (`11,19 s` fit) | `1.493,5 MiB` / `612,6 MiB` | **`SCALE_CHECK_PASS`** |
| **DL04** | `yandex-research/tabular-dl-tabr` (`17baa908`) | — | `CONDITIONAL` | `NOT_EXECUTED` | `NOT_EXECUTED` | `NOT_EXECUTED` | `NOT_EXECUTED` | — | **`CONDITIONAL`** *(repo-only, non-PyPI)* |
| **DL05** | `tabm.TabM` (`.venv-deep`, **`k=8`** ensemble) | `cuda:0` | `PASS` | `PASS` (diff `0,0`) | `PASS` (`2,24 s`) | `PASS` (`3,06 s`) | `PASS` (`6,14 s` fit) | `1.125,3 MiB` / `20,6 MiB` | **`SCALE_CHECK_PASS`** |
| **SG01** | `torch.nn` `VanillaConv1DRegressor` (`.venv-deep`) | `cuda:0` | `PASS` | `PASS` (diff `0,0`) | `PASS` (`1,79 s`) | `PASS` (`2,80 s`) | `PASS` (`5,62 s` fit) | `1.104,4 MiB` / `46,3 MiB` | **`SCALE_CHECK_PASS`** |
| **SG02** | `aeon...ResNetRegressor` (`.venv-signal-tf`) | `CPU_ONLY` | `PASS` | `PASS` (diff `0,0`) | `PASS` (`19,48 s`) | `PASS` (`62,08 s`) | `PASS` (`174,78 s` fit) | `826,5 MiB` / `N/A` | **`SCALE_CHECK_PASS`** *(CPU)* |
| **SG03** | `aeon...InceptionTimeRegressor` (`.venv-signal-tf`) | `CPU_ONLY` | `PASS` | `PASS` (diff `0,0`) | `PASS` (`24,34 s`) | `PASS` (`88,30 s`) | `PASS` (`234,27 s` fit) | `935,8 MiB` / `N/A` | **`SCALE_CHECK_PASS`** *(CPU)* |
| **SG04** | `aeon...LITETimeRegressor` (`.venv-signal-tf`) | `CPU_ONLY` | `PASS` | `PASS` (diff `0,0`) | `PASS` (`5,01 s`) | `PASS` (`10,48 s`) | `PASS` (`27,66 s` fit) | `630,6 MiB` / `N/A` | **`SCALE_CHECK_PASS`** *(CPU)* |
| **SG06** | `aeon...MultiRocketHydraRegressor` (`.venv-signal-hydra`) | `CPU` | `PASS` | `PASS` (diff `0,0`) | `PASS` (`7,55 s`) | `PASS` (`39,99 s`, `15,73 GiB` RSS) | **`FAILED`** (`WALL_CLOCK_TIMEOUT 300s`, `26,35 GiB` RSS) | `26.348,3 MiB` | **`FAILED` di L2C** *(L2B PASS)* |
| **RF05** | `DLM15LayerCNN_Table3` (`.venv-deep`, `SGDM lr=1e-3`) | `cuda:0` | `PASS` | `PASS` (diff `0,0`) | **`FAILED`** (`FloatingPointError: Non-finite loss`) | `NOT_EXECUTED` | `NOT_EXECUTED` | `1.072,9 MiB` | **`FAILED` di L2A** *(L1 PASS; butuh normalisasi input)* |

- **Penjelasan Transparan Kegagalan:**
  - **`RF05` L2A:** `FloatingPointError: Non-finite training loss encountered` dengan `SGD(lr=1e-3, momentum=0.9)` pada input mentah `[0, 255]` tanpa normalisasi, mengonfirmasi pentingnya *zero-center normalization* pada Layer 1 Tabel 3 ([RF05_REPRODUCTION_FEASIBILITY.md](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02B_20261125_081433_DESKTOP-CQB09OU/RF05_REPRODUCTION_FEASIBILITY.md)).
  - **`SG06` L2C:** Watchdog menghentikan proses pada batas `300 s` (`WALL_CLOCK_TIMEOUT (300s)`) saat RSS mencapai `26.348,34 MiB` (~25,7 GiB). `SG06` tetap dipertahankan di registry (bukan dieliminasi).
  - **`DL04` (`TabR`):** Tetap `CONDITIONAL` karena `tabular-dl-tabr` tidak tersedia di PyPI (`404`) dan membutuhkan integrasi repo khusus (`17baa908`) + FAISS.

---

## 4. Unit Test, Pelestarian Lingkungan & Status 32 Kandidat

- **Unit Test (`unit_test_results_M02B.txt`):** **`27/27` tests `OK`** dalam `1,479 s` (termasuk pengujian watchdog RAM reserve breach, pipe deadlock `200 KB`, rekonsiliasi registry, dan kontrak adapter).
- **Matriks 32 Kandidat ([model_compatibility_matrix_M02B.csv](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M02B_20261125_081433_DESKTOP-CQB09OU/model_compatibility_matrix_M02B.csv)):** `0` kandidat berstatus `APPROVED`.
- **Integritas Baseline & M02A:** `.venv`, `.venv-boost`, `.venv-signal-cpu`, `krkCMd_table.csv`, `group_split_manifest.csv`, dan `manuscript/` tetap **100% utuh**.

---

### TINDAKAN MANUAL PENELITI

- **Instalasi software manual:** **Tidak ada** (`.venv-deep`, `.venv-signal-tf`, dan `.venv-signal-hydra` sudah terpasang otomatis; `.venv-foundation` untuk M02C menunggu persetujuan Anda).
- **Eksekusi notebook manual:** **Tidak perlu** menjalankan notebook apa pun secara manual.
- **Pilihan kernel Jupyter:** `krkcmd-deep` (`Python (krkCMd - Deep Learning CUDA)`), `krkcmd-signal-tf` (`Python (krkCMd - Signal TF/Keras)`), `krkcmd-signal-hydra` (`Python (krkCMd - Signal HYDRA)`), serta kernel sebelumnya (`krkcmd-research-newpc`, `krkcmd-boost`, `krkcmd-signal-cpu`).
- **Persetujuan lisensi / akses akun:** Diperlukan **nanti pada M02C** sebelum mengunduh bobot *gated* `FM01–FM02` (PriorLabs / Hugging Face).
- **Tindakan Git yang disarankan:** Tinjau `git status` dan lakukan `git commit`/`git push` secara manual setelah review jika diinginkan (pastikan `.venv-*` tidak ikut ter-stage).
- **Berkas yang harus diunggah ke ChatGPT untuk review:**
  1. `result_run_8_M02B.md` — hasil ekspor percakapan Antigravity.
  2. `M02B_review_package.zip` — paket review ringan di `reports/runs/M02B_20261125_081433_DESKTOP-CQB09OU/M02B_review_package.zip`.
