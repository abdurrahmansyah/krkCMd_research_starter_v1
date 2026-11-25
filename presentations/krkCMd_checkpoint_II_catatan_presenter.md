# Catatan Presenter (Pribadi)

Checkpoint II · 25 November 2026 · M02B

Gunakan sebagai panduan bicara, bukan teks yang wajib dibaca. Deck utama: tekan N atau Presenter untuk membuka jendela catatan terpisah. Jangan bagikan jendela catatan ke proyektor.

## 01. Dari baseline klasik menuju benchmark AI modern

Pembukaan (±45 detik). Saya meneliti cara komputer memperkirakan lebar retak beton. Bukan mencari retak dari foto utuh, tetapi membaca 501 angka kecerahan yang sudah diambil melintasi retak. Di checkpoint sebelumnya saya sudah menunjukkan baseline klasik. Hari ini saya akan menjelaskan kenapa penelitian diperluas, bagaimana menjaga perbandingan tetap adil, dan sejauh mana model baru sudah dapat dijalankan. Saya belum membawa klaim bahwa AI modern lebih akurat. Hasil baru saat ini adalah bukti kesiapan teknis, bukan hasil lomba akurasi. Analogi: kita sudah memeriksa mobil-mobil dapat menyala dan berjalan sebelum memasukkannya ke arena balap.

## 02. Baseline sudah direproduksi. Kandidat AI diperluas.

Jelaskan perbedaan angka: enam model sudah benar-benar belajar dari data krkCMd pada baseline; dua belas model tambahan baru diuji dengan data buatan yang ukurannya setara. Angka 32 adalah daftar kandidat, bukan jumlah model yang sudah berhasil dilatih. Sebanyak 18 kandidat memiliki bukti eksekusi pada skala aktual atau sintetis ekuivalen, tetapi belum semua layak untuk benchmark final. Tidak ada model tambahan yang disetujui untuk eksperimen ilmiah sampai protokol ditetapkan. Tujuan update ini adalah memperlihatkan progres yang nyata tanpa menyamakan dua jenis bukti.

## 03. Akurasi tinggi belum tentu tahan perubahan cahaya.

Bahasa sederhana: ada tiga pertanyaan. Pertama, siapa yang paling dekat dengan ukuran manusia? Kedua, siapa yang masih bisa membaca ketika gambarnya berubah terang atau gelap? Ketiga, apakah model masih bagus pada kelompok beton lain? Fokus saat ini dua pertanyaan pertama. Ide 4 hanya skrining, belum eksperimen adaptasi domain. Saya tidak ingin memakai model terbaru hanya karena sedang tren. Saya ingin mengetahui apakah cara belajar berbeda benar-benar memberi manfaat pada masalah pengukuran ini. Novelty tidak otomatis muncul dari jumlah model; perlu bukti gap literatur dan hasil yang dapat dipertanggungjawabkan.

## 04. Dari 501 angka menjadi satu ukuran.

Satu baris adalah satu pengukuran pada satu lokasi dan satu stage, bukan satu foto. Ada 501 angka dari kiri ke kanan melintasi retak. Angka 0 gelap, 255 terang. Komputer belajar hubungan pola gelap-terang dengan lebar yang diukur manusia, yaitu MANwidth dalam mikrometer. Misalnya 1000 mikrometer sama dengan 1 milimeter. Ada 510 kolom: 6 metadata, 501 fitur, satu target, dan dua nilai pembanding. Jangan memasukkan DLMwidth atau AEDwidth sebagai fitur karena itu akan membocorkan informasi pembanding. Metadata dipakai untuk pengelompokan dan analisis. Dataset diaudit: tidak ada missing value atau duplikat baris. DLMwidth dan AEDwidth adalah hasil metode sebelumnya, bukan label pelatihan kita.

## 05. Enam stage, satu lokasi pengamatan.

