from __future__ import annotations

import argparse
import os
import random
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(APP_DIR, "abc.db")
DEFAULT_SCHEMA_PATH = os.path.join(APP_DIR, "sql", "init.sql")


FIRST_NAMES = [
    "Budi",
    "Siti",
    "Agus",
    "Dewi",
    "Rizki",
    "Putri",
    "Andi",
    "Rina",
    "Dimas",
    "Nadia",
    "Farhan",
    "Alya",
    "Farel",
    "Udin",
    "Eka",
    "Bayu",
    "Wulan",
    "Rafi",
    "Citra",
    "Salsa",
]

LAST_NAMES = [
    "Saputra",
    "Wijaya",
    "Pratama",
    "Sari",
    "Hidayat",
    "Utama",
    "Nugroho",
    "Lestari",
    "Wahyudi",
    "Permata",
    "Maulana",
    "Ananda",
    "Kusuma",
    "Santoso",
    "Setiawan",
    "Rahmawati",
]

BRANDS = [
    "IndoFresh",
    "NusaMart",
    "Sinar",
    "Prima",
    "Mega",
    "Sejahtera",
    "Nusantara",
    "Sentosa",
    "Berkah",
    "Mantap",
]

PRODUCT_WORDS = [
    "Coffee",
    "Tea",
    "Milk",
    "Sugar",
    "Rice",
    "Noodles",
    "Soap",
    "Shampoo",
    "Water",
    "Snack",
    "Biscuits",
    "Chocolate",
    "Juice",
    "Eggs",
    "Flour",
    "Salt",
    "Sauce",
    "Chips",
    "Candy",
    "Tissue",
]

PAYMENTS = ["Cash", "Card", "EWallet"]


@dataclass(frozen=True)
class SeedConfig:
    cashiers: int
    customers: int
    products: int
    sales: int
    max_items_per_sale: int


def _rand_phone(rng: random.Random) -> str:
    # Indonesian-style mobile number, not guaranteed to be real.
    return "08" + "".join(str(rng.randrange(10)) for _ in range(10))


def _rand_name(rng: random.Random) -> tuple[str, str]:
    return rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)


def _rand_customer_name(rng: random.Random) -> str:
    first, last = _rand_name(rng)
    return f"{first} {last}"


