# krkCMd Research Starter

Paket awal penelitian estimasi lebar retak beton dari brightness profile dataset krkCMd.

## Mulai dari sini

1. Baca `AGENT.md`.
2. Baca `docs/STEP_BY_STEP_INDONESIAN.md`.
3. Letakkan file dataset pada lokasi yang ditentukan.
4. Buat virtual environment.
5. Jalankan notebook `notebooks/00_baseline_krkCMd.ipynb`.
6. Jangan menjalankan Ide 4 sebelum audit Ide 1–2 selesai dan hasilnya dibahas.

## Lokasi dataset

- `data/raw/krkCMd_table.csv` (wajib)
- `data/raw/krkCMd_scripts.zip` (sangat disarankan)
- `data/raw/krkCMd_images.zip` (opsional untuk baseline tabular; besar)

Notebook menggunakan path relatif dari root proyek. Jalankan Jupyter dari root proyek atau buka notebook melalui VS Code dengan workspace root proyek.

## Windows PowerShell setup

```powershell
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name krkcmd-research --display-name "Python (krkCMd Research)"
code .
```

Jika PowerShell memblokir aktivasi, jalankan untuk sesi terminal saat ini:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Menjalankan notebook

```powershell
jupyter lab
```

Pilih kernel `Python (krkCMd Research)`. Pastikan notebook dijalankan dari project root.

## Catatan

- Baseline pertama menggunakan CPU; GPU tidak wajib.
- Jangan ekstrak `krkCMd_images.zip` untuk eksperimen CSV awal.
- Notebook memeriksa schema dan membuat audit awal. Group split yang dipakai masih harus dikonfirmasi terhadap dokumentasi/scripts.
- Hasil notebook adalah hasil eksperimen lokal Anda, bukan angka dari paper.

## Catatan Migrasi Workstation Baru (M01-R)

Pada workstation baru (`DESKTOP-CQB09OU`), environment baseline `.venv` telah dibangun ulang menggunakan **Python 3.11.9 (64-bit)** dengan pin versi historis yang terverifikasi pada `reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/requirements_baseline_new_pc.freeze.txt` (salinan `.venv` PC lama disimpan sebagai `.venv_old_pc_backup`).

- **Kernel Jupyter baru:** `krkcmd-research-newpc` (`Python (krkCMd Research - New PC)`)
  ```powershell
  .\.venv\Scripts\python.exe -m ipykernel install --user --name krkcmd-research-newpc --display-name "Python (krkCMd Research - New PC)"
  ```
- **Catatan `scripts/verify_env_and_notebook.py`:** Skrip verifikasi historis memeriksa nama kernel lama `krkcmd-research` secara hardcoded; pada workstation baru gunakan kernel `krkcmd-research-newpc` hingga pembaruan M01.1 disetujui.
- **Laporan migrasi & reproduksi:** Lihat `reports/runs/M01R_20261125_032229_DESKTOP-CQB09OU/M01_R_MIGRATION_REPORT.md`.
