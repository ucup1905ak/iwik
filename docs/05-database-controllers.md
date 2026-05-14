# Database Schema and Controllers

## Overview
The application uses **SQLite3** for data persistence. Operations are managed via custom controller classes executing raw parameterized SQL queries, abstracting data models into Python `NamedTuple` objects.

## Core Schema & Linked Controllers

### 1. **Users**
- Controller: `UserController` (`user.py`)
- Represents system operators (Cashier, Admin). Features authentication via hashed PINs/Passwords.

### 2. **Customers**
- Controller: `CustomerController` (`customer.py`)
- Standard customer profiles mapped to sales or accounts receivable.

### 3. **Products & Inventory**
- Controller: `ProductController` (`product.py`)
- Tracks items for sale. Uses barcode mapping, calculates stock levels dynamically based on Sales and Purchase events.

### 4. **Suppliers & Purchases** (Supply Chain)
- Controller: `SupplierController` (`supplier.py`), `PurchaseController` (`purchase.py`), `PurchaseDetailController` (`purchase_detail.py`)
- Tracks restock shipments from Suppliers. Inserting a PurchaseDetail record automatically triggers stock count increments for the associated Product.

### 5. **Sales & Point of Sale**
- Controller: `SalesController` (`sales.py`), `SalesDetailController` (`sales_detail.py`)
- Core POS record keeping. Sales contain a master row with total price, and SalesDetail links multiple products sold in that transaction, consequently decrementing the product stock.

### 6. **Cashiers** (Legacy)
- Controller: `CashierController` (`cashier.py`)
- *Note: Mostly migrated into the unified Users table in modern application states.*

## Data Access Pattern
All controllers adhere to standard class methods, leveraging the `DatabaseManager` for obtaining thread-safe cursor objects:

```python
class SupplierController:
    @staticmethod
    def get_all():
        with db.get_connection() as conn:
            # Executes SQL and maps to NamedTuple Models
```