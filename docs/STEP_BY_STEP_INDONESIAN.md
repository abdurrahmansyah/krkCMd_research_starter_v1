# Panduan dari Nol sampai Selesai (bahasa sederhana)

## Gambaran besarnya

Bayangkan kita punya banyak garis kecil yang merekam terang-gelap permukaan retak beton.
Setiap baris CSV berisi:
- 501 angka terang-gelap (`x1` sampai `x501`),
- satu angka lebar retak hasil pengukuran manusia (`MANwidth`),
- beberapa identitas/keterangan seperti seri, gambar, grid, dan tahap pengamatan.

Tugas komputer: belajar dari 501 angka tersebut untuk menebak lebar retak. Setelah itu kita ganggu angka terang-gelap sedikit untuk melihat apakah tebakan komputer berubah terlalu jauh.

## Tahap A — Siapkan bahan

1. Unduh/siapkan `krkCMd_table.csv`.
2. Unduh/siapkan `krkCMd_scripts.zip`.
3. Tunggu `krkCMd_images.zip` selesai jika ingin menyimpan arsip lengkap. **Tidak perlu menunggu untuk baseline awal.**
4. Buat folder proyek bernama `krkCMd_research_starter`.
5. Ekstrak paket starter ini ke folder tersebut.
6. Taruh file:
   - CSV ke `data/raw/krkCMd_table.csv`
   - ZIP scripts ke `data/raw/krkCMd_scripts.zip`
   - ZIP images (jika sudah selesai) ke `data/raw/krkCMd_images.zip`

Jangan mengedit file asli. Anggap `data/raw` sebagai lemari bahan mentah.

## Tahap B — Siapkan Python

1. Instal Python 3.11 64-bit dari situs resmi Python jika belum ada.
2. Buka folder proyek di VS Code.
3. Buka Terminal → New Terminal (pastikan terminal berada di folder proyek).
4. Jalankan perintah berikut satu per satu:

```powershell
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name krkcmd-research --display-name "Python (krkCMd Research)"
```

Jika muncul pesan execution policy, jalankan:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Kalau `py -3.11` tidak ditemukan, kemungkinan Python 3.11 belum terpasang atau Python Launcher belum tersedia.

## Tahap C — Jalankan pemeriksaan awal

1. Buka `notebooks/00_baseline_krkCMd.ipynb`.
2. Pilih kernel `Python (krkCMd Research)`.
3. Jalankan cell dari paling atas ke bawah (Run All).
4. Cell awal akan memastikan CSV bisa dibaca dan kolom-kolom penting tersedia.
5. Periksa laporan: jumlah baris, kolom, data kosong, duplikasi, distribusi target, kategori Series/Stage, dan contoh profile.

**Berhenti jika schema berbeda atau notebook memberi error.** Simpan pesan error dan diskusikan sebelum mengubah nama kolom secara asal.

## Tahap D — Pastikan pembagian data adil

Ini bagian penting. Kita tidak boleh memberi komputer foto/lokasi yang hampir sama saat belajar dan saat ujian. Kalau itu terjadi, nilainya terlihat bagus padahal komputer hanya menghafal.

Karena satu lokasi mungkin diamati pada beberapa Stage, pembagian harus berdasarkan kelompok lokasi, bukan mengacak baris satu per satu.

Notebook menyediakan rancangan group split awal dari `Series + Image + Grid`. Kita belum boleh menganggap ini benar sebelum memeriksa definisi kolom di data descriptor dan scripts ZIP. Jika unit lokasi ternyata berbeda, group key harus diperbaiki dan alasannya ditulis.

## Tahap E — Ide 1: bandingkan model

Model sederhana akan belajar dari `x1`–`x501` dan menebak `MANwidth`.

Kita bandingkan:
- tebakan rata-rata sederhana (Dummy),
- Linear Regression,
- Random Forest,
- Extra Trees,
- HistGradientBoosting,
- SVR.

Ukuran kesalahan:
- MAE: rata-rata selisih absolut; makin kecil makin baik.
- RMSE: memberi hukuman lebih besar pada kesalahan besar; makin kecil makin baik.
- R²: ukuran seberapa baik variasi target dijelaskan; makin mendekati 1 biasanya makin baik.
- Bias: apakah model cenderung menebak terlalu besar atau terlalu kecil.

Bandingkan juga `DLMwidth` dan `AEDwidth` sebagai baseline lama jika tersedia. Keduanya bukan input model.

## Tahap F — Ide 2: ganggu brightness profile

Kita ambil data test yang sama, lalu membuat salinannya:
- dibuat sedikit lebih terang/gelap,
- contrast dinaikkan/diturunkan,
- diberi noise acak,
- dibuat lebih halus (smoothing).

Lalu ukur apakah kesalahan prediksi naik. Ini hanya stress test buatan komputer, bukan bukti otomatis bahwa model tahan terhadap semua kondisi kamera/lapangan.

## Tahap G — Putuskan apakah Ide 4 layak

Setelah Ide 1 dan 2, lihat:
- Apakah performa berbeda jauh antar-Series?
- Apakah distribusi profile/target berbeda?
- Apakah ada bukti data drift?
- Apakah model yang dilatih pada satu kelompok gagal pada kelompok lain?

Jika iya, kita rancang fine-tuning/domain adaptation. Jika tidak, jangan memaksakan Ide 4.

## Tahap H — Akhir penelitian

1. Ulangi eksperimen final dengan konfigurasi yang sudah dibekukan.
2. Simpan semua hasil, grafik, parameter, dan split manifest.
3. Buat tabel hasil dan pembahasan.
4. Bandingkan dengan paper sumber secara jujur: dataset, split, target, metrik, dan protokol harus sebanding.
5. Tulis keterbatasan: ukuran dataset, korelasi antarprofil, kualitas label manual, synthetic perturbation, dan generalisasi ke beton/kamera lain.
6. Jangan menulis klaim “lebih baik dari paper” jika eksperimennya tidak apple-to-apple.

## Yang harus dikirim ke agent AI

Buka folder proyek, lalu berikan isi `MASTER_PROMPT.md`. Agent diminta memulai dari audit/setup saja, bukan langsung training besar-besaran. Periksa hasil audit bersama sebelum memberi izin eksperimen.
