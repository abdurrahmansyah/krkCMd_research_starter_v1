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
