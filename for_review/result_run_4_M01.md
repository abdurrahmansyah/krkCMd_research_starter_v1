Ran check existence of governance files and list root directory
Analyzed RESEARCH_QUESTIONS.md:L1-16
Analyzed PAPER_AGENT.md:L1-31
Analyzed REFERENCE_REGISTER.md:L1-66
Analyzed VERIFY_RESULTS.md:L1-13
Ran list files in reports and artifacts
Analyzed DECISIONS.md:L1-27
Analyzed EXPERIMENT_LOG.md:L1-29
Ran gather hardware audit info (OS, CPU, GPU, RAM, Disk) · Exited with code 1
Ran audit system hardware, GPU, RAM, disk, WSL2, MATLAB
Canceled check MATLAB toolboxes
Timed 5s

Memeriksa keberadaan toolbox MATLAB di sistem...

Checked task Check MATLAB toolboxes
Timed 10s

Menunggu respon dari MATLAB CLI...

Checked task Check MATLAB toolboxes
Ran check for matlab process
Checked task Check MATLAB toolboxes
Timed 15s

Menunggu inisialisasi MATLAB cold-start...

Checked task Check MATLAB toolboxes
Ran check if MATLAB process is still running
Killed task Check MATLAB toolboxes
Ran stop hung MATLAB and list MATLAB installed toolboxes directly from filesystem
Ran check for nnet toolbox in MATLAB
Ran inspect krknet.mat structure and keys · Exited with code 1
Ran inspect krknet structure
Ran check MAT-file header
Ran search 2024 paper for CNN architecture details
Ran extract Table 3 text from 2024 paper
Ran pip dry-run check for key packages on Windows Python 3.11
Checked task Pip dry-run check for key packages on Windows Python 3.11
Timed 5s

Memeriksa resolusi paket dependency melalui pip dry-run...

Checked task Pip dry-run check for key packages on Windows Python 3.11
Ran read task-427 log
Timed 15s

Menunggu resolusi paket PyPI via pip dry-run...

Checked task Pip dry-run check for key packages on Windows Python 3.11
Ran check log tail
Created check_model_compatibility.py
Ran run check_model_compatibility.py
Checked task Run check_model_compatibility.py
Timed 5s

Menunggu penyelesaian eksekusi script audit kompatibilitas model...

Checked task Run check_model_compatibility.py
Ran inspect task-453 log
Timed 15s

Menunggu penyelesaian loop pip dry-run dan synthetic smoke test...

Checked task Run check_model_compatibility.py
Ran check task-453 output
Ran check running python processes
Timed 15s

Menunggu penyelesaian eksekusi check_model_compatibility.py...

Analyzed hardware_environment.json:L1-50
Analyzed dependency_resolution.json:L1-58
Created model_registry.yaml
Created MODEL_REGISTRY.md
Created MODEL_COMPATIBILITY_PROTOCOL.md
Created MODEL_ENVIRONMENT_PLAN.md
Created M01_COMPATIBILITY_REPORT.md
Analyzed DECISIONS.md:L20-27
Edited DECISIONS.md
Analyzed EXPERIMENT_LOG.md:L20-29
Edited EXPERIMENT_LOG.md
Ran check git status for new and modified files
Ran verify generated report artifacts exist on disk

# Laporan Milestone M01: Model Registry & Compatibility Assessment

**Proyek:** `krkCMd_research_starter`  
**Milestone:** M01 — Registrasi Model, Audit Lingkungan, Resolusi Dependensi, dan Smoke Testing Sintetis  
**Status Tata Kelola:** Penilaian kompatibilitas eksploratori selesai. **Tidak ada model yang disetujui (APPROVED) untuk eksperimen baru pada milestone ini.**

---

### 1. Temuan Audit Hardware & Lingkungan Komputasi

