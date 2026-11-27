# Laporan Hasil Run 12 — M04B: Penyelesaian Screening Ilmiah, Analisis Statistik Eksploratori & Seleksi Finalis

- **Run ID:** `M04B_20261127_164911_DESKTOP-CQB09OU`
- **Status Fase:** **PASS (23/23 kandidat screening `PASS`; `70.380` prediksi validasi terkonsolidasi; bootstrap eksploratori `B=10.000` selesai; 0 kebocoran test)**
- **Catatan Notebook:** Eksekusi otomatis `jupyter nbconvert` terblokir Windows Application Control pada `_zmq` (`M04B_NOTEBOOK_EXECUTION_LOG.txt`); seluruh 8 figur publikasi tetap berhasil dirender via `matplotlib` (`figures/*.png`).

---

## 1. Verifikasi Bukti M04A & Hasil Pemulihan M04B (`D-010A`, `D-010B`)

1. **Verifikasi 16-Poin Bukti M04A:** Seluruh `20 / 20` kandidat `PASS` M04A lolos seluruh 16 pemeriksaan (`61.200` baris validasi, `0` duplikat, `test_rows_exposed_to_worker=0`, selisih rekomputasi `0.0`).
2. **Pemulihan 3 Kandidat (`3 / 3 PASS`, 1 percobaan masing-masing, `suspend_detected=False`):**
   - `FM04` (`TabDPT`, `.venv-foundation` `cuda:0`, `7.200s` cap): **`PASS`** dalam **`1.862,94 dtk`** (~31 menit) — `MAE = 23,90 µm`, `RMSE = 40,65 µm`, `CCC = 0,9591`.
   - `SG02` (`ResNet-1D`, `.venv-signal-tf` CPU-only TF, `10.800s` cap): **`PASS`** dalam **`5.082,38 dtk`** (~84,7 menit) — `MAE = 56,42 µm`, `RMSE = 78,84 µm`, `CCC = 0,8999`.
   - `SG03` (`InceptionTime` `n_regressors=1` single-member, `.venv-signal-tf` CPU-only TF, `10.800s` cap): **`PASS`** dalam **`5.890,92 dtk`** (~98,2 menit) — `MAE = 75,03 µm`, `RMSE = 108,22 µm`, `CCC = 0,8418`.
3. **Total Kandidat Berhasil:** **`23 / 23`** kandidat screening target `PASS` (`70.380` baris prediksi).
4. **Status 32 Model Terdaftar:** `23` Scientific `PASS`, `2` `BLOCKED_LICENSE` (`FM01`, `FM02`), `2` `REFERENCE_PENDING_IMPL` (`RF03`, `RF04`), `5` `DESIGN_REQUIRED` (`HY01–HY05`), **`0` Approved untuk M05 HPO**.

---

## 2. Leaderboard Terkonsolidasi (`n=3.060` Validasi Protocol A, `D-010E`)

| Peringkat | Model | Raw MAE (µm) | 95% Boot CI MAE | Raw RMSE (µm) | Lin's CCC | Clipped MAE (µm) | ΔMAE vs `ML01` [95% CI] | Waktu (dtk) |
|---:|---|---:|---|---:|---:|---:|---|---:|
| 1 | `ML01` Extra Trees | **14,25** | `[10,95; 18,32]` | 28,94 | 0,9796 | 14,25 | — | 32,2 |
| 2 | `FM03` TabICLv2 | **14,39** | `[10,63; 19,08]` | 29,17 | 0,9794 | 14,38 | `+0,14 [-0,48; +0,88]` | 83,2 |
| 3 | `ML02` Random Forest | **14,56** | `[11,17; 18,81]` | 29,87 | 0,9783 | 14,56 | `+0,30 [+0,04; +0,62]` | 95,9 |
| 4 | `ML04` XGBoost | **14,74** | `[11,49; 18,81]` | 29,68 | 0,9786 | 14,62 | `+0,49 [+0,11; +0,88]` | 20,7 |
| 5 | `ML06` CatBoost | **14,98** | `[11,50; 19,36]` | 29,05 | 0,9796 | 14,86 | `+0,73 [+0,28; +1,25]` | 29,5 |
| 6 | `ML05` LightGBM | **15,00** | `[11,66; 19,19]` | 29,65 | 0,9787 | 14,86 | `+0,74 [+0,32; +1,15]` | 9,4 |
| 7 | `ML03` HGB | **15,24** | `[11,85; 19,44]` | 30,15 | 0,9779 | 15,16 | `+0,98 [+0,62; +1,34]` | 9,2 |
| 8 | `DL03` RealMLP | **16,66** | `[13,10; 21,05]` | 31,41 | 0,9762 | 16,66 | `+2,41 [+1,75; +3,12]` | 119,3 |
| 9 | `DL02` FT-Transformer | **16,73** | `[13,19; 21,36]` | 31,36 | 0,9768 | 16,26 | `+2,47 [+1,52; +3,53]` | 188,2 |
| 10 | `RF05` DLM retrained | **17,49** | `[13,84; 22,15]` | 33,68 | 0,9728 | 17,45 | `+3,24 [+1,99; +4,57]` | 22,9 |
| 11 | `SG06` MultiROCKET-HYDRA | **22,33** | `[19,66; 25,65]` | 33,46 | 0,9730 | 20,61 | `+8,08 [+6,87; +9,21]` | 347,9 |
| 12 | `DL05` TabM | **23,52** | `[19,25; 28,35]` | 41,36 | 0,9583 | 23,12 | `+9,26 [+7,65; +11,20]` | 24,0 |
| 13 | `FM04` TabDPT | **23,90** | `[19,95; 28,29]` | 40,65 | 0,9591 | 23,90 | `+9,65 [+8,13; +11,29]` | 1862,9 |
| 14–23 | `DL04` (`23,95`), `DL01` (`24,21`), `SG05` (`26,25`), `SG04` (`27,72`), `ML07` (`29,72`), `SG01` (`41,88`), `RF02` (`52,45`), `SG02` (`56,42`), `SG03` (`75,03`), `RF01` (`120,27`) | — | — | — | — | — | — | — |

