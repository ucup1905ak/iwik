# 02 - Database Schema

Schema utama dibuat dari `sql/init.sql`.

## Tabel

### Cashier

- `ID` (PK)
- `FirstName` (TEXT, required)
- `LastName` (TEXT, required)
- `Salary` (REAL)

### Customer

- `ID` (PK)
- `Name` (TEXT, required)
- `Phone` (TEXT)

### Product

- `ID` (PK)
- `Name` (TEXT, required)
- `Brand` (TEXT)
- `Stock` (INTEGER, default 0)
- `Price` (REAL, required)

### Sales

- `ID` (PK)
- `CustomerID` (FK -> Customer.ID, nullable)
- `CashierID` (FK -> Cashier.ID, required)
- `Time` (TEXT, required)
- `Payment` (TEXT)
- `PaidAmount` (REAL)

### SalesDetail

- `ID` (PK)
- `SalesID` (FK -> Sales.ID, required, ON DELETE CASCADE)
- `ProductID` (FK -> Product.ID, required)
- `Quantity` (INTEGER, required)
- `Discount` (REAL, default 0)

## Catatan Relasi

- Satu record `Sales` dapat memiliki banyak `SalesDetail`.
- Jika `Sales` dihapus, semua `SalesDetail` terkait ikut terhapus (cascade).
