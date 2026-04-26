# IWIK Documentation

Dokumentasi ini menjelaskan cara menjalankan aplikasi, struktur modul, database, dan alur input penjualan.

## Daftar Dokumen

- [01 - Setup & Run](01-setup-and-run.md)
- [02 - Database Schema](02-database-schema.md)
- [03 - API Reference](03-api-reference.md)
- [04 - GUI Flow](04-gui-flow.md)

## Ringkasan Cepat

- Aplikasi desktop berbasis Tkinter.
- Database menggunakan SQLite.
- Mode environment:
  - Development: `dev_data.db`
  - Production: `appdata.db`
- Entry point: `main.py` dengan flag `--dev`.
