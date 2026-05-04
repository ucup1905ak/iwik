from __future__ import annotations
import database.db_master as db_master
from typing import NamedTuple, Optional
from database.db_master import DatabaseManager


class Customer(NamedTuple):
    id: int
    name: str
    phone: Optional[str]


class CustomerController:
    """Pembungkus Data Customer

    method : add, get, edit, remove, fetch
    """

    def add(name: str, phone: str | None = None) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            name = str(name)
        except (ValueError, TypeError):
            raise TypeError("Failed to add customer: 'name' must be a string.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Customer (Name, Phone) VALUES (?, ?)",
            (name, phone),
        )
        conn.commit()

    def get(customer_id: int) -> Customer | None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            customer_id = int(customer_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to get customer: 'customer_id' must be an integer.")

        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Customer WHERE ID = ?", (customer_id,))
        row = cursor.fetchone()
        return Customer(*row) if row else None

    def edit(customer_id: int, name: str, phone: str | None = None) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            customer_id = int(customer_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to edit customer: 'customer_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE Customer SET Name = ?, Phone = ? WHERE ID = ?",
            (name, phone, customer_id),
        )
        conn.commit()

    def remove(customer_id: int) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            customer_id = int(customer_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to remove customer: 'customer_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute("DELETE FROM Customer WHERE ID = ?", (customer_id,))
        conn.commit()

    def fetch() -> list[Customer]:
        """Bakal return **SEMUA** data customer dalam bentuk list of Customer."""
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Customer")
        rows = cursor.fetchall()
        return [Customer(*row) for row in rows]