from __future__ import annotations

from api.db_master import conn, cursor


def create_customer(name: str, phone: str | None = None) -> None:
    if cursor is None or conn is None:
        raise RuntimeError("Database connection was not initialized")

    cursor.execute(
        "INSERT INTO Customer (Name, Phone) VALUES (?, ?)",
        (name, phone),
    )
    conn.commit()


def read_customer(customer_id: int) -> tuple | None:
    if cursor is None:
        raise RuntimeError("Database connection was not initialized")

    cursor.execute("SELECT * FROM Customer WHERE ID = ?", (customer_id,))
    return cursor.fetchone()


def update_customer(customer_id: int, name: str, phone: str | None = None) -> None:
    if cursor is None or conn is None:
        raise RuntimeError("Database connection was not initialized")

    cursor.execute(
        "UPDATE Customer SET Name = ?, Phone = ? WHERE ID = ?",
        (name, phone, customer_id),
    )
    conn.commit()


def delete_customer(customer_id: int) -> None:
    if cursor is None or conn is None:
        raise RuntimeError("Database connection was not initialized")

    cursor.execute("DELETE FROM Customer WHERE ID = ?", (customer_id,))
    conn.commit()


def list_customers() -> list:
    if cursor is None:
        raise RuntimeError("Database connection was not initialized")

    cursor.execute("SELECT * FROM Customer")
    return cursor.fetchall()
