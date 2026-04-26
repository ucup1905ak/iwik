from __future__ import annotations

import api.db_master as db_master


def create_sale(
    customer_id: int | None,
    cashier_id: int,
    time: str,
    payment: str | None,
    paid_amount: float | None,
) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute(
        "INSERT INTO Sales (CustomerID, CashierID, Time, Payment, PaidAmount) VALUES (?, ?, ?, ?, ?)",
        (customer_id, cashier_id, time, payment, paid_amount),
    )
    conn.commit()


def create_sale_return_id(
    customer_id: int | None,
    cashier_id: int,
    time: str,
    payment: str | None,
    paid_amount: float | None,
) -> int:
    conn, cursor = db_master.require_connection()
    cursor.execute(
        "INSERT INTO Sales (CustomerID, CashierID, Time, Payment, PaidAmount) VALUES (?, ?, ?, ?, ?)",
        (customer_id, cashier_id, time, payment, paid_amount),
    )
    sale_id = cursor.lastrowid
    conn.commit()
    return int(sale_id)


def read_sale(sale_id: int) -> tuple | None:
    _, cursor = db_master.require_connection()
    cursor.execute("SELECT * FROM Sales WHERE ID = ?", (sale_id,))
    return cursor.fetchone()


def update_sale(
    sale_id: int,
    customer_id: int | None,
    cashier_id: int,
    time: str,
    payment: str | None,
    paid_amount: float | None,
) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute(
        "UPDATE Sales SET CustomerID = ?, CashierID = ?, Time = ?, Payment = ?, PaidAmount = ? WHERE ID = ?",
        (customer_id, cashier_id, time, payment, paid_amount, sale_id),
    )
    conn.commit()


def delete_sale(sale_id: int) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute("DELETE FROM Sales WHERE ID = ?", (sale_id,))
    conn.commit()


def list_sales() -> list:
    _, cursor = db_master.require_connection()
    cursor.execute("SELECT * FROM Sales")
    return cursor.fetchall()
