from __future__ import annotations

import database.db_master as db_master
from database.db_master import DatabaseManager
from typing import NamedTuple, Optional

class Sales(NamedTuple):
    id: int
    customer_id: Optional[int]
    cashier_id: int
    time: str
    payment: Optional[str]
    paid_amount: Optional[float]


class SalesController:
    """Pembungkus Data Sales
 
    method : add, add_return_id, get, edit, remove, fetch
    """
 
    def add(
        customer_id: int | None,
        cashier_id: int,
        time: str,
        payment: str | None,
        paid_amount: float | None,
    ) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            cashier_id = int(cashier_id)
            if customer_id is not None:
                customer_id = int(customer_id)
            if paid_amount is not None:
                paid_amount = float(paid_amount)
        except (ValueError, TypeError):
            raise TypeError("Failed to add sale: 'cashier_id' and 'customer_id' must be integers, and 'paid_amount' must be a number.")
 
        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Sales (CustomerID, CashierID, Time, Payment, PaidAmount) VALUES (?, ?, ?, ?, ?)",
            (customer_id, cashier_id, time, payment, paid_amount),
        )
        conn.commit()
 
    def add_return_id(
        customer_id: int | None,
        cashier_id: int,
        time: str,
        payment: str | None,
        paid_amount: float | None,
    ) -> int:
        """Sama seperti add, tapi return ID dari sale yang baru dibuat.
        """
        try:  # TYPE ERROR HANDLING
            cashier_id = int(cashier_id)
            if customer_id is not None:
                customer_id = int(customer_id)
            if paid_amount is not None:
                paid_amount = float(paid_amount)
        except (ValueError, TypeError):
            raise TypeError("Failed to add sale: 'cashier_id' and 'customer_id' must be integers, and 'paid_amount' must be a number.")
 
        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Sales (CustomerID, CashierID, Time, Payment, PaidAmount) VALUES (?, ?, ?, ?, ?)",
            (customer_id, cashier_id, time, payment, paid_amount),
        )
        sale_id = cursor.lastrowid
        conn.commit()
        return int(sale_id)
 
    def get(sale_id: int) -> Sales | None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            sale_id = int(sale_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to get sale: 'sale_id' must be an integer.")
 
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Sales WHERE ID = ?", (sale_id,))
        row = cursor.fetchone()
        return Sales(*row) if row else None
 
    def edit(
        sale_id: int,
        customer_id: int | None,
        cashier_id: int,
        time: str,
        payment: str | None,
        paid_amount: float | None,
    ) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            sale_id = int(sale_id)
            cashier_id = int(cashier_id)
            if customer_id is not None:
                customer_id = int(customer_id)
            if paid_amount is not None:
                paid_amount = float(paid_amount)
        except (ValueError, TypeError):
            raise TypeError("Failed to edit sale: 'sale_id' and 'cashier_id' must be integers, and 'paid_amount' must be a number.")
 
        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE Sales SET CustomerID = ?, CashierID = ?, Time = ?, Payment = ?, PaidAmount = ? WHERE ID = ?",
            (customer_id, cashier_id, time, payment, paid_amount, sale_id),
        )
        conn.commit()
 
    def remove(sale_id: int) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            sale_id = int(sale_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to remove sale: 'sale_id' must be an integer.")
 
        conn, cursor = DatabaseManager.require_connection()
        cursor.execute("DELETE FROM Sales WHERE ID = ?", (sale_id,))
        conn.commit()
 
    def fetch() -> list[Sales]:
        """Bakal return **SEMUA** data sales dalam bentuk list of Sales."""
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Sales")
        rows = cursor.fetchall()
        return [Sales(*row) for row in rows]
