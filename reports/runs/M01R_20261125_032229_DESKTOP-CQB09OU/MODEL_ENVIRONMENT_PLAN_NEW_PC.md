# MODEL_ENVIRONMENT_PLAN_NEW_PC.md — Strategi Lingkungan & Anggaran Sumber Daya Workstation Baru

**Run ID:** `M01R_20261125_032229_DESKTOP-CQB09OU`  
**Tanggal:** 2026-11-25  
**Host:** `DESKTOP-CQB09OU` (Windows Pro 24H2 Build `26100.9711`, 64-bit AMD64)  
**Kebijakan Tata Kelola:** Lingkungan baseline `.venv` telah direkonstruksi secara bersih dan **dibekukan (frozen)** untuk reproduksibilitas M00. **Tidak ada lingkungan M02 yang dibuat atau diinstal pada milestone M01-R.**

---

## 1. Perbandingan Kapasitas Host: PC Lama vs. Workstation Baru (Data Terukur)

Seluruh angka di bawah berasal dari hasil pengukuran aktual ([hardware_environment.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/hardware_environment.json) vs. log historis [reports/logs/hardware_environment.json](file:///c:/PROJECT/krkCMd_research_starter_v1/reports/logs/hardware_environment.json)):

| Komponen | PC Lama | Workstation Baru (`DESKTOP-CQB09OU`) | Perubahan Kapasitas |
|---|---|---|---|
| **CPU** | Intel Core i7 (14C / 20T) | Intel Core i9-10900KF @ 3.70 GHz (20 logical threads, AVX2) | Frekuensi tinggi; `ExtraTrees` 2,12× lebih cepat, `RandomForest` 1,72× lebih cepat |
| **RAM Total / Tersedia** | 31,70 GB / **6,29 GB** | **127,92 GB / 113,36 GB** (terpakai 11%) | **+107,07 GB RAM tersedia** (18× lebih lega) |
| **Disk `C:` Free** | **37,54 GB** / 952,51 GB | **1.752,80 GB** / 1.906,74 GB | **46,7× lebih luas** (kendala disk lama tereliminasi) |
| **GPU & VRAM** | RTX 3050 Laptop (**4,0 GB** VRAM) | **Quadro RTX 6000** (**24.576 MiB = 24,0 GB VRAM**, `22.974 MiB` bebas, CC `7.5`) | **6× VRAM lebih besar** (hambatan OOM 4 GB teratasi) |
| **Driver / CUDA UMD** | Driver `596.52` / CUDA `13.2` | Driver `621.24` / CUDA UMD `13.5` (Toolkit sistem belum terpasang) | Siap wheel CUDA PyTorch `cu126`/`cu128`/`cu130` |
| **MATLAB / WSL2 / Docker** | MATLAB R2026b (tanpa `nnet`), WSL2 Ubuntu | **Tidak terpasang** (MATLAB, WSL2, Docker, VS Code tidak ada) | `RF04` jalur MATLAB lokal tidak tersedia; jalur PyTorch menjadi utama |

---

## 2. Strategi Isolasi Multi-Lingkungan (Diusulkan, Belum Diinstal)

Pemisahan lingkungan tetap wajib meskipun disk kini sangat lega (1,75 TB bebas), karena hasil *dry-run* transitif membuktikan adanya perbedaan batasan dependensi antar-ekosistem:
- Pada `env-signal-cpu` (`aeon 1.6.0` + `numba 0.63.1`), `numba` membatasi `numpy` ke `2.3.5` dan menarik `pandas 3.0.6`, berbeda dari `numpy 2.4.6` & `pandas 2.3.3` di `.venv` baseline.
- Pada PyTorch, indeks default PyPI (`torch 2.15.0`) mengirim wheel CPU lebih baru dari indeks CUDA `download.pytorch.org/whl/cu128` (`torch 2.9.1+cu128`), sehingga `--extra-index-url` saja keliru memilih wheel CPU. Lingkungan deep learning harus memakai `--index-url https://download.pytorch.org/whl/cu128` (atau `cu126`/`cu130`) secara eksplisit untuk komponen `torch`/`torchvision`.

| Nama Env | Path Usulan | Python | Kandidat Model | Paket Inti Terverifikasi (*Dry-Run*) | Estimasi Disk |
|---|---|---|---|---|---|
| **`env-baseline`** | `.venv` *(TERPASANG)* | `3.11.9` | `ML01–03`, `ML07`, `DL01`(sklearn), `RF01–02`, `RF03`(proto), `HY02` | `scikit-learn 1.9.1`, `numpy 2.4.6`, `pandas 2.3.3`, `scipy 1.17.1` | ~0,6 GB *(Terukur di `.venv`)* |
| **`env-boost`** | `.venv-boost` | `3.11.9` | `ML04`, `ML05`, `ML06`, `HY01` | `xgboost 3.2.0`, `lightgbm 4.7.0`, `catboost 1.2.10`, `numpy 2.4.6` *(25 pkg)* | ~1,0 GB *(Estimasi)* |
| **`env-deep`** | `.venv-deep` | `3.11.9` | `DL02–05`, `SG01`, `HY03–04`, `RF04`(port), `RF05` | `torch 2.9.1+cu128` (indeks `cu128`), `faiss-cpu 1.16.0`, `rtdl-num-embeddings 0.0.12`, `tabm 0.0.3` | ~5,5 GB *(Estimasi incl. CUDA runtime wheel)* |
| **`env-signal-cpu`** | `.venv-signal-cpu` | `3.11.9` | `SG05`, `SG06`, `HY05` | `aeon 1.6.0`, `numba 0.63.1`, `numpy 2.3.5`, `scipy 1.17.1` *(17 pkg)* | ~1,1 GB *(Estimasi)* |
| **`env-signal-tf`** | `.venv-signal-tf` *(Opsional)* | `3.11.9` | `SG02–04` (jika memakai backend TF/Keras di `aeon`) | `aeon 1.6.0`, `tensorflow 2.21.0`, `keras 3.15.1`, `numba 0.63.1` *(45 pkg)* | ~2,8 GB *(Estimasi)* |
| **`env-foundation`** | `.venv-foundation` *(Gated)* | `3.11.9` | `FM01–04` | `tabpfn 10.2.0`, `tabicl 2.2.0`, `tabdpt 1.3.2`, `huggingface_hub 2.4.0`, `torch` CUDA | ~6,0 GB *(Estimasi incl. cache bobot)* |

*Catatan `xgboost`:* Versi PyPI terbaru (`3.4.1`) mensyaratkan `Python >= 3.12`. Pada Python `3.11.9`, *resolver* otomatis memilih `xgboost 3.2.0` tanpa konflik.

---

## 3. Strategi PyTorch/CUDA, TensorFlow, CPU-Only, dan WSL2 Fallback

1. **PyTorch / CUDA Build:**
   - Driver NVIDIA `621.24` melaporkan dukungan hingga CUDA UMD `13.5`, sedangkan Quadro RTX 6000 memakai arsitektur Turing (`Compute Capability 7.5`).
   - Rekomendasi: gunakan **`--index-url https://download.pytorch.org/whl/cu128`** (menyediakan `torch 2.9.1+cu128` untuk `cp311-win_amd64`, sudah mencakup runtime CUDA tanpa perlu instalasi CUDA Toolkit sistem secara terpisah). Setelah pembuatan lingkungan disetujui, wajib verifikasi komputasi GPU nyata (`torch.cuda.is_available()` dan operasi tensor di device `cuda:0`).
2. **Strategi TensorFlow (`env-signal-tf`):**
   - `tensorflow 2.21.0` + `keras 3.15.1` + `aeon 1.6.0` berhasil di-resolve pada Windows Python 3.11 (`45` paket). Namun karena `tensorflow` Windows native sejak >2.10 tidak mendukung GPU secara native tanpa WSL2/DirectML, gunakan `env-signal-tf` hanya untuk eksekusi CPU atau pertimbangkan implementasi PyTorch murni jika akselerasi GPU diperlukan pada tahap M01.1/M02.
3. **CPU-Only Environments:**
   - `env-baseline`, `env-boost` (CPU default, GPU opsional via parameter CUDA XGBoost/CatBoost), dan `env-signal-cpu` (`ROCKET`/`MultiRocket` berbasis Numba multi-core) berjalan optimal secara native di Windows CPU 20-thread.
4. **WSL2 Fallback:**
   - WSL2 saat ini **tidak terpasang** di `DESKTOP-CQB09OU`. Mengingat `faiss-cpu 1.16.0`, `aeon 1.6.0`, `tabpfn 10.2.0`, `tabicl 2.2.0`, dan `tabdpt 1.3.2` semuanya memiliki distribusi PyPI untuk Python 3.11 Windows, **WSL2 belum diperlukan** untuk fase M01.1/M02 awal. WSL2 hanya diusulkan sebagai fallback terpisah jika nanti muncul paket *research-only* yang memerlukan kompilasi Linux atau `faiss-gpu` / TensorFlow GPU.

---

## 4. Lokasi Cache Checkpoint & Anggaran Sumber Daya Dinamis

- **Lokasi Cache Checkpoint:**  
  Tetapkan `HF_HOME` / `TORCH_HOME` ke direktori khusus pada drive `C:` (misalnya `C:\PROJECT\krkCMd_research_starter_v1\.cache\hf` dan `.cache\torch`, atau `C:\Users\Nur Ridho A\.cache\`), dan pastikan folder `.cache/` ditambahkan ke `.gitignore` sebelum mengunduh bobot apa pun.
- **Anggaran Sumber Daya Berbasis Kapasitas Tersedia (Bukan Sekadar Total Terpasang):**

| Parameter Anggaran | Batas PC Lama (Historis) | Anggaran Baru (`DESKTOP-CQB09OU`) | Dasar Penetapan |
|---|---|---|---|
| **Disk Budget Total Semua Env + Cache** | $\le 8,0\text{ GB}$ (dari 37,54 GB free) | **Maks. 30 GB** (dari **1.752,80 GB** free; `< 2%` ruang bebas) | Terukur 1.752,80 GB bebas *(estimasi total env+cache ~17–25 GB)* |
| **RAM Reserve & Plafon per Proses** | Maks. 4,0–8,0 GB (hanya 6,29 GB free) | **Sisakan cadangan sistem $\ge 16\text{ GB}$**; plafon per proses **maks. `min(64 GB, 0.70 × RAM_tersedia)`** (~79 GB saat kondisi idle 113,36 GB free) | Terukur 113,36 GB tersedia saat audit; cegah OOM jika ada proses latar |
| **VRAM Reserve & Plafon GPU** | Maks. 3,5 GB (dari 4,0 GB) | **Sisakan cadangan display $\ge 2,5\text{ GB}$**; plafon per proses **maks. `min(20 GB, 0.85 × VRAM_tersedia)`** (~19,5 GB saat 22,97 GB free) | Terukur 22.974 MiB bebas dari 24.576 MiB (Quadro RTX 6000 sedang menggerakkan WDDM display 1.282 MiB) |
| **CPU Thread Budget** | `n_jobs=-1` (20 thread, RAM ketat) | Default `n_jobs=16` untuk proses tunggal paralel (menyisakan 4 thread untuk OS/IO), atau `n_jobs=-1` untuk benchmark tunggal tanpa konkurensi | 20 logical threads terukur |
| **Max Concurrent Workers** | 1 worker | **1 worker GPU** (eksklusif pada GPU tunggal `cuda:0`) atau **maks. 2 worker CPU** dengan pembagian thread (`OMP_NUM_THREADS=8`, `n_jobs=8`) | Mencegah *oversubscription* thread & kontensi VRAM |
| **Timeout Strategy (L2 / Training)** | 300 s (klasik) / 900 s (DL) | Klasik/Boosting/ROCKET: **300 s**; Deep Learning / TabR / Foundation: **900 s** (dengan guard `psutil` + `torch.cuda.max_memory_allocated` per subprocess) | Menjaga keamanan eksekusi otomatis |

---

## 5. Catatan Ketidakpastian & Prasyarat Persetujuan

1. Semua ukuran disk env baru dan waktu eksekusi model M02 di atas adalah **estimasi**, kecuali spesifikasi hardware dan hasil resolusi dependensi *dry-run*.
2. `FM01–FM03` membutuhkan penerimaan lisensi *gated* oleh peneliti secara langsung (`huggingface-cli login` / persetujuan lisensi PriorLabs).
3. **Tidak ada lingkungan baru (`env-boost`, `env-deep`, `env-signal-*`, `env-foundation`) yang dibuat dalam M01-R.** Pembuatan lingkungan hanya boleh dilakukan setelah persetujuan peneliti (dan setelah perbaikan M01.1 jika dipilih berurutan).
