from __future__ import annotations
from database.db_master import DatabaseManager
from typing import NamedTuple, Optional

import database.db_master as db_master

class Receivables(NamedTuple):
    id: int
    sales_id: int
    customer_id: Optional[int]
    amount_paid: float
    total_amount: float
    due_date: Optional[str]
    status: str


class ReceivablesController:
    """Pembungkus Data Receivables (Piutang)
 
    method : add, get, edit, remove, fetch
    """
 
    def add(
        sales_id: int,
        customer_id: int | None,
        total_amount: float,
        due_date: str | None,
        amount_paid: float = 0.0,
        status: str = 'unpaid',
    ) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:
            sales_id = int(sales_id)
            if customer_id is not None:
                customer_id = int(customer_id)
            total_amount = float(total_amount)
            amount_paid = float(amount_paid)
        except (ValueError, TypeError):
            raise TypeError("Failed to add receivable: Invalid data types provided.")
 
        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Receivables (SalesID, CustomerID, AmountPaid, TotalAmount, DueDate, Status) VALUES (?, ?, ?, ?, ?, ?)",
            (sales_id, customer_id, amount_paid, total_amount, due_date, status),
        )
        conn.commit()
 
    def get(receivable_id: int) -> Receivables | None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:
            receivable_id = int(receivable_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to get receivable: 'receivable_id' must be an integer.")
 
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Receivables WHERE ID = ?", (receivable_id,))
        row = cursor.fetchone()
        return Receivables(*row) if row else None
 
    def edit(
        receivable_id: int,
        sales_id: int,
        customer_id: int | None,
        amount_paid: float,
        total_amount: float,
        due_date: str | None,
        status: str,
    ) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:
            receivable_id = int(receivable_id)
            sales_id = int(sales_id)
            if customer_id is not None:
                customer_id = int(customer_id)
            amount_paid = float(amount_paid)
            total_amount = float(total_amount)
        except (ValueError, TypeError):
            raise TypeError("Failed to edit receivable: Invalid data types provided.")
 
        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE Receivables SET SalesID = ?, CustomerID = ?, AmountPaid = ?, TotalAmount = ?, DueDate = ?, Status = ? WHERE ID = ?",
            (sales_id, customer_id, amount_paid, total_amount, due_date, status, receivable_id),
        )
        conn.commit()
 
    def remove(receivable_id: int) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:
            receivable_id = int(receivable_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to remove receivable: 'receivable_id' must be an integer.")
 
        conn, cursor = DatabaseManager.require_connection()
        cursor.execute("DELETE FROM Receivables WHERE ID = ?", (receivable_id,))
        conn.commit()
 
    def fetch() -> list[Receivables]:
        """Bakal return **SEMUA** data receivables dalam bentuk list of Receivables."""
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Receivables")
        rows = cursor.fetchall()
        return [Receivables(*row) for row in rows]

    def get_by_sales_id(sales_id: int) -> Receivables | None:
        """Mendapatkan data piutang berdasarkan SalesID."""
        try:
            sales_id = int(sales_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to get receivable: 'sales_id' must be an integer.")

        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Receivables WHERE SalesID = ?", (sales_id,))
        row = cursor.fetchone()
        return Receivables(*row) if row else None