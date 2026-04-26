from __future__ import annotations

import api.db_master as db_master


def create_product(
    name: str,
    brand: str | None,
    stock: int,
    price: float,
) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute(
        "INSERT INTO Product (Name, Brand, Stock, Price) VALUES (?, ?, ?, ?)",
        (name, brand, stock, price),
    )
    conn.commit()


def read_product(product_id: int) -> tuple | None:
    _, cursor = db_master.require_connection()
    cursor.execute("SELECT * FROM Product WHERE ID = ?", (product_id,))
    return cursor.fetchone()


def update_product(
    product_id: int,
    name: str,
    brand: str | None,
    stock: int,
    price: float,
) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute(
        "UPDATE Product SET Name = ?, Brand = ?, Stock = ?, Price = ? WHERE ID = ?",
        (name, brand, stock, price, product_id),
    )
    conn.commit()


def delete_product(product_id: int) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute("DELETE FROM Product WHERE ID = ?", (product_id,))
    conn.commit()


def list_products() -> list:
    _, cursor = db_master.require_connection()
    cursor.execute("SELECT * FROM Product")
    return cursor.fetchall()
