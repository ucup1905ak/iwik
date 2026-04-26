from __future__ import annotations

from api.db_master import conn, cursor


def create_product(
    name: str,
    brand: str | None,
    stock: int,
    price: float,
) -> None:
    if cursor is None or conn is None:
        raise RuntimeError("Database connection was not initialized")

    cursor.execute(
        "INSERT INTO Product (Name, Brand, Stock, Price) VALUES (?, ?, ?, ?)",
        (name, brand, stock, price),
    )
    conn.commit()


def read_product(product_id: int) -> tuple | None:
    if cursor is None:
        raise RuntimeError("Database connection was not initialized")

    cursor.execute("SELECT * FROM Product WHERE ID = ?", (product_id,))
    return cursor.fetchone()


def update_product(
    product_id: int,
    name: str,
    brand: str | None,
    stock: int,
    price: float,
) -> None:
    if cursor is None or conn is None:
        raise RuntimeError("Database connection was not initialized")

    cursor.execute(
        "UPDATE Product SET Name = ?, Brand = ?, Stock = ?, Price = ? WHERE ID = ?",
        (name, brand, stock, price, product_id),
    )
    conn.commit()


def delete_product(product_id: int) -> None:
    if cursor is None or conn is None:
        raise RuntimeError("Database connection was not initialized")

    cursor.execute("DELETE FROM Product WHERE ID = ?", (product_id,))
    conn.commit()


def list_products() -> list:
    if cursor is None:
        raise RuntimeError("Database connection was not initialized")

    cursor.execute("SELECT * FROM Product")
    return cursor.fetchall()
