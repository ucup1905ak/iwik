from __future__ import annotations

import api.db_master as db_master


def create_sales_detail(sales_id: int, product_id: int, quantity: int, discount: float = 0.0) -> None:
    if db_master.cursor is None or db_master.conn is None:
        raise RuntimeError("Database connection was not initialized")

    db_master.cursor.execute(
        "INSERT INTO SalesDetail (SalesID, ProductID, Quantity, Discount) VALUES (?, ?, ?, ?)",
        (sales_id, product_id, quantity, discount),
    )
    db_master.conn.commit()


def read_sales_detail(detail_id: int) -> tuple | None:
    if db_master.cursor is None:
        raise RuntimeError("Database connection was not initialized")

    db_master.cursor.execute("SELECT * FROM SalesDetail WHERE ID = ?", (detail_id,))
    return db_master.cursor.fetchone()


def update_sales_detail(
    detail_id: int,
    sales_id: int,
    product_id: int,
    quantity: int,
    discount: float = 0.0,
) -> None:
    if db_master.cursor is None or db_master.conn is None:
        raise RuntimeError("Database connection was not initialized")

    db_master.cursor.execute(
        "UPDATE SalesDetail SET SalesID = ?, ProductID = ?, Quantity = ?, Discount = ? WHERE ID = ?",
        (sales_id, product_id, quantity, discount, detail_id),
    )
    db_master.conn.commit()


def delete_sales_detail(detail_id: int) -> None:
    if db_master.cursor is None or db_master.conn is None:
        raise RuntimeError("Database connection was not initialized")

    db_master.cursor.execute("DELETE FROM SalesDetail WHERE ID = ?", (detail_id,))
    db_master.conn.commit()


def list_sales_details() -> list:
    if db_master.cursor is None:
        raise RuntimeError("Database connection was not initialized")

    db_master.cursor.execute("SELECT * FROM SalesDetail")
    return db_master.cursor.fetchall()
