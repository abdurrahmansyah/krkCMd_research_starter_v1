# AGENT.md — krkCMd Crack-Width Research

> **Peran dokumen:** instruksi induk untuk coding agent (Codex, Antigravity, IDE agent, atau sejenisnya).
> **Status:** living document. Dokumen ini boleh berkembang, tetapi perubahan harus tercatat dan tidak boleh menghapus keputusan/hasil eksperimen lama tanpa jejak.

## 1. Misi proyek

Membangun eksperimen yang dapat direproduksi untuk estimasi lebar retak beton (`MANwidth`, µm) menggunakan 501 nilai brightness profile (`x1`–`x501`) dari dataset krkCMd.

Urutan penelitian yang disepakati:
1. **Ide 1 — Benchmark model:** Linear Regression, Random Forest, Extra Trees, SVR, HistGradientBoosting, MLP, dan bila sesuai 1D-CNN.
2. **Ide 2 — Robustness:** uji sensitivitas terhadap brightness shift, contrast scaling, Gaussian noise, dan smoothing/blur pada data uji.
3. **Ide 4 — Data drift/fine-tuning:** hanya setelah hasil Ide 1–2 diperiksa dan memang ada indikasi perbedaan distribusi/performa antar-Series atau kelompok.

Jangan mulai Ide 4 otomatis. Buat laporan singkat yang menjelaskan bukti awal, risiko leakage, dan rancangan eksperimen sebelum implementasi.

## 2. Prinsip wajib

- **Reproducibility first:** semua eksperimen memiliki seed, konfigurasi, versi environment, log, dan output yang tersimpan.
- **No fabricated results:** jangan pernah mengarang angka, tabel, grafik, hasil training, sitasi, DOI, atau status download.
- **No plagiarism:** paper boleh direplikasi dengan atribusi; jangan menyalin teks paper untuk diklaim sebagai tulisan sendiri.
- **No data leakage:** `MANwidth` adalah target. `DLMwidth` dan `AEDwidth` adalah baseline pembanding, bukan fitur input model utama.
- Kolom metadata `No`, `Profile`, `Series`, `Image`, `Gridline`, `Stage` tidak masuk fitur utama secara default. Simpan untuk audit dan grouping.
- Baris bukan otomatis sampel independen. Beberapa profil dapat terkait gambar/lokasi/spesimen dan tahapan self-healing.
- Jangan memakai random row-wise split sebagai hasil utama.
- Fit scaler/preprocessor hanya pada data training.
- Robustness perturbations dilakukan pada salinan data test, bukan data training, dan label `MANwidth` dipertahankan hanya sebagai uji sensitivitas terkontrol.
- Jangan menyebut synthetic perturbation sebagai bukti ketahanan di lapangan. Laporkan sebagai stress test sintetis.
- Semua keputusan metodologis harus dapat ditelusuri di `docs/DECISIONS.md`.
- Jangan mengunduh dataset/paper dari sumber yang tidak jelas. Gunakan sumber resmi yang tercantum pada `docs/DATA_AND_PAPERS.md`.

## 3. Dataset dan schema yang diharapkan

Dataset utama: `krkCMd_table.csv`

Kolom yang diharapkan:
- Metadata: `No`, `Profile`, `Series`, `Image`, `Gridline`, `Stage`
- Input: `x1` sampai `x501` (intensitas brightness, umumnya 0–255)
- Target manual: `MANwidth` (µm)
- Baseline terdahulu: `DLMwidth`, `AEDwidth`

Jangan menganggap schema pasti benar. Notebook/script harus memeriksa kolom aktual, missing values, tipe data, rentang nilai, duplikasi, dan jumlah kategori. Jika ada perbedaan schema, berhenti dengan pesan yang jelas dan minta konfirmasi; jangan diam-diam mengubah definisi fitur.

## 4. Struktur folder

```text
krkCMd_research_starter/
├── AGENT.md
├── MASTER_PROMPT.md
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── configs/
│   └── baseline.yaml
├── data/
│   ├── raw/          # file asli; jangan diedit
│   ├── interim/      # hasil ekstraksi/validasi sementara
│   ├── processed/    # dataset siap eksperimen
│   └── external/     # data eksternal yang sah
├── notebooks/
│   └── 00_baseline_krkCMd.ipynb
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── evaluation/
├── scripts/
├── tests/
├── papers/           # PDF paper yang diunduh
├── references/       # bibliografi/DOI/metadata
├── docs/
│   ├── DATA_AND_PAPERS.md
│   ├── DECISIONS.md
│   ├── EXPERIMENT_LOG.md
│   └── RESEARCH_QUESTIONS.md
├── reports/
│   ├── figures/
│   ├── tables/
│   └── logs/
└── artifacts/
    ├── models/
    └── results/
```

