from __future__ import annotations
from typing import NamedTuple, Optional
from database.db_master import DatabaseManager


class SalesDetail(NamedTuple):
    id: int
    sales_id: int
    product_id: int
    quantity: int
    discount: Optional[float]


class SalesDetailController:
    """Pembungkus Data SalesDetail

    method : create, read, update, delete, list
    """

    def create(sales_id: int, product_id: int, quantity: int, discount: float = 0.0) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            sales_id = int(sales_id)
            product_id = int(product_id)
            quantity = int(quantity)
            discount = float(discount)
        except (ValueError, TypeError):
            raise TypeError("Failed to create sales detail: 'sales_id', 'product_id', and 'quantity' must be integers, and 'discount' must be a number.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO SalesDetail (SalesID, ProductID, Quantity, Discount) VALUES (?, ?, ?, ?)",
            (sales_id, product_id, quantity, discount),
        )
        conn.commit()

    def read(detail_id: int) -> SalesDetail | None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            detail_id = int(detail_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to read sales detail: 'detail_id' must be an integer.")

        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM SalesDetail WHERE ID = ?", (detail_id,))
        row = cursor.fetchone()
        return SalesDetail(*row) if row else None

    def update(
        detail_id: int,
        sales_id: int,
        product_id: int,
        quantity: int,
        discount: float = 0.0,
    ) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            detail_id = int(detail_id)
            sales_id = int(sales_id)
            product_id = int(product_id)
            quantity = int(quantity)
            discount = float(discount)
        except (ValueError, TypeError):
            raise TypeError("Failed to update sales detail: 'detail_id', 'sales_id', 'product_id', and 'quantity' must be integers, and 'discount' must be a number.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE SalesDetail SET SalesID = ?, ProductID = ?, Quantity = ?, Discount = ? WHERE ID = ?",
            (sales_id, product_id, quantity, discount, detail_id),
        )
        conn.commit()

    def delete(detail_id: int) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            detail_id = int(detail_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to delete sales detail: 'detail_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute("DELETE FROM SalesDetail WHERE ID = ?", (detail_id,))
        conn.commit()

    def list() -> list[SalesDetail]:
        """Bakal return **SEMUA** data sales detail dalam bentuk list of SalesDetail."""
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM SalesDetail")
        rows = cursor.fetchall()
        return [SalesDetail(*row) for row in rows]