Klik S1 sampai S6. Ini profil asli dari lokasi yang sama, disalin dari presentasi checkpoint pertama. Garis yang turun menunjukkan bagian yang lebih gelap; bentuknya tidak selalu ideal karena permukaan beton juga memiliki tekstur. Setiap stage adalah pengamatan pada tahap penyembuhan retak yang berbeda. Lebar manual berubah, bahkan pada contoh ini mencapai nol di stage terakhir. Tidak harus selalu mengecil secara monoton. Jelaskan bahwa ini satu contoh, bukan bukti bahwa semua retak menutup. Karena enam pengamatan saling berkaitan, kita tidak boleh memasukkan beberapa stage dari lokasi yang sama ke train dan sisanya ke test.

## 06. Pisahkan lokasi, bukan sekadar baris.

Bayangkan satu murid mempunyai enam foto. Jika foto pertama dipakai untuk belajar dan foto kedua untuk ujian, komputer mungkin menghafal ciri murid tersebut. Karena itu kita mengelompokkan enam stage menggunakan Series, Image, dan Gridline, lalu membagi group secara utuh. Train 12.216 baris, validation 3.060, test 3.822. Ketiganya tidak berbagi group gridline. Validation untuk memilih model dan parameter, test untuk evaluasi. Namun, satu citra bisa menyumbang beberapa gridline, sehingga nol overlap group bukan berarti nol overlap citra. M03 perlu menetapkan analisis sensitivitas image-level dan cara menghindari pemilihan model berulang pada test yang sudah dilihat. Split historis tetap dipertahankan sebagai pembanding eksploratori.

## 07. Extra Trees kompetitif pada data normal.

Ini hasil baseline M00 pada data asli. MAE artinya rata-rata jarak prediksi dari jawaban manusia. Extra Trees memiliki MAE 14,31 mikrometer, artinya rata-rata meleset sekitar 0,014 milimeter. DLM existing 13,64, selisih sekitar 0,68 mikrometer. Kita belum boleh menyatakan setara atau lebih baik secara statistik. Random Forest sedikit lebih baik pada RMSE, yang lebih menghukum kesalahan besar. DLM dan AED pada grafik berasal dari kolom dataset, bukan model yang kita latih dengan split yang sama. Riwayat training DLM harus diperiksa sebelum membuat klaim fairness. Model baru seperti TabM atau XGBoost belum punya MAE aktual; jangan menaruh hasil sintetis di grafik ini.

## 08. Bagaimana jika profil menjadi lebih terang?

Pilih brightness shift lalu gerakkan slider. Bayangkan memotret retak yang sama dengan lampu lebih terang. Secara fisik lebar retaknya tidak berubah, tetapi angka kecerahannya berubah. Lalu pilih contrast scale dan geser ke bawah agar perbedaan antara gelap dan terang berkurang. Model bisa salah membaca perubahan warna sebagai perubahan ukuran. Demo ini hanya transformasi angka dengan clipping 0 sampai 255; tidak ada inferensi model langsung. Label MANwidth dianggap tetap. Gangguan sintetis merupakan simulasi terkontrol, bukan bukti ketahanan terhadap semua kondisi kamera di dunia nyata.

## 09. Akurat pada clean, sensitif pada kontras.

Pada Ide 2, Extra Trees dipilih berdasarkan MAE validation lalu dilatih ulang dengan train dan validation. Karena itu clean MAE 14,05 berbeda dari 14,31 pada Ide 1. Ketika kontras diperkecil ke 0,8, MAE naik menjadi 77,14 mikrometer, atau sekitar 5,49 kali. Ini seperti seseorang yang hanya pandai membaca tulisan dengan pencahayaan tertentu. Jika cahaya berubah, ia salah membaca. Brightness +20 juga membuat error naik besar. Smoothing ringan hampir tidak berdampak. Hasil ini hanya berlaku untuk Extra Trees dan gangguan yang telah diuji. Belum diketahui apakah CNN, boosting, atau foundation model akan lebih stabil. Inilah alasan utama memperluas Ide 2 dan merancang normalisasi, derivative, serta augmentation.

