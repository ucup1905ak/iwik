# Database & Controllers

Dokumen ini merangkum struktur database dan controller yang tersedia di aplikasi.

## Schema Database
Sumber schema: [database/sql/init.sql](../database/sql/init.sql)

### Customer
Kolom:
- `ID` (INTEGER, PK, AUTOINCREMENT)
- `Name` (TEXT, NOT NULL)
- `Phone` (TEXT)

Relasi: tidak ada FK.

### Product
Kolom:
- `ID` (INTEGER, PK, AUTOINCREMENT)
- `Name` (TEXT, NOT NULL)
- `Brand` (TEXT)
- `SKU` (TEXT, UNIQUE)
- `Category` (TEXT)
- `Stock` (INTEGER, NOT NULL, DEFAULT 0)
- `Price` (REAL, NOT NULL)
- `ImagePath` (TEXT)

Relasi: tidak ada FK.

### Sales
Kolom:
- `ID` (INTEGER, PK, AUTOINCREMENT)
- `CustomerID` (INTEGER)
- `CashierID` (INTEGER, NOT NULL)
- `Time` (TEXT, NOT NULL)
- `Payment` (TEXT)
- `PaidAmount` (REAL)

Relasi:
- `CustomerID` → `Customer.ID`
- `CashierID` → `Cashier.ID`

### SalesDetail
Kolom:
- `ID` (INTEGER, PK, AUTOINCREMENT)
- `SalesID` (INTEGER, NOT NULL)
- `ProductID` (INTEGER, NOT NULL)
- `Quantity` (INTEGER, NOT NULL)
- `Discount` (REAL, DEFAULT 0)

Relasi:
- `SalesID` → `Sales.ID` (ON DELETE CASCADE)
- `ProductID` → `Product.ID`

### users
Kolom:
- `id` (INTEGER, PK, AUTOINCREMENT)
- `name` (TEXT, NOT NULL)
- `pin` (TEXT, NOT NULL)
- `role` (INTEGER, NOT NULL, CHECK 1/2)

Relasi: tidak ada FK.

### Suppliers
Kolom:
- `ID` (INTEGER, PK, AUTOINCREMENT)
- `Name` (TEXT, NOT NULL)
- `Phone` (TEXT)
- `Address` (TEXT)

Relasi: tidak ada FK.

### Purchases
Kolom:
- `ID` (INTEGER, PK, AUTOINCREMENT)
- `SupplierID` (INTEGER, NOT NULL)
- `UserID` (INTEGER, NOT NULL)
- `Time` (TEXT, NOT NULL)
- `TotalAmount` (REAL)

Relasi:
- `SupplierID` → `Suppliers.ID`
- `UserID` → `users.id`

### PurchaseDetail
Kolom:
- `ID` (INTEGER, PK, AUTOINCREMENT)
- `PurchaseID` (INTEGER, NOT NULL)
- `ProductID` (INTEGER, NOT NULL)
- `Quantity` (INTEGER, NOT NULL)
- `PurchasePrice` (REAL, NOT NULL)

Relasi:
- `PurchaseID` → `Purchases.ID` (ON DELETE CASCADE)
- `ProductID` → `Product.ID`

## Controllers
Semua controller mengikuti pola metode: `add`, `get`, `edit`, `remove`, `fetch`.

### Customer
File: [controllers/customer.py](../controllers/customer.py)

- `CustomerController.add(name, phone=None)`
- `CustomerController.get(customer_id)`
- `CustomerController.edit(customer_id, name, phone=None)`
- `CustomerController.remove(customer_id)`
- `CustomerController.fetch()`

### Product
File: [controllers/product.py](../controllers/product.py)

- `ProductController.add(name, price, stock, brand=None, sku=None, category=None, image_path=None)`
- `ProductController.get(product_id)`
- `ProductController.edit(product_id, name, brand, stock, price, sku=None, category=None, image_path=None)`
- `ProductController.remove(product_id)`
- `ProductController.fetch()`

### Sales
File: [controllers/sales.py](../controllers/sales.py)

- `SalesController.add(customer_id, cashier_id, time, payment, paid_amount)`
- `SalesController.add_return_id(customer_id, cashier_id, time, payment, paid_amount)`
- `SalesController.get(sale_id)`
- `SalesController.edit(sale_id, customer_id, cashier_id, time, payment, paid_amount)`
- `SalesController.remove(sale_id)`
- `SalesController.fetch()`

### SalesDetail
File: [controllers/sales_detail.py](../controllers/sales_detail.py)

- `SalesDetailController.add(sales_id, product_id, quantity, discount=0.0)`
- `SalesDetailController.get(detail_id)`
- `SalesDetailController.edit(detail_id, sales_id, product_id, quantity, discount=0.0)`
- `SalesDetailController.remove(detail_id)`
- `SalesDetailController.fetch()`

### User
File: [controllers/user.py](../controllers/user.py)

- `UserController.add(name, pin, role)`
- `UserController.fetch()`
- `UserController.edit(user_id, name, role, pin=None)`
- `UserController.remove(user_id)`
- `UserController.verify_pin(name, input_pin)`
- `UserController.get_first_admin_id()`

### Supplier
File: [controllers/supplier.py](../controllers/supplier.py)

- `SupplierController.add(name, phone=None, address=None)`
- `SupplierController.get(supplier_id)`
- `SupplierController.edit(supplier_id, name, phone=None, address=None)`
- `SupplierController.remove(supplier_id)`
- `SupplierController.fetch()`

### Purchase
File: [controllers/purchase.py](../controllers/purchase.py)

- `PurchaseController.add(supplier_id, user_id, time, total_amount=None)`
- `PurchaseController.get(purchase_id)`
- `PurchaseController.edit(purchase_id, supplier_id, user_id, time, total_amount=None)`
- `PurchaseController.remove(purchase_id)`
- `PurchaseController.fetch()`

### PurchaseDetail
File: [controllers/purchase_detail.py](../controllers/purchase_detail.py)

- `PurchaseDetailController.add(purchase_id, product_id, quantity, purchase_price)`
- `PurchaseDetailController.get(detail_id)`
- `PurchaseDetailController.edit(detail_id, purchase_id, product_id, quantity, purchase_price)`
- `PurchaseDetailController.remove(detail_id)`
- `PurchaseDetailController.fetch()`
