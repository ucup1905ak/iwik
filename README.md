# IWIK - Store Management Desktop App

IWIK is a Python desktop application for managing store operational data:

- Cashiers
- Customers
- Products
- Sales transactions
- Sales details
- Sales report export (CSV and PDF)

The app uses:

- Tkinter for GUI
- SQLite for local database
- ReportLab for PDF report generation

## Features

- CRUD-style management for master data (cashier, customer, product)
- Sales input page with multi-item detail
- Built-in reports page
- Export report to CSV and PDF
- Environment mode via CLI flag:
  - `--dev` uses `dev_data.db`
  - default (production) uses `appdata.db`

## Project Structure

- `main.py` - application entry point
- `api/` - database access and CRUD functions
- `gui/` - Tkinter pages and main app window
- `sql/` - database schema scripts
- `utils/` - export helpers (CSV/PDF)
- `assets/` - generated output files
- `docs/` - detailed technical documentation

## Quick Start

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Run application

Production mode:

```bash
python main.py
```

Development mode:

```bash
python main.py --dev
```

## Database Behavior

On startup, the app will:

1. Connect to the selected SQLite database file.
2. Run initialization SQL from `sql/init.sql`.

Database file selection:

- Production: `appdata.db`
- Development: `dev_data.db`

## Export Output

- CSV files are generated in `assets/csv/`
- PDF files are generated in `assets/pdf/`

## Detailed Documentation

See documents in `docs/`:

- `docs/01-setup-and-run.md`
- `docs/02-database-schema.md`
- `docs/03-api-reference.md`
- `docs/04-gui-flow.md`

## Requirements

From `requirements.txt`:

- `SQLAlchemy>=2.0`
- `reportlab>=3.6.0`

> Note: current database layer is implemented with Python `sqlite3` module.
