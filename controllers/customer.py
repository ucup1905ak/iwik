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

    method : create, read, update, delete, list
    """

    def create(name: str, phone: str | None = None) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            name = str(name)
        except (ValueError, TypeError):
            raise TypeError("Failed to create customer: 'name' must be a string.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Customer (Name, Phone) VALUES (?, ?)",
            (name, phone),
        )
        conn.commit()

    def read(customer_id: int) -> Customer | None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            customer_id = int(customer_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to read customer: 'customer_id' must be an integer.")

        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Customer WHERE ID = ?", (customer_id,))
        row = cursor.fetchone()
        return Customer(*row) if row else None

    def update(customer_id: int, name: str, phone: str | None = None) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            customer_id = int(customer_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to update customer: 'customer_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE Customer SET Name = ?, Phone = ? WHERE ID = ?",
            (name, phone, customer_id),
        )
        conn.commit()

    def delete(customer_id: int) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            customer_id = int(customer_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to delete customer: 'customer_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute("DELETE FROM Customer WHERE ID = ?", (customer_id,))
        conn.commit()

    def list() -> list[Customer]:
        """Bakal return **SEMUA** data customer dalam bentuk list of Customer."""
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Customer")
        rows = cursor.fetchall()
        return [Customer(*row) for row in rows]