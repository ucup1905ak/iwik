from __future__ import annotations

import api.db_master as db_master


def create_sale(
    customer_id: int | None,
    cashier_id: int,
    time: str,
    payment: str | None,
    paid_amount: float | None,
) -> None:
    if db_master.cursor is None or db_master.conn is None:
        raise RuntimeError("Database connection was not initialized")

    db_master.cursor.execute(
        "INSERT INTO Sales (CustomerID, CashierID, Time, Payment, PaidAmount) VALUES (?, ?, ?, ?, ?)",
        (customer_id, cashier_id, time, payment, paid_amount),
    )
    db_master.conn.commit()


def read_sale(sale_id: int) -> tuple | None:
    if db_master.cursor is None:
        raise RuntimeError("Database connection was not initialized")

    db_master.cursor.execute("SELECT * FROM Sales WHERE ID = ?", (sale_id,))
    return db_master.cursor.fetchone()


def update_sale(
    sale_id: int,
    customer_id: int | None,
    cashier_id: int,
    time: str,
    payment: str | None,
    paid_amount: float | None,
) -> None:
    if db_master.cursor is None or db_master.conn is None:
        raise RuntimeError("Database connection was not initialized")

    db_master.cursor.execute(
        "UPDATE Sales SET CustomerID = ?, CashierID = ?, Time = ?, Payment = ?, PaidAmount = ? WHERE ID = ?",
        (customer_id, cashier_id, time, payment, paid_amount, sale_id),
    )
    db_master.conn.commit()


def delete_sale(sale_id: int) -> None:
    if db_master.cursor is None or db_master.conn is None:
        raise RuntimeError("Database connection was not initialized")

    db_master.cursor.execute("DELETE FROM Sales WHERE ID = ?", (sale_id,))
    db_master.conn.commit()


def list_sales() -> list:
    if db_master.cursor is None:
        raise RuntimeError("Database connection was not initialized")

    db_master.cursor.execute("SELECT * FROM Sales")
    return db_master.cursor.fetchall()
