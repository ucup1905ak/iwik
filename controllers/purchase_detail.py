from __future__ import annotations
from typing import NamedTuple
from database.db_master import DatabaseManager


class PurchaseDetail(NamedTuple):
    id: int
    purchase_id: int
    product_id: int
    quantity: int
    purchase_price: float


class PurchaseDetailController:
    """Pembungkus Data PurchaseDetail

    method : add, get, edit, remove, fetch
    """

    def add(
        purchase_id: int,
        product_id: int,
        quantity: int,
        purchase_price: float,
    ) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            purchase_id = int(purchase_id)
            product_id = int(product_id)
            quantity = int(quantity)
            purchase_price = float(purchase_price)
        except (ValueError, TypeError):
            raise TypeError("Failed to add purchase detail: 'purchase_id', 'product_id', and 'quantity' must be integers, and 'purchase_price' must be a number.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO PurchaseDetail (PurchaseID, ProductID, Quantity, PurchasePrice) VALUES (?, ?, ?, ?)",
            (purchase_id, product_id, quantity, purchase_price),
        )
        conn.commit()

    def get(detail_id: int) -> PurchaseDetail | None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            detail_id = int(detail_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to get purchase detail: 'detail_id' must be an integer.")

        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM PurchaseDetail WHERE ID = ?", (detail_id,))
        row = cursor.fetchone()
        return PurchaseDetail(*row) if row else None

    def edit(
        detail_id: int,
        purchase_id: int,
        product_id: int,
        quantity: int,
        purchase_price: float,
    ) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            detail_id = int(detail_id)
            purchase_id = int(purchase_id)
            product_id = int(product_id)
            quantity = int(quantity)
            purchase_price = float(purchase_price)
        except (ValueError, TypeError):
            raise TypeError("Failed to edit purchase detail: 'detail_id', 'purchase_id', 'product_id', and 'quantity' must be integers, and 'purchase_price' must be a number.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE PurchaseDetail SET PurchaseID = ?, ProductID = ?, Quantity = ?, PurchasePrice = ? WHERE ID = ?",
            (purchase_id, product_id, quantity, purchase_price, detail_id),
        )
        conn.commit()

    def remove(detail_id: int) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah."""
        try:  # TYPE ERROR HANDLING
            detail_id = int(detail_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to remove purchase detail: 'detail_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute("DELETE FROM PurchaseDetail WHERE ID = ?", (detail_id,))
        conn.commit()

    def fetch() -> list[PurchaseDetail]:
        """Bakal return **SEMUA** data purchase detail dalam bentuk list of PurchaseDetail."""
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM PurchaseDetail")
        rows = cursor.fetchall()
        return [PurchaseDetail(*row) for row in rows]
    
    @staticmethod
    def calculate_total(purchase_id: int) -> float:
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("""
            SELECT SUM(Quantity * PurchasePrice)
            FROM PurchaseDetail
            WHERE PurchaseID = ?
        """, (purchase_id,))
        
        result = cursor.fetchone()[0]
        return result or 0.0
    
    @staticmethod
    def update_purchase_total(purchase_id: int):
        total = PurchaseDetailController.calculate_total(purchase_id)

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE Purchases SET TotalAmount = ? WHERE ID = ?",
            (total, purchase_id),
        )
        conn.commit()
