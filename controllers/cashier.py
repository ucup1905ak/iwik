from typing import NamedTuple
import database.db_master as db_master
from __future__ import annotations
from database.db_master import DatabaseManager


class Cashier(NamedTuple):
    id: int
    first_name: str
    last_name: str
    salary: float
    
class CashierController:
    """Pembungkus Data Cashier 
    
    method : create,read,update,delete,list
    """

    def create(first_name: str, last_name: str, salary: float) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # Erron handling typing 
            salary = float(salary)
        except (ValueError, TypeError):
            raise TypeError("Failed to create cashier: 'salary' must be a number.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Cashier (FirstName, LastName, Salary) VALUES (?, ?, ?)",
            (first_name, last_name, salary),
        )
        conn.commit()


    def read(cashier_id: int) -> Cashier | None:
            """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
            """
            try:  # TYPE ERROR HANDLING
                cashier_id = int(cashier_id)
            except (ValueError, TypeError):
                raise TypeError("Failed to read cashier: 'cashier_id' must be an integer.")

            _, cursor = DatabaseManager.require_connection()
            cursor.execute("SELECT * FROM Cashier WHERE ID = ?", (cashier_id,))
            row = cursor.fetchone()
            return Cashier(*row) if row else None

    def update(cashier_id: int, first_name: str, last_name: str, salary: float) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            cashier_id = int(cashier_id)
            salary = float(salary)
        except (ValueError, TypeError):
            raise TypeError("Failed to update cashier: 'cashier_id' must be an integer and 'salary' must be a number.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE Cashier SET FirstName = ?, LastName = ?, Salary = ? WHERE ID = ?",
            (first_name, last_name, salary, cashier_id),
        )
        conn.commit()

    def delete(cashier_id: int) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:  # TYPE ERROR HANDLING
            cashier_id = int(cashier_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to delete cashier: 'cashier_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute("DELETE FROM Cashier WHERE ID = ?", (cashier_id,))
        conn.commit()

    def list() -> list[Cashier]:
        """Bakal return **SEMUA** data cashier dalam bentuk list of Cashier."""
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Cashier")
        rows = cursor.fetchall()
        return [Cashier(*row) for row in rows]