## 5. Lokasi file input

Letakkan file berikut:
- `krkCMd_table.csv` → `data/raw/krkCMd_table.csv`
- `krkCMd_scripts.zip` → `data/raw/krkCMd_scripts.zip`
- `krkCMd_images.zip` → `data/raw/krkCMd_images.zip` (opsional untuk tahap awal; jangan diekstrak kecuali dibutuhkan)

Jangan rename file asli kecuali dicatat. Jangan mengubah CSV asli. Semua hasil turunan masuk ke `data/interim/` atau `data/processed/`.

## 6. Workflow agent setiap kali menerima tugas

1. Baca `AGENT.md`, `docs/DECISIONS.md`, `docs/EXPERIMENT_LOG.md`, `docs/RESEARCH_QUESTIONS.md`, dan konfigurasi terkait.
2. Periksa status folder/data yang tersedia. Jangan mengasumsikan file sudah ada.
3. Identifikasi apakah permintaan mengubah data, kode, metodologi, atau hanya dokumentasi.
4. Sebelum perubahan besar, tulis rencana singkat: file yang akan dibuat/diubah, alasan, risiko, dan cara validasi.
5. Implementasikan perubahan sekecil mungkin.
6. Jalankan pemeriksaan yang relevan (syntax, unit test, notebook smoke test, atau eksperimen kecil).
7. Laporkan file yang berubah, perintah yang dijalankan, hasil aktual, error yang belum selesai, dan langkah berikutnya.
8. Perbarui log/decision jika ada temuan atau keputusan baru.

## 7. Self-extendable protocol (wajib)

Dokumen ini adalah master instruction yang dapat berkembang. Ikuti aturan berikut:

### 7.1 Jangan menimpa sejarah
- Jangan menghapus keputusan lama dari `docs/DECISIONS.md`; tandai sebagai `SUPERSEDED` dan tambahkan keputusan baru.
- Jangan menghapus catatan eksperimen lama dari `docs/EXPERIMENT_LOG.md`.
- Jangan mengubah hasil numerik lama agar cocok dengan hipotesis baru.

### 7.2 Kapan memperluas AGENT.md
Tambahkan aturan ke `AGENT.md` hanya jika temuan/aturan:
- berlaku lintas banyak tugas, atau
- mencegah kesalahan berulang, atau
- mengubah definisi metodologi inti.

Detail satu eksperimen masuk ke `docs/EXPERIMENT_LOG.md`, bukan memenuhi AGENT.md.

### 7.3 Format catatan perubahan
Setiap perubahan penting pada dokumen induk harus ditambahkan ke bagian `## 12. Changelog` dengan:
- tanggal (YYYY-MM-DD),
- ringkasan,
- alasan/bukti,
- file terkait,
- dampak pada eksperimen terdahulu (jika ada).

### 7.4 Usulan perubahan oleh agent
Jika agent menemukan hal yang seharusnya mengubah instruksi induk:
1. Jangan langsung menghapus aturan lama.
2. Tulis usulan di `docs/AGENT_CHANGE_PROPOSALS.md`.
3. Jelaskan bukti dan konsekuensi.
4. Jika perubahan aman dan disetujui pengguna, terapkan dan catat di changelog.
5. Jika belum disetujui, pertahankan aturan lama dan tandai usulan sebagai `PENDING`.

### 7.5 Update mandiri setelah diskusi
Setelah setiap diskusi yang menghasilkan keputusan final, agent harus:
- memperbarui `docs/DECISIONS.md`,
- memperbarui `docs/RESEARCH_QUESTIONS.md` bila pertanyaan riset berubah,
- memperbarui `docs/EXPERIMENT_LOG.md` bila eksperimen/hasil berubah,
- memperbarui `AGENT.md` hanya bila prinsip umum berubah,
- menampilkan ringkasan perubahan kepada pengguna.

## 8. Rancangan eksperimen baseline

### 8.1 Target dan fitur
- `y = MANwidth`
- `X = x1 ... x501`
- `DLMwidth` dan `AEDwidth` hanya dihitung sebagai baseline eksternal pada baris test yang sama.
- Baris dengan target kosong/tidak valid harus dilaporkan dan ditangani eksplisit.

