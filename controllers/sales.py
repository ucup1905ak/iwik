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
    total_price: Optional[float] = None


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
        total_price: float | None = None,
    ) -> None:
        try:
            cashier_id = int(cashier_id)
            if customer_id is not None:
                customer_id = int(customer_id)
            if paid_amount is not None:
                paid_amount = float(paid_amount)
            if total_price is not None:
                total_price = float(total_price)
        except (ValueError, TypeError):
            raise TypeError("Failed to add sale: 'cashier_id' and 'customer_id' must be integers, and 'paid_amount' must be a number.")
 
        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Sales (CustomerID, CashierID, Time, Payment, PaidAmount, TotalPrice) VALUES (?, ?, ?, ?, ?, ?)",
            (customer_id, cashier_id, time, payment, paid_amount, total_price),
        )
        conn.commit()
 
    def add_return_id(
        customer_id: int | None,
        cashier_id: int,
        time: str,
        payment: str | None,
        paid_amount: float | None,
        total_price: float | None = None,
    ) -> int:
        try:
            cashier_id = int(cashier_id)
            if customer_id is not None:
                customer_id = int(customer_id)
            if paid_amount is not None:
                paid_amount = float(paid_amount)
            if total_price is not None:
                total_price = float(total_price)
        except (ValueError, TypeError):
            raise TypeError("Failed to add sale: 'cashier_id' and 'customer_id' must be integers, and 'paid_amount' must be a number.")
 
        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Sales (CustomerID, CashierID, Time, Payment, PaidAmount, TotalPrice) VALUES (?, ?, ?, ?, ?, ?)",
            (customer_id, cashier_id, time, payment, paid_amount, total_price),
        )
        sale_id = cursor.lastrowid
        conn.commit()
        return int(sale_id)
 
    def get(sale_id: int) -> Sales | None:
        try:
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
        total_price: float | None = None,
    ) -> None:
        try:
            sale_id = int(sale_id)
            cashier_id = int(cashier_id)
            if customer_id is not None:
                customer_id = int(customer_id)
            if paid_amount is not None:
                paid_amount = float(paid_amount)
            if total_price is not None:
                total_price = float(total_price)
        except (ValueError, TypeError):
            raise TypeError("Failed to edit sale: 'sale_id' and 'cashier_id' must be integers, and 'paid_amount' must be a number.")
 
        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE Sales SET CustomerID = ?, CashierID = ?, Time = ?, Payment = ?, PaidAmount = ?, TotalPrice = ? WHERE ID = ?",
            (customer_id, cashier_id, time, payment, paid_amount, total_price, sale_id),
        )
        conn.commit()
 
    def remove(sale_id: int) -> None:
        try:
            sale_id = int(sale_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to remove sale: 'sale_id' must be an integer.")
 
        conn, cursor = DatabaseManager.require_connection()
        cursor.execute("DELETE FROM Sales WHERE ID = ?", (sale_id,))
        conn.commit()
 
    def fetch() -> list[Sales]:
        """Bakal return SEMUA data sales dari tanggal terbaru."""
        
        _, cursor = DatabaseManager.require_connection()

        cursor.execute("""
            SELECT ID, CustomerID, CashierID, Time, Payment, PaidAmount, TotalPrice
            FROM Sales
            ORDER BY Time DESC
        """)

        rows = cursor.fetchall()

        return [Sales(*row) for row in rows]