from __future__ import annotations
from typing import NamedTuple, Optional
from database.db_master import DatabaseManager


class Purchase(NamedTuple):
    id: int
    supplier_id: int
    user_id: int
    time: str
    total_amount: Optional[float]


class PurchaseController:
    """Pembungkus Data Purchases

    method : add, get, edit, remove, fetch
    """

    def add(
        supplier_id: int,
        user_id: int,
        time: str,
        total_amount: float | None = None,
    ) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            supplier_id = int(supplier_id)
            user_id = int(user_id)
            if total_amount is not None:
                total_amount = float(total_amount)
        except (ValueError, TypeError):
            raise TypeError("Failed to add purchase: 'supplier_id' and 'user_id' must be integers, and 'total_amount' must be a number.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Purchases (SupplierID, UserID, Time, TotalAmount) VALUES (?, ?, ?, ?)",
            (supplier_id, user_id, time, total_amount),
        )
        conn.commit()

    def get(purchase_id: int) -> Purchase | None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            purchase_id = int(purchase_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to get purchase: 'purchase_id' must be an integer.")

        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Purchases WHERE ID = ?", (purchase_id,))
        row = cursor.fetchone()
        return Purchase(*row) if row else None

    def edit(
        purchase_id: int,
        supplier_id: int,
        user_id: int,
        time: str,
        total_amount: float | None = None,
    ) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            purchase_id = int(purchase_id)
            supplier_id = int(supplier_id)
            user_id = int(user_id)
            if total_amount is not None:
                total_amount = float(total_amount)
        except (ValueError, TypeError):
            raise TypeError("Failed to edit purchase: 'purchase_id', 'supplier_id', and 'user_id' must be integers, and 'total_amount' must be a number.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE Purchases SET SupplierID = ?, UserID = ?, Time = ?, TotalAmount = ? WHERE ID = ?",
            (supplier_id, user_id, time, total_amount, purchase_id),
        )
        conn.commit()

    def remove(purchase_id: int) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            purchase_id = int(purchase_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to remove purchase: 'purchase_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute("DELETE FROM Purchases WHERE ID = ?", (purchase_id,))
        conn.commit()

    def fetch() -> list[Purchase]:
        """Bakal return **SEMUA** data purchase dalam bentuk list of Purchase."""
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Purchases")
        rows = cursor.fetchall()
        return [Purchase(*row) for row in rows]