### 8.2 Group split
Default grouping awal yang telah diverifikasi: gabungan `Series + Image + Gridline`, tanpa `Stage`, agar lokasi yang sama lintas tahapan tidak tersebar antara train dan test.
- Verifikasi telah membuktikan kombinasi tersebut merepresentasikan unit pengukuran/lokasi fisik yang sama di mana setiap kelompok memiliki tepat 6 tahapan (Stage 1 sampai 6).
- Kolom di CSV terkonfirmasi bernama `Gridline` (bukan `Grid`).
- Simpan daftar group train/validation/test agar dapat direproduksi.
- Jika group count terlalu kecil atau group tidak seimbang, jangan memaksakan split; laporkan masalah dan usulkan alternatif.
- Lakukan pemeriksaan overlap group setelah split.

### 8.3 Model awal
Model CPU-friendly:
- DummyRegressor (baseline minimum)
- LinearRegression
- RandomForestRegressor
- ExtraTreesRegressor
- HistGradientBoostingRegressor
- SVR (dengan scaling)
- MLPRegressor (dengan scaling; optional jika runtime terlalu lama)

Jangan menambahkan banyak model hanya untuk memperbanyak tabel. Catat parameter dan seed. 1D-CNN merupakan tahap opsional terpisah, bukan syarat baseline pertama.

### 8.4 Metrics
Minimal:
- MAE (µm)
- RMSE (µm)
- R²
- Median Absolute Error (µm)
- Bias = mean(prediction - target), µm

Laporkan jumlah sampel test dan jumlah group test. Bandingkan model hanya pada subset test yang sama.

### 8.5 Robustness
Pada test set:
- brightness shift (mis. -20, +20 intensity levels),
- contrast scaling (mis. 0.8, 1.2 around profile mean),
- Gaussian noise (mis. sigma 5, 10),
- Gaussian smoothing (mis. sigma 1; jelaskan implementasinya).

Clip intensity ke [0,255]. Gunakan seed tetap. Tampilkan MAE dan perubahan relatif terhadap MAE pada test asli. Perturbasi adalah eksperimen sintetis terkontrol; jangan overclaim.

### 8.6 Ide 4 gate
Sebelum domain adaptation/fine-tuning:
- bandingkan distribusi target dan fitur antar-Series/group,
- ukur performa baseline per-Series jika test coverage memadai,
- periksa apakah ada shift yang relevan,
- rancang source→target split berbasis group,
- fine-tune hanya dengan subset group target (mis. 5%, 10%, 20%) dan test pada group target tersisa.
Jika tidak ada indikasi atau data tidak cukup, jangan jalankan Ide 4.

## 9. Output wajib setiap milestone

Milestone 0 — Setup:
- Python version, OS, CPU/GPU info, package versions
- data file presence and file size
- successful CSV read

Milestone 1 — Data reconnaissance:
- shape/schema, missing, duplicates, target stats
- category counts for Series/Image/Gridline/Stage
- group count and group-size distribution
- target distribution by Series and Stage
- sample brightness profiles plot

Milestone 2 — Benchmark:
- saved metrics CSV
- saved predictions CSV
- model config/parameters
- group split manifest
- comparison chart

Milestone 3 — Robustness:
- perturbation config
- robustness metrics CSV and plot
- clear synthetic-stress-test caveat

Milestone 4 — Ide 4 decision:
- evidence summary and go/no-go recommendation
- no automatic execution without user approval

## 10. Coding standards

- Python 3.11 recommended; Windows PowerShell commands must be provided where relevant.
- Use pathlib for paths; avoid hard-coded machine-specific paths.
- Use functions for reusable logic and keep notebooks readable.
- Add docstrings/type hints for reusable source modules.
- Use `random_state`/seed consistently.
- Avoid loading the 38.6 GB image archive for tabular profile experiments.
- Never commit raw data, large images, model binaries, secrets, or local `.venv`.
- Keep requirements pinned or bounded and update them deliberately.
- Add tests for parsing, feature selection, split leakage checks, and metrics when code becomes modular.

## 11. Definition of done

A milestone is done only when:
- code executes without hidden manual steps,
- outputs are saved in the designated folders,
- data split/leakage checks pass,
- actual results are reported with caveats,
- logs and decisions are updated,
- user receives clear next action.

## 12. Changelog

- 2026-11-23 — Schema correction and group validation: Kolom metadata diverifikasi dari CSV aktual bernama `Gridline` (bukan `Grid`). Group key `Series + Image + Gridline` tervalidasi 100% konsisten (3,183 kelompok, masing-masing tepat 6 observasi Stage 1–6). Dependency `pypdf` ditambahkan ke requirements.txt.
- 2026-11-20 — Initial master protocol created. Research sequence fixed as Ide 1 + Ide 2, with Ide 4 gated by initial evidence. Initial grouping proposal is Series+Image+Grid and must be validated against dataset documentation/scripts.