## 10. Hasil baseline bertahan setelah pindah workstation.

Reproduksibilitas artinya orang lain atau komputer lain dapat menjalankan prosedur yang sama dan memperoleh hasil yang konsisten. Saya pindah ke workstation baru dan membangun ulang Python 3.11.9 dengan versi pustaka historis. Notebook dijalankan otomatis dalam ruang terisolasi, jadi tidak perlu Run All secara manual. Enam model baseline menghasilkan metrik sama pada presisi yang ditampilkan. Empat prediksi persis dan dua memiliki selisih numerik sangat kecil. Waktu eksekusi berubah karena hardware; SVR bahkan sedikit lebih lambat. Ini bukti reproduksi komputasional, bukan bukti bahwa model akan bagus pada beton dari lokasi baru. Tidak perlu mengulang M00 untuk mengejar angka yang sudah sama.

## 11. Mengapa tidak berhenti pada Extra Trees?

Data kita berbentuk tabel, tetapi bukan tabel sembarang. Kolom x1 sampai x501 adalah posisi berurutan, seperti garis piksel dari kiri ke kanan. Tree model melihat fitur-fitur ini, sedangkan CNN dapat mencari pola lokal seperti sisi lembah gelap. Transformer mencoba menangkap hubungan antarf fitur, retrieval mencari contoh serupa, dan foundation model menggunakan pengetahuan hasil pretraining. Setiap pendekatan punya kelebihan dan kelemahan. Kita tidak tahu pemenangnya sebelum uji aktual. Saya tetap mempertahankan model klasik agar model modern harus membuktikan manfaatnya, bukan hanya lebih rumit. Evaluasi efisiensi juga penting untuk aplikasi praktis.

## 12. 32 kandidat, enam keluarga pendekatan.

Ini adalah katalog penelitian, bukan daftar juara. Klik filter L2C untuk memperlihatkan 12 model tambahan yang sudah lulus uji kapasitas sintetis. Klik recovery untuk tiga kandidat yang masih bermasalah. Klik M00 aktual untuk enam model awal yang sudah punya hasil penelitian. AED original dan DLM pretrained masih menunggu uji reproduksi/paritas. Lima model custom masih tahap desain. Empat foundation model direncanakan pada M02C. Jika dosen bertanya kenapa banyak, jawab bahwa registry membantu memilih secara transparan, bukan berarti seluruh 32 wajib masuk eksperimen akhir. Setiap kandidat mempunyai ID, versi, implementasi, environment, bukti runtime, dan status persetujuan. Jumlah final akan diputuskan melalui protokol M03.

## 13. Satu kontrak data, banyak jalur pemodelan.

Jelaskan gambar dari atas ke bawah. CSV dibaca, diperiksa, lalu dibagi berdasarkan lokasi. Registry adalah daftar identitas model dan konfigurasi. Semua model menerima informasi yang sama, yaitu 501 nilai brightness. Model tabular menerima tabel biasa. Model signal menerima bentuk satu channel dengan panjang 501, seperti gelombang; reshape tidak membuang nilai. Foundation model menerima contoh berlabel sebagai context dan query tanpa label. Semua harus mengembalikan satu prediksi lebar dalam mikrometer untuk satu observasi. Baru setelah itu kita menilai dengan metrik yang sama. Diagram ini merupakan arsitektur target; runner scientific benchmark dan foundation belum selesai. Jangan menganggap semua jalur sudah dieksekusi.

## 14. Enam environment terisolasi menjaga eksperimen lama.

Environment itu seperti kotak alat yang berbeda. Jika semua alat dicampur, versi NumPy yang dibutuhkan Numba mungkin bertabrakan dengan paket neural. Kita pisahkan agar paket baseline tetap sama. Registry memberi tahu worker model apa yang harus dijalankan. Worker menggunakan interpreter sesuai environment, dan watchdog mengawasi RAM, VRAM dan waktu. Hasil disimpan dalam CSV/JSON dengan run ID, bukan hanya tangkapan layar. Notebook digunakan untuk membaca hasil dan membuat grafik. Ini membuat penelitian lebih mudah direproduksi dan membantu agar kegagalan satu model tidak menghentikan seluruh proses. Enam environment sudah dibuat; foundation dan TabR masih rencana.

