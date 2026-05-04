PRAGMA foreign_keys = ON;


-- Customer Table
CREATE TABLE IF NOT EXISTS Customer (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Phone TEXT
);

-- Product Table
CREATE TABLE IF NOT EXISTS Product (
    ID          INTEGER PRIMARY KEY AUTOINCREMENT,
    Name        TEXT    NOT NULL,
    Brand       TEXT,
    SKU         TEXT    UNIQUE,
    Category    TEXT,
    Stock       INTEGER NOT NULL DEFAULT 0,
    Price       REAL    NOT NULL,
    ImagePath   TEXT
);

-- Sales Table
CREATE TABLE IF NOT EXISTS Sales (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerID INTEGER,
    CashierID INTEGER NOT NULL,
    Time TEXT NOT NULL,
    Payment TEXT,
    PaidAmount REAL,

    FOREIGN KEY (CustomerID) REFERENCES Customer(ID),
    FOREIGN KEY (CashierID) REFERENCES users(id)
);

-- SalesDetail Table
CREATE TABLE IF NOT EXISTS SalesDetail (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    SalesID INTEGER NOT NULL,
    ProductID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL,
    Discount REAL DEFAULT 0,

    FOREIGN KEY (SalesID) REFERENCES Sales(ID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Product(ID)
);
CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        pin TEXT NOT NULL,
        role INTEGER NOT NULL CHECK(role IN (1, 2))
);

-- Suppliers Table
CREATE TABLE IF NOT EXISTS Suppliers (
    ID          INTEGER     PRIMARY KEY AUTOINCREMENT,
    Name        TEXT        NOT NULL,
    Phone       TEXT,
    Address     TEXT
);

-- Purchases Table
CREATE TABLE IF NOT EXISTS Purchases (
    ID          INTEGER     PRIMARY KEY AUTOINCREMENT,
    SupplierID  INTEGER     NOT NULL,
    UserID      INTEGER     NOT NULL,
    Time        TEXT        NOT NULL,
    TotalAmount REAL,

    FOREIGN KEY (SupplierID) REFERENCES Suppliers(ID),
    FOREIGN KEY (UserID) REFERENCES users(id)
);

-- PurchaseDetail Table
CREATE TABLE IF NOT EXISTS PurchaseDetail (
    ID              INTEGER     PRIMARY KEY AUTOINCREMENT,
    PurchaseID      INTEGER     NOT NULL,
    ProductID       INTEGER     NOT NULL,
    Quantity        INTEGER     NOT NULL,
    PurchasePrice   REAL        NOT NULL,

    FOREIGN KEY (PurchaseID) REFERENCES Purchases(ID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Product(ID)
);