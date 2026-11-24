# Prompt untuk Antigravity / Codex: ekspor bukti run aktual (read-only)
Baca AGENT.md, docs/DECISIONS.md, notebook aktual dan HTML yang sudah dieksekusi. Jangan training ulang, mengubah split/model/hyperparameter, atau mengubah notebook. Jangan commit/push data mentah atau PDF. Laporkan git SHA, Python, run ID, waktu dan status eksekusi cell. Baca artefak hasil run yang sama, jangan mencampur run. Jika tidak ada file, catat missing, jangan membuat angka.

Periksa `reports/tables/group_split_manifest.csv` dengan pandas: kolom `source_row_id`, `group_id`, `split`; seluruh ID baris unik, group tidak tersebar antarpartisi, ukuran aktual train/validation/test, jumlah group, tiga irisan pasangan, total cakupan dibanding CSV, dan setiap group berisi Stage 1–6 tepat satu kali setelah join ke CSV menggunakan source_row_id. Catat apakah group key Series + Image + Gridline digunakan. Periksa juga jumlah Series/Image yang tersebar antarpartisi, sebagai keterbatasan (bukan otomatis kegagalan D-003). Jangan mengubah data.

Ekspor dalam satu ZIP khusus untuk review (tanpa raw CSV, PDF, model biner, atau arsip gambar):
- notebooks/00_baseline_krkCMd.html dan .ipynb (jika tersedia)
- configs/baseline.yaml, docs/DECISIONS.md, docs/EXPERIMENT_LOG.md
- reports/tables/group_split_manifest.csv, benchmark_metrics.csv, existing_baseline_metrics.csv, robustness_metrics.csv, test_per_series_metrics.csv, comprehensive_audit.json (jika ada)
- reports/logs/baseline_run_summary.json, artifacts/results/benchmark_predictions.csv (jika ada)
- ringkasan verifikasi manifest, git status, commit SHA dan daftar artefak yang hilang.

Jangan mengklaim Ide 4 selesai hanya karena ada tabel per-series. Jika run berhenti, laporkan cell terakhir dan error apa adanya. Berhenti setelah ekspor dan laporan.