## 15. Lulus compatibility test ≠ menang benchmark.

Analogi: sebelum lomba lari, kita periksa apakah sepatu pas dan pelari bisa menyelesaikan jarak. L0 hanya memastikan model tersedia. L1 mencoba sedikit data buatan. L2 menambah ukuran sampai setara jumlah baris penelitian. PASS artinya model dapat menerima input, fit dan predict, menghasilkan angka finite dengan jumlah benar, dan tidak melewati batas sumber daya. Ini belum menyatakan model memahami retak beton. Kita sengaja menggunakan data buatan supaya tidak berulang kali melihat test aktual sebelum protokol dikunci. Konfigurasi uji juga diperkecil, jadi waktu fit tidak boleh dijadikan ranking kecepatan final. Pada M04 baru akan masuk data nyata setelah persetujuan M03.

## 16. GPU kini benar-benar terverifikasi.

Sebelumnya RAM sekitar 32 GiB dan VRAM 4 GiB. Sekarang tersedia hampir 128 GiB RAM dan GPU Quadro RTX 6000 dengan 24 GiB VRAM. GPU ini generasi Turing, bukan GPU terbaru. Kita sudah melakukan operasi tensor nyata, convolution, FP16 AMP dan attention; jadi tidak sekadar melihat nama GPU pada nvidia-smi. Namun, native BF16 atau kernel attention tertentu tidak otomatis tersedia. TensorFlow resmi pada Windows yang dipakai berjalan di CPU, dan HYDRA juga CPU meskipun memakai torch. Karena itu setiap model harus mencatat perangkat yang benar. Peningkatan hardware membuka peluang, tetapi tidak merupakan kontribusi ilmiah utama.

## 17. 4 dari 5 kandidat mencapai L2C.

XGBoost, LightGBM dan CatBoost adalah keluarga boosting. ROCKET adalah pendekatan yang berbeda: ia mengubah sinyal 501 titik menjadi banyak fitur melalui convolution acak, lalu regresor belajar dari fitur tersebut. Keempatnya lulus pada 12.216 profil buatan dan 3.822 prediksi. Angka pada tabel adalah durasi fit dan predict pada konfigurasi terbatas, bukan performa ilmiah. ROCKET lebih lama pada uji ini, tetapi kita belum boleh menyimpulkan bahwa model ini lebih buruk. MultiROCKET-HYDRA gagal import karena membutuhkan torch, sedangkan saat itu torch memang belum diizinkan untuk dipasang. Status gagal ini teknis, bukan kegagalan model memahami retak.

## 18. 8 dari 11 target mencapai L2C.

Pada M02B kita berhasil menjalankan lima model GPU yaitu MLP, FT-Transformer, RealMLP, TabM, dan Vanilla 1D-CNN. Tiga model sinyal dari aeon, yaitu ResNet, InceptionTime, dan LITETime berjalan pada CPU. Waktu fit yang terlihat berbeda karena jumlah epoch, ukuran arsitektur dan perangkat berbeda. Jangan menggunakan tabel ini untuk menyatakan TabM lebih cepat secara ilmiah dari InceptionTime. Tabel adalah bukti bahwa model dapat berjalan. Semua delapan model lulus L2C dengan bentuk data setara penelitian; belum ada hasil MAE aktual. Tiga target lain belum lulus seluruh tahap dan akan dibahas berikutnya.

## 19. Tiga kandidat belum lulus penuh, bukan dieliminasi.