**Pembanding Historis (Terpisah — Bukan Retraining Adil):** `DLMwidth` (`MAE=14,59 µm`, 95% CI `[11,26; 18,84]`, `RMSE=27,14 µm`, `CCC=0,9820`) dan `AEDwidth` (`MAE=33,21 µm`, `[27,57; 39,61]`, `RMSE=52,19 µm`, `CCC=0,9288`).

---

## 3. Temuan Statistik Eksploratori, Subgrup, Kelayakan & Usulan Finalis

- **Klaster Gambar Validasi:** `35` dari `36` grup `Series + Image` muncul pada partisi validasi (`3.060` baris); bootstrap `B=10.000` (`seed=42`) bersifat **eksploratori** (`D-010C`), bukan pembuktian konfirmatori.
- **Rezim Nol-Lebar (`n=796` / `26,01%`):** `DL03` (`8,55 µm` MAE, `0%` negatif) dan `DL02` (`9,58 µm` raw / `7,85 µm` clipped) sangat kuat di rezim nol-lebar, sedangkan `SG01` (`45,22 µm`) dan `RF02` (`61,66 µm`) kesulitan.
- **Audit Data Training Efektif:** Model neural early-stopping (`DL01`, `DL02`, `DL04`, `DL05`, `SG01`, `RF05`) berlatih pada `9.774` baris (`1.629` grup) dan memantau `2.442` baris (`407` grup); model lain memakai seluruh `12.216` baris.
- **Usulan Roster Finalis (`M04B_PROPOSED_FINALIST_ROSTERS.md`) & Skenario M05 (`M05_PROPOSED_BUDGET_SCENARIOS.csv`):**
  - **Compact:** 5 HPO (`ML01`, `ML04`, `ML06`, `FM03` inference-only, `DL03`) + 3 jangkar (`RF05`, `RF02`, `RF01`) -> ~1,5–2,5 jam.
  - **Balanced (Direkomendasikan):** 9 HPO (`ML01`, `ML02`, `ML04`, `ML05`, `ML06`, `FM03`, `DL03`, `DL02`, `SG06`) + 3 jangkar -> ~4–7 jam.
  - **Expanded:** 13 HPO (+ `ML03`, `DL05`, `DL04`, `SG04`) + 3 jangkar -> ~8–14 jam.
- **Keputusan Menunggu Persetujuan Peneliti (`M05_RESEARCHER_APPROVAL_REQUIRED.md`):** Pilihan roster (Compact/Balanced/Expanded), skema inner CV M05, kebijakan refit setelah early stopping, dan anggaran komputasi M05.

---

### TINDAKAN MANUAL PENELITI

1. **Instalasi Software:** Tidak diperlukan. Seluruh 8 environment `.venv*` tidak berubah.
2. **Eksekusi Notebook Manual:** **Diperlukan jika ingin file `.ipynb` ter-eksekusi**, karena `jupyter nbconvert` diblokir oleh kebijakan **Windows Application Control** pada file `_zmq` (`M04B_NOTEBOOK_EXECUTION_LOG.txt`). Jalankan manual di VS Code / Jupyter dengan:
   - **Path Notebook:** `c:\PROJECT\krkCMd_research_starter_v1\notebooks\02_M04B_screening_completion_analysis.ipynb`
   - **Kernel:** `krkcmd-research-newpc` (`.venv`)
   - **Lokasi HTML Export (jika diekspor manual):** `c:\PROJECT\krkCMd_research_starter_v1\reports\runs\M04B_20261127_164911_DESKTOP-CQB09OU\02_M04B_screening_completion_analysis.html`
   - *(Catatan: seluruh 8 figur `.png` sudah otomatis dirender dan tersimpan di `reports/runs/M04B_20261127_164911_DESKTOP-CQB09OU/figures/`).*
3. **Pengaturan Sleep Windows:** Pengaturan AC Sleep (`0x00000000` / Never) dan Hibernate (`0x00000000` / Never) tidak diubah oleh agen; tidak ada yang perlu dipulihkan.
4. **Akses Checkpoint / Lisensi:** Tidak ada tindakan lisensi wajib untuk M05 kecuali peneliti ingin membuka `FM01`/`FM02` (`TABPFN_TOKEN`).
5. **Pemeriksaan Git Aman:** Agen tidak menjalankan `git commit` atau `git push`. Dua file sementara `.keras` di root (`1795681367142376600.keras`, `1795684965468312200.keras`) dibiarkan utuh dan dikecualikan dari `M04B_review_package.zip`.
6. **File untuk Diunggah ke ChatGPT:**
   1. `c:\PROJECT\krkCMd_research_starter_v1\for_review\result_run_12_M04B.md`
   2. `c:\PROJECT\krkCMd_research_starter_v1\reports\runs\M04B_20261127_164911_DESKTOP-CQB09OU\M04B_review_package.zip`
