# Sebelum Eksekusi: Checklist Bahan dan File

## Sudah dimiliki menurut informasi pengguna
- [x] `krkCMd_table.csv` — taruh di `data/raw/krkCMd_table.csv`
- [x] `krkCMd_scripts.zip` — taruh di `data/raw/krkCMd_scripts.zip`
- [ ] `krkCMd_images.zip` — sedang diunduh; taruh di `data/raw/krkCMd_images.zip` setelah selesai (opsional tahap awal)

## Paper yang sebaiknya diunduh dan disimpan

Simpan PDF (jika akses legal tersedia) di folder `papers/`:
1. Paper metode utama 2024 — DOI `10.1016/j.conbuildmat.2024.135768`
   Nama file yang disarankan: `Jakubowski_Tomczak_2024_DLM_Crack_Width.pdf`
2. Data descriptor 2025 — DOI `10.1038/s41597-025-04485-z`
   Nama file: `Jakubowski_Tomczak_2025_krkCMd_Data_Descriptor.pdf`
3. Paper pendukung robustness/feature learning 2024 — DOI `10.1016/j.jobe.2024.111386`
   Nama file: `Su_et_al_2024_CNN_Crack_Geometric_Features.pdf`
4. Paper Carrasco 2021 yang sudah pernah dipakai pada proyek terdahulu — DOI `10.3390/s21227534` (opsional untuk konteks metode; bukan dataset krkCMd)
   Nama file: `Carrasco_et_al_2021_Image_Based_Crack_Width.pdf`

Jangan mengunduh ulang jika PDF yang sama sudah tersedia. Jangan mencari versi bajakan. Jika tidak bisa mengakses PDF, simpan DOI/URL dan tandai `PDF_NOT_AVAILABLE`.

## Software
- [ ] Python 3.11 64-bit
- [ ] Visual Studio Code (atau IDE lain)
- [ ] Extension Python dan Jupyter untuk VS Code
- [ ] Codex / Antigravity / coding agent yang akan digunakan (opsional; notebook bisa jalan tanpa agent)

## Tidak perlu untuk baseline pertama
- GPU/CUDA
- Mengunduh ulang dataset gambar jika CSV sudah tersedia
- Menginstal TensorFlow/PyTorch
- Mengunggah data privat ke layanan eksternal

## Verifikasi sebelum menjalankan
- [ ] File CSV berada di `data/raw/` dan ukurannya masuk akal (puluhan MB)
- [ ] ZIP scripts berada di `data/raw/`
- [ ] Python 3.11 aktif di virtual environment `.venv`
- [ ] `pip install -r requirements.txt` selesai
- [ ] Notebook kernel `Python (krkCMd Research)` terpilih