TabR bukan tidak cocok, hanya integrasi repository belum selesai. HYDRA sudah berhasil import, belajar dan memprediksi sampai 4.096 sampel; pada 12.216 sampel proses dihentikan oleh batas 300 detik. Memori saat dihentikan sekitar 26.348 MiB atau 25,7 GiB, bukan bukti OOM. Rencana satu kali retry dengan timeout 1.800 detik tanpa menaikkan plafon memori. DLM retrained gagal karena loss menjadi NaN/inf pada L2A. Ini belum membuktikan penyebab tunggal; perlu mengecek normalisasi, satuan target, learning rate, dan gradient. Jangan mengubah metode asal sembarangan agar model lulus. Jika detail tidak tersedia, beri label architecture-inspired. Kita bisa lanjut ke eksperimen lain meski ada kandidat yang masih conditional.

## 20. Foundation model: belajar sebelumnya, membaca context sekarang.

Bayangkan model biasa adalah murid yang baru belajar dari buku kita, sedangkan foundation model adalah murid yang sudah sekolah sebelumnya. Saat ujian, ia membaca contoh berlabel dari training context untuk membantu menjawab soal baru. Mekanisme persisnya berbeda untuk setiap model. Kita akan menguji TabPFN-3.5, varian Fast, TabICLv2 dan TabDPT. Belum ada hasil aktual. Kita harus memastikan checkpoint yang benar, lisensi, kompatibilitas Turing dan kemampuan menangani semua 501 fitur. Tidak boleh membuang satu fitur hanya untuk membuat model lulus. Native retrieval atau preprocessing bawaan model harus dicatat. Kemungkinan data pretraining pernah melihat krkCMd belum diketahui; hal itu perlu dicatat sebagai keterbatasan, bukan diasumsikan bebas leakage.

## 21. Pisahkan informasi intensitas dari bentuk retak.

Kalau semua piksel menjadi lebih terang, bentuk lembah retak mungkin masih mirip. Raw stream mempertahankan angka asli, sedangkan shape stream mencoba membaca bentuk relatif. SNV mengurangi rata-rata tiap profil dan membaginya dengan simpangan baku; jika profil konstan perlu penanganan khusus supaya tidak membagi nol. Derivative membaca perubahan antar posisi, seperti tepi retak. Dua cabang kemudian digabung untuk memprediksi lebar. Ini masih hipotesis, tidak menjamin tahan terhadap clipping atau gangguan nonlinear. Model custom lain: SNV + CatBoost, derivative + Extra Trees, CNN + CatBoost dan stacking robust. Stacking harus menggunakan prediksi out-of-fold berbasis group. Nanti ablation study akan memeriksa apakah setiap komponen benar-benar memberi manfaat. Tidak ada hasil custom saat ini.

## 22. Menilai model dari lebih dari satu sisi.

MAE mudah dimengerti sebagai rata-rata selisih. RMSE memberi hukuman lebih besar pada kesalahan besar. Median AE membantu melihat error tipikal, bias menunjukkan kecenderungan terlalu besar atau kecil, dan R² menunjukkan variasi yang dapat dijelaskan. Robustness membandingkan seberapa besar error naik ketika kondisi berubah. Agreement memeriksa apakah prediksi bisa dianggap dekat secara praktis, bukan hanya berkorelasi. Confidence interval dan perbandingan berpasangan perlu memperhitungkan group karena enam stage saling terkait. MAPE bermasalah jika target nol. Efisiensi harus memisahkan waktu fit, predict dan loading checkpoint. Untuk final, kita perlu menutup peluang memilih model berdasarkan test berulang, misalnya menggunakan group-aware validation dan menetapkan evaluasi konfirmatori yang independen bila tersedia. Semua tambahan ini masih proposal M03.

## 23. DLM dan AED harus dibandingkan secara tepat.