def _read_schema(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _ensure_schema(conn: sqlite3.Connection, schema_path: str) -> None:
    conn.executescript(_read_schema(schema_path))


def _wipe_tables(conn: sqlite3.Connection) -> None:
    # Order matters because of foreign keys.
    conn.execute("PRAGMA foreign_keys = OFF")
    for table in ["SalesDetail", "Sales", "Product", "Customer", "Cashier"]:
        conn.execute(f"DELETE FROM {table}")
    # Reset AUTOINCREMENT counters (safe if table absent).
    conn.execute("DELETE FROM sqlite_sequence")
    conn.execute("PRAGMA foreign_keys = ON")


def _chunks(items: list[tuple], size: int) -> Iterable[list[tuple]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def seed_database(
    db_path: str,
    schema_path: str,
    config: SeedConfig,
    *,
    seed: int = 42,
    wipe: bool = False,
) -> None:
    rng = random.Random(seed)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        _ensure_schema(conn, schema_path)

        if wipe:
            _wipe_tables(conn)

        # --- Cashier
        cashiers: list[tuple[str, str, float]] = []
        for _ in range(config.cashiers):
            first, last = _rand_name(rng)
            # salary in IDR-like range; stored as REAL.
            salary = float(rng.randrange(3_000_000, 9_000_000, 50_000))
            cashiers.append((first, last, salary))

        conn.executemany(
            "INSERT INTO Cashier (FirstName, LastName, Salary) VALUES (?, ?, ?)",
            cashiers,
        )

        # --- Customer
        customers: list[tuple[str, str]] = []
        for _ in range(config.customers):
            name = _rand_customer_name(rng)
            phone = _rand_phone(rng) if rng.random() < 0.9 else None
            customers.append((name, phone))

        conn.executemany(
            "INSERT INTO Customer (Name, Phone) VALUES (?, ?)",
            customers,
        )

        # --- Product
        products: list[tuple[str, str, int, float]] = []
        for i in range(config.products):
            word = rng.choice(PRODUCT_WORDS)
            name = f"{word} {i + 1:04d}"
            brand = rng.choice(BRANDS) if rng.random() < 0.85 else None
            stock = int(rng.randrange(0, 250))
            price = float(rng.randrange(2_000, 250_000, 500))
            products.append((name, brand, stock, price))

        conn.executemany(
            "INSERT INTO Product (Name, Brand, Stock, Price) VALUES (?, ?, ?, ?)",
            products,
        )

        # Determine ID ranges (assuming empty DB or wipe; still OK if not empty)
        cashier_min_id = conn.execute("SELECT MIN(ID) FROM Cashier").fetchone()[0]
        cashier_max_id = conn.execute("SELECT MAX(ID) FROM Cashier").fetchone()[0]
        customer_min_id = conn.execute("SELECT MIN(ID) FROM Customer").fetchone()[0]
        customer_max_id = conn.execute("SELECT MAX(ID) FROM Customer").fetchone()[0]
        product_min_id = conn.execute("SELECT MIN(ID) FROM Product").fetchone()[0]
        product_max_id = conn.execute("SELECT MAX(ID) FROM Product").fetchone()[0]

        if cashier_min_id is None or product_min_id is None:
            raise RuntimeError("Failed to create base tables (Cashier/Product)")

        # Fetch product prices once for computing PaidAmount
        product_prices = {
            row[0]: float(row[1])
            for row in conn.execute("SELECT ID, Price FROM Product").fetchall()
        }

        # --- Sales + SalesDetail
        now = datetime.now()
        sales_ids: list[int] = []

        for sale_index in range(config.sales):
            cashier_id = rng.randint(int(cashier_min_id), int(cashier_max_id))
            # allow NULL customer sometimes
            customer_id = (
                rng.randint(int(customer_min_id), int(customer_max_id))
                if (customer_min_id is not None and rng.random() < 0.85)
                else None
            )
            when = now - timedelta(minutes=rng.randrange(0, 60 * 24 * 30))
            payment = rng.choice(PAYMENTS)

            # Create sale first with placeholder PaidAmount, then update after details
            cur = conn.execute(
                "INSERT INTO Sales (CustomerID, CashierID, Time, Payment, PaidAmount) VALUES (?, ?, ?, ?, ?)",
                (customer_id, cashier_id, when.isoformat(timespec="seconds"), payment, 0.0),
            )
            sale_id = int(cur.lastrowid)
            sales_ids.append(sale_id)

            item_count = rng.randint(1, max(1, config.max_items_per_sale))
            details: list[tuple[int, int, int, float]] = []
            total = 0.0

            for _ in range(item_count):
                product_id = rng.randint(int(product_min_id), int(product_max_id))
                qty = rng.randint(1, 5)
                discount = rng.choice([0.0, 0.0, 0.05, 0.1, 0.15])
                details.append((sale_id, product_id, qty, float(discount)))

                price = product_prices.get(product_id, 0.0)
                line = price * qty * (1.0 - discount)
                total += line

            conn.executemany(
                "INSERT INTO SalesDetail (SalesID, ProductID, Quantity, Discount) VALUES (?, ?, ?, ?)",
                details,
            )

            conn.execute("UPDATE Sales SET PaidAmount = ? WHERE ID = ?", (float(total), sale_id))

            # Commit every N sales to keep it fast and not too much RAM
            if (sale_index + 1) % 500 == 0:
                conn.commit()

        conn.commit()

    finally:
        conn.close()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Seed SQLite database with large sample data")
    p.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to SQLite .db file")
    p.add_argument("--schema", default=DEFAULT_SCHEMA_PATH, help="Path to schema .sql file")
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    p.add_argument("--wipe", action="store_true", help="Delete existing rows before seeding")

    p.add_argument("--cashiers", type=int, default=50)
    p.add_argument("--customers", type=int, default=1000)
    p.add_argument("--products", type=int, default=500)
    p.add_argument("--sales", type=int, default=5000)
    p.add_argument("--max-items", type=int, default=5)

    return p.parse_args()


def main() -> None:
    args = parse_args()
    config = SeedConfig(
        cashiers=args.cashiers,
        customers=args.customers,
        products=args.products,
        sales=args.sales,
        max_items_per_sale=args.max_items,
    )

    seed_database(
        db_path=args.db,
        schema_path=args.schema,
        config=config,
        seed=args.seed,
        wipe=args.wipe,
    )

    print("Done.")
    print(f"DB: {args.db}")
    print(
        f"Inserted approx: cashiers={args.cashiers}, customers={args.customers}, products={args.products}, sales={args.sales}"
    )


if __name__ == "__main__":
    main()
