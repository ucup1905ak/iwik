# 04 - GUI Flow

## Halaman utama (`gui/app.py`)

Aplikasi memiliki tab:

1. **Customers**
   - List data
   - Add customer
   - Delete customer
2. **Products**
   - List data
   - Add product
   - Delete product
3. **Cashiers**
   - List data
   - Add cashier
   - Delete cashier
4. **Input Penjualan**
   - Form sales header + multi item detail
5. **Laporan & Ekspor**
   - Tampilkan data sales
   - Export CSV/PDF

## Input Penjualan (`gui/sales_page.py`)

Alur simpan transaksi:

1. Input header sales: customer, cashier, waktu, metode bayar, paid amount.
2. Tambah 1+ baris detail item (product, quantity, discount).
3. Klik **Simpan Penjualan**.
4. Sistem membuat record sales (`create_sale_return_id`).
5. Sistem menyimpan semua detail (`create_sales_detail`).
6. Form dibersihkan dan riwayat detail di-refresh.

## Export

- CSV menggunakan `utils/export_csv.py`
- PDF menggunakan `utils/generate_pdf.py`
