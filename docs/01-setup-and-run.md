# 01 - Setup & Run

## Requirements

- Python 3.10+
- Package dari `requirements.txt`

## Install dependencies

```bash
pip install -r requirements.txt
```

## Menjalankan aplikasi

### Production mode (default)

```bash
python main.py
```

- Menggunakan database: `appdata.db`

### Development mode

```bash
python main.py --dev
```

- Menggunakan database: `dev_data.db`
- Menampilkan log: `[DEV] Development mode enabled`

## Inisialisasi database

Saat aplikasi start, `main.py` akan:

1. Membuka koneksi SQLite (`connect_db`).
2. Menjalankan script schema `sql/init.sql` (`init_db`).

## Output report

- CSV tersimpan ke folder: `assets/csv/`
- PDF tersimpan ke folder: `assets/pdf/`
