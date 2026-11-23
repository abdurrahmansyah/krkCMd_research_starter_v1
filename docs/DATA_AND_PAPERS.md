# Data and Papers Register

## Dataset utama

### krkCMd_table.csv
- Repository: Zenodo record https://zenodo.org/records/14568863
- Data descriptor: Jakubowski & Tomczak (2025), *Scientific Data* 12, 165.
- DOI: https://doi.org/10.1038/s41597-025-04485-z
- Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC11775250/
- Gunakan CSV sebagai data utama eksperimen brightness-profile regression.
- Schema yang diharapkan: metadata + x1..x501 + MANwidth + DLMwidth + AEDwidth.
- Status lokal: pengguna menyatakan sudah mengunduh; perlu verifikasi file berada di `data/raw/`.

### krkCMd_scripts.zip
- Sumber: Zenodo record yang sama.
- Status lokal: pengguna menyatakan sudah mengunduh; perlu diekstrak/ditinjau setelah audit awal.
- Tujuan: memverifikasi definisi Profile/Series/Image/Gridline/Stage dan prosedur pembentukan data.

### krkCMd_images.zip
- Sumber: Zenodo record yang sama.
- Status lokal: sedang diunduh menurut pengguna.
- Ukuran yang pernah dilaporkan sekitar 38.6 GB.
- Tidak diperlukan untuk baseline tabular dari CSV. Simpan sebagai arsip; jangan ekstrak dulu.

## Paper inti

1. Jakubowski, K. & Tomczak, A. (2024). “Deep learning metasensor for crack-width assessment and self-healing evaluation in concrete.” *Construction and Building Materials*, 422, 135768. DOI: https://doi.org/10.1016/j.conbuildmat.2024.135768
   - Paper metode utama terkait DLM dan evaluasi self-healing.
   - Unduh PDF melalui akses institusi/penerbit yang sah bila tersedia.
2. Jakubowski, K. & Tomczak, A. (2025). “Dataset for developing deep learning models to assess crack width and self-healing progress in concrete.” *Scientific Data*, 12, 165. DOI: https://doi.org/10.1038/s41597-025-04485-z
   - Wajib dibaca untuk memahami dataset, variabel, provenance, dan validasi teknis.
3. Su et al. (2024). “Utilizing pretrained convolutional neural networks for crack detection and geometric feature recognition in concrete surface images.” *Journal of Building Engineering*. DOI: https://doi.org/10.1016/j.jobe.2024.111386
   - Referensi pendukung untuk ekstraksi fitur/regresi dan gangguan lingkungan; bukan dataset utama.

## Paper yang sudah dimiliki pengguna dari proyek terdahulu

- Carrasco et al. (2021), “Image-Based Automated Width Measurement of Surface Cracking,” *Sensors*. DOI: https://doi.org/10.3390/s21227534
- Repository: https://github.com/mlacarrasco/crack_width
- Catatan: proyek/data berbeda dari krkCMd. Simpan di `papers/` jika dipakai sebagai pembanding metodologis, bukan campur dataset.

## Aturan sitasi dan status

- Simpan PDF yang legal diakses di `papers/`.
- Simpan DOI, URL, status akses, tanggal unduh, dan catatan relevansi di `references/`.
- Jangan menandai paper “sudah dibaca” hanya karena metadata ditemukan.
- Jangan menebak hasil/arsitektur paper; verifikasi dari full text atau supplementary materials.
