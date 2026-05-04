from __future__ import annotations
from typing import NamedTuple, Optional
from database.db_master import DatabaseManager


class Supplier(NamedTuple):
    id: int
    name: str
    phone: Optional[str]
    address: Optional[str]


class SupplierController:
    """Pembungkus Data Suppliers

    method : add, get, edit, remove, fetch
    """

    def add(name: str, phone: str | None = None, address: str | None = None) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            name = str(name)
        except (ValueError, TypeError):
            raise TypeError("Failed to add supplier: 'name' must be a string.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Suppliers (Name, Phone, Address) VALUES (?, ?, ?)",
            (name, phone, address),
        )
        conn.commit()

    def get(supplier_id: int) -> Supplier | None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            supplier_id = int(supplier_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to get supplier: 'supplier_id' must be an integer.")

        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Suppliers WHERE ID = ?", (supplier_id,))
        row = cursor.fetchone()
        return Supplier(*row) if row else None

    def edit(supplier_id: int, name: str, phone: str | None = None, address: str | None = None) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            supplier_id = int(supplier_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to edit supplier: 'supplier_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE Suppliers SET Name = ?, Phone = ?, Address = ? WHERE ID = ?",
            (name, phone, address, supplier_id),
        )
        conn.commit()

    def remove(supplier_id: int) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            supplier_id = int(supplier_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to remove supplier: 'supplier_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute("DELETE FROM Suppliers WHERE ID = ?", (supplier_id,))
        conn.commit()

    def fetch() -> list[Supplier]:
        """Bakal return **SEMUA** data supplier dalam bentuk list of Supplier."""
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Suppliers")
        rows = cursor.fetchall()
        return [Supplier(*row) for row in rows]
