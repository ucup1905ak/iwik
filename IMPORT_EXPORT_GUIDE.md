# Panduan Fitur Import & Export Excel Produk

## Deskripsi

Fitur ini memungkinkan Anda untuk mengimpor dan mengekspor data produk dalam format Excel (.xlsx). Fitur ini dirancang untuk memudahkan manajemen stok dan data produk di warung Anda.

## Tombol-Tombol yang Ditambahkan

Di halaman **Manajemen Produk**, Anda akan melihat tiga tombol di bagian atas:

- **📥 Import** - Untuk mengimpor produk dari file Excel
- **📤 Export** - Untuk mengekspor semua produk ke file Excel
- **+ Tambah Produk** - Tombol yang sudah ada sebelumnya

## Cara Menggunakan

### Export (Ekspor Data Produk)

1. Klik tombol **📤 Export** di halaman Manajemen Produk
2. Sistem akan secara otomatis membuat file Excel dengan semua data produk Anda
3. File akan disimpan di folder `assets/xlsx/` dengan nama `products_export_[tanggal_waktu].xlsx`
4. Folder tersebut akan terbuka otomatis di File Explorer
5. Anda akan melihat notifikasi sukses jika export berhasil

### Import (Impor Data Produk)

1. Klik tombol **📥 Import** di halaman Manajemen Produk
2. Pilih file Excel (.xlsx) yang ingin Anda impor
3. Sistem akan membaca file dan menampilkan jumlah produk yang akan diimpor
4. Klik **OK** untuk mengkonfirmasi impor
5. Produk akan ditambahkan ke database (SKU yang sudah ada akan di-skip)
6. Hasil impor akan ditampilkan dengan detail jumlah produk berhasil, di-skip, dan error

## Format File Excel

### Struktur Kolom

File Excel harus memiliki kolom-kolom berikut (secara berurutan):

| Kolom | Deskripsi   | Tipe   | Contoh              |
| ----- | ----------- | ------ | ------------------- |
| A     | No          | Number | 1, 2, 3             |
| B     | Nama Produk | Text   | Nasi Goreng Spesial |
| C     | Merek       | Text   | Warung Nusantara    |
| D     | SKU         | Text   | MKN-001             |
| E     | Kategori    | Text   | Makanan             |
| F     | Harga (Rp)  | Number | 25000               |
| G     | Stok        | Number | 10                  |

### Contoh Data

```
No  | Nama Produk          | Merek              | SKU      | Kategori | Harga (Rp) | Stok
----|----------------------|-------------------|----------|----------|------------|-----
1   | Nasi Goreng Spesial  | Warung Nusantara  | MKN-001  | Makanan  | 25000      | 10
2   | Es Teh Manis         | Fresh Drink       | MNM-001  | Minuman  | 5000       | 120
3   | Keripik Singkong     | SnackRasa         | SNK-001  | Snack    | 8000       | 50
```

## Template Import

Template file Excel tersedia di: `assets/xlsx/sample_import_template.xlsx`

Anda dapat menggunakan template ini sebagai dasar untuk membuat file import Anda sendiri.

## Validasi & Aturan

### Saat Import:

- **Nama Produk** (kolom B): Wajib diisi, tidak boleh kosong
- **SKU** (kolom D): Wajib diisi, tidak boleh kosong, harus unik (tidak ada duplikasi dengan produk yang sudah ada)
- **Harga** (kolom F): Harus berupa angka, tidak boleh negatif
- **Stok** (kolom G): Harus berupa angka bulat (integer), tidak boleh negatif
- **Kategori** (kolom E): Opsional, tetapi direkomendasikan untuk organisasi yang lebih baik

### Penanganan Error:

- Jika terjadi error pada baris tertentu, sistem akan melaporkannya dengan nomor baris dan deskripsi error
- SKU yang duplikat akan di-skip tanpa menghentikan proses import
- Hanya produk yang valid yang akan diimpor

## Tips & Trik

1. **Backup Data**: Selalu buat backup sebelum melakukan import data besar
2. **Validasi Data**: Periksa data Excel Anda sebelum import untuk menghindari error
3. **Export Dulu**: Jika unsure dengan format, lakukan export terlebih dahulu untuk melihat format yang tepat
4. **Kategori Standar**: Gunakan kategori yang konsisten: Makanan, Minuman, Snack, Sembako, Lainnya
5. **Update Stok**: Untuk update stok produk yang sudah ada, gunakan fitur Edit di halaman Manajemen Produk

## File yang Berhubungan

- **[utils/generate_xlsx.py](utils/generate_xlsx.py)** - Modul utama untuk import/export Excel
- **[gui/views/screens/product_page.py](gui/views/screens/product_page.py)** - Halaman Manajemen Produk dengan tombol import/export
- **[assets/xlsx/](assets/xlsx/)** - Folder penyimpanan file import/export

## Troubleshooting

### "File tidak ditemukan"

- Pastikan Anda memilih file yang benar saat import
- Periksa bahwa file masih ada di lokasi yang ditentukan

### "Format data tidak valid"

- Pastikan tipe data sesuai dengan kolom (angka untuk harga dan stok, teks untuk nama, dll)
- Periksa tidak ada spasi ekstra atau karakter khusus yang tidak perlu

### "SKU sudah ada"

- SKU yang sudah ada akan di-skip saat import
- Jika ingin update, gunakan fitur Edit di halaman Manajemen Produk

### "Tidak ada produk untuk diekspor"

- Pastikan Anda sudah menambahkan produk terlebih dahulu di halaman Manajemen Produk

## Pembaruan Mendatang

Fitur-fitur yang mungkin ditambahkan di masa depan:

- Import dengan merge/update untuk SKU yang sudah ada
- Template Excel yang dapat di-download langsung dari aplikasi
- Export ke format CSV
- Batch update stok
