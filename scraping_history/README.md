# Scraping Historical Data

Folder ini berisikan kodingan yang digunakan untuk melakukan scraping pada data berita yang sudah lama. Data berita yang diambil berasal dari [bisnis.com](http://bisnis.com/) kategori Market & Saham dan [detik finance](https://finance.detik.com/). Data yang diambil dari tahun 2004. Selain melakukan scraping data berita, dilakukan juga scraping data harga saham di [Yahoo Finance](https://finance.yahoo.com/)

### Tools yang Digunakan

Bahasa peprogramman yang digunakan adalah `Python 3.8.5` dengan library utama untuk melakukan scraping adalah `BeautifulSoup`. Selain itu digunakan juga beberapa library tambahan seperti `pandas`, `json`, `os` dan lain sebagainya untuk melakukan preprocessing data hasil scraping. 

### File Data dan Kodingan

Terdapat 4 file kodingan utama yang ada pada folder ini

1. `Scraping_Bisnis.ipynb`, berisikan kodingan untuk melakukan scraping data artikel pada [bisnis.com](http://bisnis.com/) kategori Market dan Saham
2. `Scraping_Detik.ipynb`, berisikan kodingan untuk melakukan scraping data artikel pada [detik finance](https://finance.detik.com/)
3. `Scraping_Harga_Saham.ipynb`, berisikan kodingan untuk melakukan scraping harga saham di [Yahoo Finance](https://finance.yahoo.com/)
4. `Preprocessing.ipynb`, berisikan kodingan untuk melakukan preprocessing data artikel hasil scraping sehingga siap untuk digunakan pada analisis selanjutnya

Selain file kodingan terdapat juga beberapa file yang ada pada folder `data`.
- `all_saham.csv`, list semua saham yang ada di Bursa Efek Indonesia (BEI) pada Desember 2021, datanya diambil secara manual diwebsite BEI
- `daftar_saham.csv`, hasil preprocessing dari file `all_saham.csv`
- `related_to_saham_summary`, file yang berisi jumlah artikel untuk setipa saham/perusahaan.
- `stop_words_binsis.xlsx`, file yang berisi stop words atau kata/kalimat yang tidak memiliki makna apapun yang sering muncul pada arikel hasil saham dari bisnis.com

Selain itu pada folder `data` terdapat beberapa folder lagi yang mana kegunaan dari folder tersebut akan dijelaskan pada section selanjutnya.


### Alur Pengerjaan

*Disclaimer*
> Alur dari programnya tidak tersusun dengan rapi sehingga banyak kemungkinan terjadi error ketika menjalankannya. Folder `data` juga hanya berisi contoh dari hasil scraping yang telah dilakukan. Data hasil scrapingnya sudah dihapus karena ukurannya yang lumayan besar

Tahapan pertama untuk mengumpulkan data berita adaka melakukan scraping pada judul berita. Hasil scraping judul tersebut akan disimpan dalam format `json` pada folder `/data/json_bisnis_finance/`, `/data/json_bisnis_market/` dan `/data/json_detik_finance/`. Dalam satu file terdiri dari data selama 150 hari, ini dikarenakan untuk menghindari hal yang tidak diinginkan, selama proses scraping akan dilakukan penyimpanan hasil scraping untuk setiap 150 hari.

Setelah seluruh judul dikumpulkan maka masuk ke proses selanjutnya yaitu melakukan scraping isi artikelnya. Hasilnya akan disimpan pada folder `/data/isi_berita_bisnis/` dan `/data/isi_berita_detik/`. Satu file terdiri dari data untuk satu hari dan disimpan dalam bentuk `json`. Hal ini dilakukan agar mudah mengidentifikasi proses scraping sudah berjalan sampai tanggal berapa sehingga ketika terjadi kegagalan tidak perlu mengulang dari awal

Setelah seluruh isi artikel selesai di scraping maka dilakukan tahap preprocessing yang ada pada file `Preprocessing.ipynb`. Beberapa hal yang dilakukan

1. Menggabungkan data yang masih dalam bentuk file harian menjadi satu file yang memuat seluruh data secara keseluruhan
2. Menghapus kata/kalimat yang tidak perlu. Misalnya kalimat-kalimat iklan diakhir artikel. Untuk mengidentifikasi kata/kalimat tidak perlu tersebut dilakukan secara manual dengan mengidentifikasi beberapa artikel
3. Mengidentifikasi artikel yang membahas saham/perusahaan pemilik saham
4. Menyiapkan format data yang akan digunakan untuk proses selanjutnya. Dalam hal ini akan ada 5 file utama
    - `article_norelated_to_saham`, file yang berisi seluruh artikel yang tidak membahas tentang saham/perusahaan terkait.
    - `article_related_to_saham`, file yang berisi seluruh artikel yang membahas saham/perusahaan terkait
    - `table_article.json`, file yang berisi seluruh artikel yang akan digunakan pada tahap selanjutnya. Artikel yang ada pada file ini hanyalah artikel yang membahas 4 saham yang akan diteliti yaitu artikel yang berkaitan dengan bank BRI, BNI, BCA, dan Mandiri. Bisa dibilang file ini adalah subset dari file `article_related_to_saham`
    - `table_saham.json`, file ini berisi list saham yang akan digunakan pada penelitian.
    - `table_article_saham.json`, file yang berisikan tabel hasil many to many relationship antara article dan saham. File ini berisi 2 kolom utama `saham_id` dan `article_id`


Setelah proses scraping dan penyiapan data selesai maka analisis selanjutnya tidak dilakukan di folder ini. Sehingga seluruh data scraping atau hasil pengolahannya telah dihapus ataupun dipindahkan ke folder yang lain.