Kalau membandingkan dua murid, kita perlu tahu apakah keduanya belajar dari materi yang sama. DLMwidth dan AEDwidth adalah hasil yang sudah ada di CSV. Kita dapat menghitung error terhadap MANwidth pada test set yang sama, tetapi belum tahu sepenuhnya hubungan training DLM asli dengan split kita. RF03 adalah port AED, belum terbukti sama dengan VBA asli. RF04 adalah DLM dengan bobot original. RF05 memakai arsitektur DLM tetapi belajar ulang; ini berbeda dari checkpoint asli. Kita perlu membedakan empat jenis bukti tersebut. Tidak boleh mengklaim berhasil mengalahkan metode asli secara adil sebelum provenance dan parity diperiksa. Analisis per-series dan image-level juga penting karena split gridline saja tidak menjamin citra independen.

## 24. Dari kesiapan teknis menuju temuan ilmiah.

Jelaskan bahwa baseline sudah ada dan berhasil direproduksi. Saat ini posisi kita tepat sebelum M02C, bukan setelah foundation model berhasil. M03 adalah titik persetujuan metodologi: metrik, split, fairness, kriteria seleksi dan anggaran. M04 adalah saat pertama model tambahan akan diuji dengan data aktual. HPO dilakukan dengan validation saja dan budget yang terdokumentasi. M06 membandingkan robustness, M07 mengembangkan custom model dan ablation, M08 mengevaluasi hasil final, M09 mengintegrasikan ke manuscript IMRAD Inggris dan Indonesia. Jika beberapa kandidat gagal teknis, tidak harus menunggu semua 32 untuk maju. Reference track bisa berjalan paralel. Saya ingin menerima masukan dosen tentang prioritas dan batas waktu penelitian.

## 25. Apa yang perlu diputuskan sebelum benchmark final?

Penutup. Tiga hal yang sudah kita ketahui: baseline kompetitif pada data normal, Extra Trees sangat sensitif terhadap perubahan kontras, dan infrastruktur model modern sudah jauh lebih siap. Dua belas model baru telah lulus kapasitas sintetis, tetapi belum memiliki hasil MAE ilmiah. Saya meminta masukan tentang apakah fokus tesis cukup pada benchmark dan robustness, apakah evaluasi image-level perlu diperkuat, dan model custom mana yang paling masuk akal. Jika ditanya apakah novelty sudah pasti, jawab belum: harus ditopang telaah pustaka dan hasil. Jika ditanya kapan hasil baru muncul, jawab setelah M02C dan persetujuan M03, bukan menjanjikan tanggal. Terima kasih.

## 26. Performa berbeda tajam antar-series.

Gunakan bila dosen bertanya mengenai generalisasi. Per-series MAE berbeda sampai 5,20 kali. Ini belum cross-series holdout karena data train masih mengandung series yang sama. Penyebabnya mungkin distribusi lebar, tekstur atau kualitas profil. Jangan langsung menyebut domain drift. Fokus Ide 1 dan 2 tetap utama; analisis ini menjadi subgroup analysis dan dasar mempertimbangkan holdout yang lebih ketat.

## 27. Template hasil akhir (seluruh nilai baru TBD).

Tabel ini sengaja belum diisi. Jika ditanya siapa pemenang dari model baru, jawab belum ada hasil akurasi aktual. Ini menunjukkan rencana format pelaporan, bukan hasil yang dibuat-buat. Pada final tabel diisi hanya dari artefak eksperimen yang sudah disetujui, dengan konfigurasi dan provenance yang jelas. Metrik efisiensi sintetis tidak dimasukkan ke tabel hasil ilmiah.

## 28. Jejak bukti untuk setiap klaim.

Sumber utama penelitian adalah paper DLM 2024 dan data descriptor 2025. Deck ini menggunakan bukti dari presentasi sebelumnya, laporan migrasi, serta ZIP M02A dan M02B. Grafik aktual baseline berasal dari hasil M00 yang direproduksi, sedangkan tabel kompatibilitas berasal dari data sintetis. Visual arsitektur baru adalah ilustrasi konsep penelitian. Tidak ada klaim bahwa model baru telah mengalahkan DLM. Tidak ada verifikasi ulang GitHub atau literature review baru dalam pembuatan deck ini. Bila dosen meminta daftar pustaka lengkap, jelaskan bahwa register referensi masih dikembangkan untuk manuscript.