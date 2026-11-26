# Ringkasan Eksekutif Milestone M03 (Bahasa Indonesia)

- **Run ID:** `M03_20261126_132016_DESKTOP-CQB09OU`
- **Workstation:** `DESKTOP-CQB09OU` (Intel Core i9-10900KF, 127.92 GB RAM, NVIDIA Quadro RTX 6000 24 GB VRAM)
- **Status:** **SELESAI (PROPOSED EVALUATION PROTOCOL — BELUM ADA TRAINING DATA ASLI `krkCMd`)**

---

## 1. Pencapaian Utama M03

1. **Penutupan Kesiapan Foundation Model (Sintetis L2C Penuh):**
   - **`FM03` (`TabICLv2`)**: Dengan parameter `offload_mode="cpu"`, `batch_size=1`, `use_fa3=False`, berhasil lulus uji skala penuh **L2C (`12.216 -> 3.822`) dalam `52,719 detik`** (reservasi CUDA puncak `18.418 MiB` / `18,0 GiB`, di bawah batas `20 GiB`).
   - **`FM04` (`TabDPT`)**: Lulus uji konsistensi batch (`max_abs_diff = 3.05e-05`) dan berhasil lulus **L2C (`12.216 -> 3.822`) dalam `2.361,703 detik` (~39,4 menit)** (reservasi CUDA puncak `10.864 MiB`).
   - **`FM01` & `FM02` (`TabPFN-3.5` & `Fast`)**: Tetap berstatus **`BLOCKED_LICENSE`** karena `TABPFN_TOKEN` tidak tersedia; agen tidak menerima lisensi secara otomatis.

2. **Rekonsiliasi Kesiapan 32 Kandidat Model (`0 APPROVED`):**
   - **6** model baseline historis M00 (`ML01`, `ML02`, `ML03`, `ML07`, `RF01`, `RF02`)
   - **17** model tambahan lulus uji kapasitas sintetis L2C (`ML04–ML06`, `DL01–DL05`, `FM03`, `FM04`, `SG01–SG06`, `RF05`) -> Total **23 model siap/eligible untuk M04**.
   - **2** `BLOCKED_LICENSE` (`FM01`, `FM02`).
   - **2** referensi menunggu implementasi eksak (`RF03` port VBA `k=6`, `RF04` port `krknet.mat` PyTorch).
   - **5** arsitektur kustom `DESIGN_REQUIRED` (`HY01–HY05`).
   - **0** model berstatus `APPROVED` — seluruh 32 model menunggu persetujuan peneliti untuk M04.

3. **Audit Dataset & Manifest Split Tanpa Kebocoran Spasial:**
   - Dataset `krkCMd_table.csv`: `19.098` baris, `501` fitur profil intensitas, `3.183` grup gridline (`k=6`), `36` grup `Series + Image` (`60`–`924` baris/grup, median `513`).
   - Ditemukan **`4.900` observasi lebar retak nol (`MANwidth == 0.0`, `25,66%`)** sehingga metrik `MAPE` global **dilarang** sebagai metrik utama dan digantikan oleh `RMSE`, `MAE`, `R²`, serta metrik terstratifikasi (`zero_width_mae`, `positive_width_rmse`, `positive_width_mape`).
   - Dihasilkan manifest split baru tanpa kebocoran antar-gambar (`max_folds_per_image_group = 1`): **Protocol B 3-fold** (utama, keempat Series hadir di tiap fold), **Protocol B 5-fold** (sensitivitas, dengan catatan `CMd_0.28_20mths` hanya punya 4 grup gambar), dan **Protocol C LOSO** (4-fold Leave-One-Series-Out untuk generalisasi antar-seri).

4. **Perbaikan Infrastruktur, Modul Evaluasi & Unit Test:**
   - Perbaikan watchdog (`scripts/resource_policy.py`) dengan deteksi sleep/suspend sistem (`suspend_detected`, `max_poll_gap_sec`, timeout `nvidia-smi`) serta investigasi anomali `48.477,078 detik` di M02C (`WATCHDOG_ANOMALY_INVESTIGATION_M03.md`).
   - Implementasi modul baru: `src/evaluation/metrics.py`, `src/features/perturbations.py` (7 famili perturbasi teruji), dan `src/evaluation/experiment_runner.py` (dengan pengaman `authorize_real_data_training=True`).
   - Seluruh **37 unit test** di `tests/` lulus (`OK`).

5. **Protokol Ilmiah, Referensi, & Analisis Kesenjangan Literatur:**
   - Disusun lengkap dokumen protokol penelitian (`M03_RESEARCH_QUESTIONS.md`, `M03_METRIC_REGISTER.yaml`, `M03_PERTURBATION_REGISTER.yaml`, `M03_SPLIT_PROTOCOL.md`, `M03_STATISTICAL_ANALYSIS_PLAN.md`, `M03_ROBUSTNESS_PROTOCOL.md`, `M03_HPO_BUDGET_PLAN.md`, `M03_REFERENCE_REPRODUCTION_PROTOCOL.md`, `M03_DLM_AED_FAIRNESS_REVIEW.md`, `M03_LITERATURE_EVIDENCE_MATRIX.csv`, `M03_NOVELTY_GAP_ANALYSIS.md`, `M03_EVALUATION_PROTOCOL.md`, `M04_EXECUTION_PLAN.md`).
   - Seluruh 8 environment `.venv*` dan file terproteksi diverifikasi tidak berubah (`before_after_integrity_M03.json`).

---

## 2. Keputusan yang Membutuhkan Persetujuan Peneliti Sebelum M04

1. Persetujuan menggunakan **Protocol B 3-fold (`Series + Image`)** sebagai CV utama, didampingi **Protocol A** (kontinuitas M00), **Protocol B 5-fold** (sensitivitas), dan **Protocol C** (LOSO).
2. Persetujuan daftar **23 model eligible** (serta apakah `FM04` dibatasi ke Protocol A / Protocol B 3-fold karena waktu inferensi ~39,4 menit per split).
3. Keputusan apakah port eksak **`RF03` (`CrackWidthAED_VBA.txt` `k=6`)** dan **`RF04` (`krknet.mat` PyTorch)** atau token **`FM01`/`FM02` (`TABPFN_TOKEN`)** akan diaktifkan sebelum M04 dimulai.
