# IWIK (Warung+) - Store Management Desktop App

IWIK (codenamed Warung+) is a Python desktop application for managing store operational data:

- Authentication & Role Management (Admin/Cashier)
- Suppliers & Purchases
- Customers
- Products & Inventory
- Sales transactions & details
- Reports & Receivables
- Data export (CSV, PDF, and XLSX)

The app uses:

- **PyQt6** for a modern, responsive GUI
- **SQLite3** for the local database
- **ReportLab** for PDF report generation
- **OpenPyXL** for Excel report generation

## Features

- Secure login and user selection system
- CRUD-style management for master data (cashiers, customers, products, suppliers, purchases)
- Complete POS (Point of Sale) sales interface with multi-item cart management
- Built-in business intelligence reports and charts
- Export capabilities to CSV, PDF, and Excel formats

## Project Structure

- `main.py` - Application entry point
- `controllers/` - Backend business logic and CRUD wrappers for data models (using `NamedTuple`)
- `database/` - SQLite connection manager and SQL initialization scripts (`appdata.db`)
- `gui/` - Contains all PyQt6 views, standardized components, and screens
- `utils/` - Helpers for file exports (CSV/PDF/XLSX) and sample data generation
- `assets/` - Storage for generated output files and images
- `docs/` - System documentation and feature guides

## Quick Start

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Run application

```bash
python main.py
```

## Database Behavior

On startup, the app will:

1. Connect to the SQLite database file at `database/appdata.db`.
2. Run the initialization SQL script from `database/sql/init.sql` if the schema does not exist yet.

## Export Output

- CSV files are generated in `assets/csv/`
- PDF files are generated in `assets/pdf/`
- Excel files are generated in `assets/xlsx/`
- Images are managed under `assets/image/`

## Detailed Documentation

See documents in `docs/`:

- [docs/01-features-overview.md](docs/01-features-overview.md) - High-level functional breakdown
- [docs/04-gui-flow.md](docs/04-gui-flow.md) - Visual navigation and interaction mapping
- [docs/05-database-controllers.md](docs/05-database-controllers.md) - Database schema mapping and backend logic APIs

## Requirements

From `requirements.txt`:

- `PyQt6`
- `reportlab>=3.6.0`
- `openpyxl>=3.10.0`
- `Pillow>=9.0.0`
- `SQLAlchemy>=2.0` (Optional/Legacy compatibility)

> Note: The active database manager currently interfaces directly with the Python `sqlite3` module.
