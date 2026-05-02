from __future__ import annotations

import database.db_master as db_master


def create_customer(name: str, phone: str | None = None) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute(
        "INSERT INTO Customer (Name, Phone) VALUES (?, ?)",
        (name, phone),
    )
    conn.commit()


def read_customer(customer_id: int) -> tuple | None:
    _, cursor = db_master.require_connection()
    cursor.execute("SELECT * FROM Customer WHERE ID = ?", (customer_id,))
    return cursor.fetchone()


def update_customer(customer_id: int, name: str, phone: str | None = None) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute(
        "UPDATE Customer SET Name = ?, Phone = ? WHERE ID = ?",
        (name, phone, customer_id),
    )
    conn.commit()


def delete_customer(customer_id: int) -> None:
    conn, cursor = db_master.require_connection()
    cursor.execute("DELETE FROM Customer WHERE ID = ?", (customer_id,))
    conn.commit()


def list_customers() -> list:
    _, cursor = db_master.require_connection()
    cursor.execute("SELECT * FROM Customer")
    return cursor.fetchall()