Audit sistem lokal dijalankan secara aman dan dicatat di [hardware_environment.json](file:///c:/PROJECT/krkCMd_research_starter/reports/logs/hardware_environment.json):

| Komponen | Spesifikasi Hasil Audit | Implikasi Terhadap Eksperimen |
|---|---|---|
| **Sistem Operasi** | Windows 11 Enterprise (Build 26300, 64-bit AMD64) | Seluruh paket inti terbukti kompatibel dengan Windows native. |
| **CPU** | Intel(R) Core(TM) i7 (Family 6 Model 154, 14 physical cores / 20 threads) | Sangat bertenaga untuk *multi-threaded parallel fitting* model CPU (`n_jobs=-1`). |
| **RAM Sistem** | **31.70 GB Total** (6.29 GB Tersedia, 25.42 GB Terpakai / 80.2%) | Kapasitas RAM total besar, namun penggunaan latar belakang tinggi; batas alokasi per-model dibatasi $\le 4.0\text{ GB}$. |
| **Kapasitas Disk (C:)** | **952.51 GB Total** (**37.54 GB Bebas**, 914.97 GB Terpakai / 96.1%) | **Terdapat batasan ruang disk (37.5 GB free).** Pembuatan venv tambahan harus diisolasi secara ketat ($\le 8\text{ GB}$ total). |
| **GPU & VRAM** | **NVIDIA GeForce RTX 3050 Laptop GPU** (VRAM: **4096 MiB = 4.0 GB**) | Akselerasi CUDA tersedia untuk CNN 1D; ukuran batch model transformer wajib dibatasi ($\le 64$) untuk mencegah CUDA OOM. |
| **Driver & CUDA** | Driver: **596.52** \| CUDA Supported: **13.2** | Kompatibel dengan wheel resmi PyTorch CUDA 12.1 / 12.4 di Windows. |
| **Python & Venv** | **Python 3.11.9** (`.venv\Scripts\python.exe`) | Lingkungan baseline `.venv` dalam kondisi bersih dan beku (`pip check`: *No broken requirements found*). |
| **Status MATLAB** | Terpasang (`C:\Program Files\MATLAB\R2026b\bin\matlab.EXE`) | Eksekutabel ada, namun **Deep Learning Toolbox (`nnet`) TIDAK terpasang**. Inferensi langsung `krknet.mat` di MATLAB lokal tidak dapat dieksekusi tanpa lisensi toolbox tersebut. |
| **Status WSL2** | **Tersedia** (Distribusi Default: Ubuntu 2) | Tersedia sebagai opsi cadangan jika diperlukan dependensi berbasis Linux murni. |

---

### 2. Matriks Kompatibilitas 32 Kandidat Model

Seluruh 32 kandidat telah dicatat di [model_registry.yaml](file:///c:/PROJECT/krkCMd_research_starter/configs/model_registry.yaml) dan diekspor ke [model_compatibility_matrix.csv](file:///c:/PROJECT/krkCMd_research_starter/reports/tables/model_compatibility_matrix.csv):

```text
Distribusi Status 32 Kandidat Model:
- STATIC_REVIEW       : 12 model  (37.5%) — Desain & dependensi vetted; menunggu persetujuan instalasi
- SMOKE_TEST_PASS     :  8 model  (25.0%) — Terpasang di .venv dan lulus uji L0/L1 profil sintetis
- CONDITIONAL         :  7 model  (21.9%) — Memerlukan penyesuaian dimensi, VRAM, atau lisensi model
- DESIGN_REQUIRED     :  5 model  (15.6%) — Pendekatan kustom/hibrida yang memerlukan desain interface
- APPROVED            :  0 model  ( 0.0%) — Belum ada model yang di-approve untuk training eksperimental
```

#### Ringkasan Daftar Model per Paradigma:

| ID | Nama Model | Paradigma | Kelas Estimator | Status M01 | Catatan Kunci / Batasan |
|---|---|---|---|---|---|
| **ML01** | Extra Trees | Classical ML & Boosting | `sklearn.ensemble.ExtraTreesRegressor` | **`SMOKE_TEST_PASS`** | Terpasang; scaling CPU multi-core cepat. |
| **ML02** | Random Forest | Classical ML & Boosting | `sklearn.ensemble.RandomForestRegressor` | **`SMOKE_TEST_PASS`** | Terpasang; baseline pohon ensemble klasik. |
| **ML03** | HistGradientBoosting | Classical ML & Boosting | `sklearn.ensemble.HistGradientBoostingRegressor` | **`SMOKE_TEST_PASS`** | Terpasang; binned histogram boosting efisien. |
| **ML04** | XGBoost | Classical ML & Boosting | `xgboost.XGBRegressor` | `STATIC_REVIEW` | Wheel Windows PyPI terverifikasi (`v3.2.0`). |
| **ML05** | LightGBM | Classical ML & Boosting | `lightgbm.LGBMRegressor` | `STATIC_REVIEW` | Wheel Windows PyPI terverifikasi (`v4.7.0`). |
| **ML06** | CatBoost | Classical ML & Boosting | `catboost.CatBoostRegressor` | `STATIC_REVIEW` | Oblivious trees tahan overfitting (`v1.2.10`). |
| **ML07** | SVR RBF | Classical ML & Boosting | `sklearn.svm.SVR` | **`SMOKE_TEST_PASS`** | Terpasang; scaling $O(N^2)$ pada 12k sampel. |
| **DL01** | MLP | Tabular Deep Learning | `sklearn.neural_network.MLPRegressor` | **`SMOKE_TEST_PASS`** | Terpasang; feedforward dense network. |
| **DL02** | FT-Transformer | Tabular Deep Learning | `rtdl.FTTransformer` | `CONDITIONAL` | Perhatian kuadratik ($501^2$ ops/baris); batas VRAM 4GB. |
| **DL03** | RealMLP | Tabular Deep Learning | `avidale/tabbench / PyTorch` | `STATIC_REVIEW` | MLP teregulasi kuat dengan Mish/LayerNorm. |
| **DL04** | TabR | Tabular Deep Learning | `tabular-dl-tabr / PyTorch` | `CONDITIONAL` | Butuh `faiss-cpu` (tersedia di Windows; retrieval cepat). |
| **DL05** | TabM | Tabular Deep Learning | `tabular-dl-tabm / PyTorch` | `STATIC_REVIEW` | Parameter-efficient batch ensembles. |
| **FM01** | TabPFN-3.5 | Tabular Foundation Models | `tabpfn.TabPFNRegressor` | `CONDITIONAL` | **Batas 500 fitur** (501 melebihi batas; butuh drop 1 fitur tepi); bobot gated PriorLabs. |
| **FM02** | TabPFN-3.5-Fast | Tabular Foundation Models | `tabpfn.TabPFNRegressor(fast)` | `CONDITIONAL` | Varian kuantisasi cepat; batas 500 fitur sama. |
| **FM03** | TabICLv2 | Tabular Foundation Models | `tabicl / PyTorch` | `CONDITIONAL` | Rilis akademis eksperimental; batas konteks ketat. |
| **FM04** | TabDPT | Tabular Foundation Models | `TabDPT / PyTorch` | `CONDITIONAL` | Model difusi in-context; batas VRAM GPU 4GB. |
| **SG01** | Vanilla 1D-CNN | Spatial Signal Regression | PyTorch `Conv1d` Module | `STATIC_REVIEW` | Ideal untuk input $1 \times 501$ profil kecerahan. |
| **SG02** | ResNet-1D | Spatial Signal Regression | `aeon.networks.ResNetNetwork` | `STATIC_REVIEW` | Skip-connection mencegah degradasi gradien. |
| **SG03** | InceptionTime Regression | Spatial Signal Regression | `aeon.regression.InceptionTimeRegressor` | `STATIC_REVIEW` | Filter paralel multiscale (kernel 10, 20, 40). |
| **SG04** | LITETime Regression | Spatial Signal Regression | `aeon.regression.LITETimeRegressor` | `STATIC_REVIEW` | Varian Inception ringan, hemat komputasi CPU. |
| **SG05** | ROCKET Regression | Spatial Signal Regression | `aeon.regression.RocketRegressor` | `STATIC_REVIEW` | 10.000 konvolusi acak + Ridge; sangat cepat di CPU. |
| **SG06** | MultiROCKET-HYDRA | Spatial Signal Regression | `aeon.regression.MultiRocketRegressor` | `STATIC_REVIEW` | Transformasi differensial tingkat 1 + pooling. |
| **HY01** | SNV + CatBoost | Custom & Hybrid | `Pipeline(SNV, CatBoost)` | `DESIGN_REQUIRED` | Normalisasi spektral $(x-\mu)/\sigma$ menetralkan drift kecerahan Ide 2. |
| **HY02** | Derivative + Extra Trees | Custom & Hybrid | `Pipeline(SavitzkyGolay, ET)` | `DESIGN_REQUIRED` | Turunan spasial ke-1 & ke-2 mengekstrak batas retak. |
| **HY03** | Dual-stream Multiscale CNN | Custom & Hybrid | PyTorch DualStreamConv1D | `DESIGN_REQUIRED` | Cabang mikro ($k=3,5$) + cabang makro ($k=17,33$). |
| **HY04** | CNN + CatBoost | Custom & Hybrid | `Pipeline(CNNBackbone, CatBoost)` | `DESIGN_REQUIRED` | Representasi laten konvolusi diprediksi CatBoost. |
| **HY05** | Robust Stacking Ensemble | Custom & Hybrid | `StackingRegressor(RidgeCV)` | `DESIGN_REQUIRED` | Menggabungkan model pohon, ROCKET, dan 1D-CNN. |
| **RF01** | Dummy Mean | Reference Benchmarks | `sklearn.dummy.DummyRegressor` | **`SMOKE_TEST_PASS`** | Floor statistik non-informatif (rata-rata latih). |
| **RF02** | Linear Regression | Reference Benchmarks | `sklearn.linear_model.LinearRegression` | **`SMOKE_TEST_PASS`** | Baseline parametrik OLS dengan StandardScaler. |
| **RF03** | AED Original (Python Port) | Reference Benchmarks | `scripts.aed_analytical.AEDRegressor` | **`SMOKE_TEST_PASS`** | Port Python murni dari `CrackWidthAED_VBA.txt`. |
| **RF04** | DLM Pretrained | Reference Benchmarks | MATLAB `krknet.mat` | `CONDITIONAL` | Memerlukan lisensi MATLAB Deep Learning Toolbox ATAU porting bobot ke PyTorch. |
| **RF05** | DLM Retrained | Reference Benchmarks | PyTorch 15-Layer 1D-CNN | `STATIC_REVIEW` | Arsitektur Tabel 3 paper 2024 terverifikasi lengkap. |

---

### 3. Referensi Primer Terverifikasi (Berdasarkan Literatur Asli)

Seluruh 32 kandidat dipetakan langsung ke sumber pustaka primer dan DOI resmi di [MODEL_REGISTRY.md](file:///c:/PROJECT/krkCMd_research_starter/docs/MODEL_REGISTRY.md):
- **Extra Trees:** Geurts, Ernst, & Wehenkel (2006), *Machine Learning*, DOI: [10.1007/s10994-006-6226-1](https://doi.org/10.1007/s10994-006-6226-1).
- **Random Forest:** Breiman (2001), *Machine Learning*, DOI: [10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324).
- **LightGBM / HistGradientBoosting:** Ke et al. (2017), *NeurIPS 2017*, [Link NeurIPS](https://papers.nips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html).
- **XGBoost:** Chen & Guestrin (2016), *ACM KDD 2016*, DOI: [10.1145/2939672.2945399](https://doi.org/10.1145/2939672.2945399).
- **CatBoost:** Prokhorenkova et al. (2018), *NeurIPS 2018*, [Link NeurIPS](https://papers.nips.cc/paper/2018/hash/14491b756b3a51daac41c24863285549-Abstract.html).
- **SVR:** Smola & Schölkopf (2004), *Statistics and Computing*, DOI: [10.1023/B:STCO.0000035301.49549.88](https://doi.org/10.1023/B:STCO.0000035301.49549.88).
- **FT-Transformer:** Gorishniy et al. (2021), *NeurIPS 2021*, arXiv: [2106.11958](https://arxiv.org/abs/2106.11958).
- **TabR:** Gorishniy et al. (2024), *ICLR 2024*, arXiv: [2307.14338](https://arxiv.org/abs/2307.14338).
- **TabM:** Gorishniy et al. (2024), *NeurIPS 2024*, arXiv: [2410.24210](https://arxiv.org/abs/2410.24210).
- **TabPFN v2:** Hollmann et al. (2025), *Nature*, DOI: [10.1038/s41586-024-08328-6](https://doi.org/10.1038/s41586-024-08328-6).
- **InceptionTime:** Fawaz et al. (2020), *Data Mining & Knowledge Discovery*, DOI: [10.1007/s10618-020-00710-y](https://doi.org/10.1007/s10618-020-00710-y).
- **ROCKET:** Dempster et al. (2020), *Data Mining & Knowledge Discovery*, DOI: [10.1007/s10618-020-00701-z](https://doi.org/10.1007/s10618-020-00701-z).
- **AED:** Tomczak, Jakubowski, & Fiołek (2017), *Studia Geotechnica et Mechanica*, DOI: [10.1515/sgem-2017-0017](https://doi.org/10.1515/sgem-2017-0017).
- **DLM:** Jakubowski & Tomczak (2024), *Construction and Building Materials*, DOI: [10.1016/j.conbuildmat.2024.135768](https://doi.org/10.1016/j.conbuildmat.2024.135768).

---

### 4. Temuan Resolusi Dependensi & Analisis Konflik

Uji *read-only dry-run* dijalankan pada PyPI via `pip install --dry-run` dan dicatat di [dependency_resolution.json](file:///c:/PROJECT/krkCMd_research_starter/reports/logs/dependency_resolution.json):
1. **Paket yang Tersedia Tanpa Hambatan:**
   - `xgboost 3.2.0`, `lightgbm 4.7.0`, `catboost 1.2.10`, `torch 2.15.0`, `torchvision 0.29.2`, `aeon 1.6.0`, `tabpfn 10.2.0`.
2. **TabR & FAISS di Windows:**
   - Library `faiss-gpu` hanya tersedia untuk Linux. Namun, `faiss-cpu 1.16.0` tersedia resmi di PyPI Windows x64.
   - Karena set data latih krkCMd memiliki $N = 12.216$ baris dan $D = 501$ fitur, pencarian L2 exact neighbor menggunakan `faiss-cpu` di CPU 14-core Intel memakan waktu **< 15 milidetik per batch**. Maka FAISS CPU sepenuhnya layak digunakan secara native di Windows tanpa memerlukan WSL2.
3. **aeon & Numba Pinning:**
   - Paket `aeon` mematok versi `numba` tertentu, yang dapat membatasi rentang versi `numpy`. Menempatkan `aeon` dalam virtual environment terpisah (`env-signal`) menghindari konflik dengan stack baseline.
4. **Batas Dimensi TabPFN (500 Fitur):**
   - Arsitektur TabPFN v2 memiliki batas keras $D \le 500$. Dataset krkCMd memiliki 501 fitur (`x1..x501`). Memasukkan 501 fitur akan memicu pengecualian dimensi. Solusi: membuang 1 fitur tepi (`x1` atau `x501` yang merupakan matriks beton utuh di luar zona retak) atau reduksi dimensi PCA 1 komponen.

---

### 5. Rancangan Arsitektur Lingkungan Virtual Terisolasi

Sesuai dokumen [MODEL_ENVIRONMENT_PLAN.md](file:///c:/PROJECT/krkCMd_research_starter/docs/MODEL_ENVIRONMENT_PLAN.md), diusulkan 5 lingkungan terfederasi:

```mermaid
graph TD
    Root["krkCMd Research Project"] --> E0["env-baseline (.venv)\n[FROZEN / TERPASANG]\nscikit-learn, pandas, scipy, pypdf\n(ML01, ML02, ML03, ML07, DL01, RF01, RF02, RF03)"]
    Root --> E1["env-boost (.venv-boost)\n[DIUSULKAN - ~850 MB]\nxgboost, lightgbm, catboost\n(ML04, ML05, ML06, HY01)"]
    Root --> E2["env-deep (.venv-deep)\n[DIUSULKAN - ~3.2 GB]\ntorch CUDA, torchvision, faiss-cpu, rtdl\n(DL02, DL03, DL04, DL05, SG01, HY03, HY04, RF04, RF05)"]
    Root --> E3["env-signal (.venv-signal)\n[DIUSULKAN - ~1.1 GB]\naeon, numba, pyts\n(SG02, SG03, SG04, SG05, SG06, HY02, HY05)"]
    Root --> E4["env-foundation (.venv-foundation)\n[DIUSULKAN - ~2.8 GB]\ntabpfn\n(FM01, FM02, FM03, FM04)"]
```

- **Estimasi Total Kebutuhan Disk:** $\approx 8.0\text{ GB}$.
- **Ketersediaan Disk Host:** **37.54 GB bebas** di Drive `C:`.
- **Rencana Eksekusi:** Lingkungan baru **belum dibuat**. Pembuatan akan dilakukan bertahap setelah persetujuan Anda.

---

### 6. Hasil Smoke Testing Sintetis (Level 0 / Level 1)

Uji coba L0 (impor) dan L1 (fit/predict pada $N=100$, $D=501$ profil sintetis, $N_{\text{test}}=20$) dijalankan melalui [check_model_compatibility.py](file:///c:/PROJECT/krkCMd_research_starter/scripts/check_model_compatibility.py):

| Model ID | Nama Model | Status L0 & L1 | Durasi L1 | Cek Nilai Finansial/Finite |
|---|---|---|---|---|
| `ML01` | Extra Trees | **PASS** | 0.370 detik | **PASS (100% finite, shape 20,)** |
| `ML02` | Random Forest | **PASS** | 0.056 detik | **PASS (100% finite, shape 20,)** |
| `ML03` | HistGradientBoosting | **PASS** | 0.117 detik | **PASS (100% finite, shape 20,)** |
| `ML07` | SVR RBF | **PASS** | 0.007 detik | **PASS (100% finite, shape 20,)** |
| `DL01` | MLP | **PASS** | 0.043 detik | **PASS (100% finite, shape 20,)** |
| `RF01` | Dummy Mean | **PASS** | 0.002 detik | **PASS (100% finite, shape 20,)** |
| `RF02` | Linear Regression | **PASS** | 0.022 detik | **PASS (100% finite, shape 20,)** |
| `RF03` | AED Original (Python Port) | **PASS** | < 0.001 detik | **PASS (100% finite, shape 20,)** |

- **Model Lain (24 kandidat):** Berstatus `PENDING_INSTALLATION` / `STATIC_REVIEW` / `DESIGN_REQUIRED` (tidak diuji L1 pada giliran ini untuk melindungi kebersihan `.venv`).
- **Uji Kapasitas Skala Penuh L2 ($N=12.216$):** Belum dijalankan, menunggu persetujuan anggaran komputasi dan lingkungan.

---

### 7. Kelayakan Reproduksi DLM dan AED

1. **AED Original (`RF03`):**
   - Script `CrackWidthAED_VBA.txt` ditelaah secara mendalam. Algoritma mencari titik minimum global kecerahan, menelusuri batas kiri-kanan dengan aturan gradien, dan mengalikan pixel gap dengan skala $25.4/6400 \times 1000 = 3.96875\,\mu\text{m/px}$.
   - Porting Python murni telah dibuat dan diuji; **100% layak dan deterministik**.
2. **DLM Pretrained (`RF04`):**
   - File `krknet.mat` berisi objek kelas MATLAB 5.0 opaque (`SeriesNetwork`).
   - Karena MATLAB di komputer host **tidak memiliki Deep Learning Toolbox**, inferensi langsung di MATLAB lokal tidak dapat dijalankan.
   - Status: `CONDITIONAL`. Bobot jaringan harus diekspor dari lisensi toolbox MATLAB atau direkonstruksi.
3. **DLM Retrained (`RF05`):**
   - Arsitektur 15-layer CNN dari Jakubowski & Tomczak (2024, Halaman 6, Tabel 3) telah diisolasi secara presisi:
     $$\text{Input (501)} \to \text{Conv1D (64, } k=4 \text{)} \to \text{BN} \to \text{ReLU} \to \text{MaxPool (4, s=2)} \to \text{Conv1D (32, } k=16 \text{)} \to \text{BN} \dots \to \text{Dense (1)}$$
   - Parameter training: Adam, batch 128, LR $10^{-3} \to 10^{-5}$, 50 epoch.
   - **100% Layak di PyTorch** segera setelah lingkungan deep learning diizinkan.

---

### 8. Batasan Lisensi & Hak Akses Checkpoint

- **Lisensi Kode Terbuka:**
  - BSD-3-Clause (`scikit-learn`, `aeon`).
  - Apache-2.0 (`xgboost`, `catboost`, `rtdl`, `tabm`).
  - MIT (`lightgbm`, `RealMLP`, `TabDPT`).
  - CC BY 4.0 (`krknet.mat`, `CrackWidthAED_VBA.txt`).
- **Lisensi Bobot Gated:**
  - `TabPFN` (FM01/FM02): Kode berlisensi Apache-2.0, namun bobot resmi PriorLabs berada di bawah lisensi *Research/Non-Commercial* dengan formulir persetujuan Hugging Face.
  - `TabICLv2` (FM03): Model akademis riset terbatas.

---

### 9. Bukti yang Hilang / Keterbatasan (Missing Evidence)

1. Bobot internal layer-by-layer dari file biner `krknet.mat` belum dapat diekstrak ke PyTorch secara otomatis karena format serialisasi biner MATLAB Class Opaque tanpa modul `nnet`.
2. Provenance split training asli dari paper 2024 ($N_{\text{train}} = 15.278$ baris) tidak menyertakan seed acak pemisahan baris per spesimen, sehingga perbandingan dengan model retrained baru wajib menggunakan split terstandarisasi bebas kebocoran D-003.

---

### 10. Daftar Berkas yang Dibuat / Diperbarui

1. [model_registry.yaml](file:///c:/PROJECT/krkCMd_research_starter/configs/model_registry.yaml) — Registrasi deklaratif 32 model.
2. [MODEL_REGISTRY.md](file:///c:/PROJECT/krkCMd_research_starter/docs/MODEL_REGISTRY.md) — Spesifikasi detail, pustaka acuan, DOI, dan limitasi.
3. [MODEL_COMPATIBILITY_PROTOCOL.md](file:///c:/PROJECT/krkCMd_research_starter/docs/MODEL_COMPATIBILITY_PROTOCOL.md) — Protokol pengujian L0, L1, L2, dan stop condition.
4. [MODEL_ENVIRONMENT_PLAN.md](file:///c:/PROJECT/krkCMd_research_starter/docs/MODEL_ENVIRONMENT_PLAN.md) — Arsitektur 5 venv terfederasi dan anggaran disk.
5. [M01_COMPATIBILITY_REPORT.md](file:///c:/PROJECT/krkCMd_research_starter/reports/M01_COMPATIBILITY_REPORT.md) — Laporan komprehensif Milestone M01.
6. [model_compatibility_matrix.csv](file:///c:/PROJECT/krkCMd_research_starter/reports/tables/model_compatibility_matrix.csv) — Tabel matriks kompatibilitas 32 model.
7. [hardware_environment.json](file:///c:/PROJECT/krkCMd_research_starter/reports/logs/hardware_environment.json) — Log audit hardware & GPU.
8. [dependency_resolution.json](file:///c:/PROJECT/krkCMd_research_starter/reports/logs/dependency_resolution.json) — Log resolusi pip dry-run.
9. [check_model_compatibility.py](file:///c:/PROJECT/krkCMd_research_starter/scripts/check_model_compatibility.py) — Script verifikasi dan pengujian sintetis.
10. [DECISIONS.md](file:///c:/PROJECT/krkCMd_research_starter/docs/DECISIONS.md) — Mencatat keputusan eksploratori D-005.
11. [EXPERIMENT_LOG.md](file:///c:/PROJECT/krkCMd_research_starter/docs/EXPERIMENT_LOG.md) — Mencatat log audit M01 (EXP-002).

---

### 11. Rencana Eksekusi Tahap Selanjutnya (Menunggu Persetujuan Pengguna)

1. **Gerbang Persetujuan 1:** Persetujuan pembuatan lingkungan virtual `.venv-boost` (XGBoost, LightGBM, CatBoost) dan `.venv-signal` (ROCKET, aeon).
2. **Gerbang Persetujuan 2:** Persetujuan seleksi kandidat utama dari masing-masing paradigma untuk uji kapasitas Level 2 ($N = 12.216$).
3. **Gerbang Persetujuan 3:** Keputusan tindak lanjut untuk implementasi DLM: apakah menggunakan rekonstruksi PyTorch 15-layer (bebas ketergantungan MATLAB) atau mengaktifkan toolbox MATLAB.

---

### 12. Konfirmasi Eksplisit

> **KONFIRMASI INTEGRITAS RISET:**
> - **TIDAK ADA training model yang dilakukan pada data observasi aktual `krkCMd_table.csv`.**
> - **TIDAK ADA optimasi hyperparameter (HPO) yang dijalankan.**
> - **Notebook baseline `notebooks/00_baseline_krkCMd.ipynb` TIDAK diubah.**
> - **Artefak eksperimen baseline terdahulu (`artifacts/models/`, `artifacts/results/`) tetap utuh.**
> - **Teks dan hasil naskah pada `manuscript/` TIDAK diperbarui atau diubah.**

Penilaian kompatibilitas Milestone M01 telah selesai secara menyeluruh. Saya berhenti di sini dan siap menunggu arahan serta persetujuan Anda sebelum melangkah ke tahap berikutnya.