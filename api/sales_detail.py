from __future__ import annotations

import api.db_master as db_master


def create_sales_detail(sales_id: int, product_id: int, quantity: int, discount: float = 0.0) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute(
        "INSERT INTO SalesDetail (SalesID, ProductID, Quantity, Discount) VALUES (?, ?, ?, ?)",
        (sales_id, product_id, quantity, discount),
    )
    conn.commit()


def read_sales_detail(detail_id: int) -> tuple | None:
    _, cursor = db_master.require_connection()
    cursor.execute("SELECT * FROM SalesDetail WHERE ID = ?", (detail_id,))
    return cursor.fetchone()


def update_sales_detail(
    detail_id: int,
    sales_id: int,
    product_id: int,
    quantity: int,
    discount: float = 0.0,
) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute(
        "UPDATE SalesDetail SET SalesID = ?, ProductID = ?, Quantity = ?, Discount = ? WHERE ID = ?",
        (sales_id, product_id, quantity, discount, detail_id),
    )
    conn.commit()


def delete_sales_detail(detail_id: int) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute("DELETE FROM SalesDetail WHERE ID = ?", (detail_id,))
    conn.commit()


def list_sales_details() -> list:
    _, cursor = db_master.require_connection()
    cursor.execute("SELECT * FROM SalesDetail")
    return cursor.fetchall()
