from __future__ import annotations
from database.db_master import DatabaseManager

class ProductController: 

    def add(name: str, price: float, stock: int, brand: str | None = None, sku: str | None = None, category: str | None = None) -> None:
        try:
            price = float(price)
            stock = int(stock)
        except (ValueError, TypeError):
            raise TypeError("Failed to add product: 'price' must be a number and 'stock' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Product (Name, Brand, SKU, Category, Stock, Price) VALUES (?, ?, ?, ?, ?, ?)",
            (name, brand, sku, category, stock, price),
        )
        conn.commit()

    def get(product_id: int) -> tuple | None:
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to get product: 'product_id' must be an integer.")

        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Product WHERE ID = ?", (product_id,))
        return cursor.fetchone()

    def edit(product_id: int, name: str, brand: str | None, stock: int, price: float, sku: str | None = None, category: str | None = None) -> None:
        try:
            product_id = int(product_id)
            stock = int(stock)
            price = float(price)
        except (ValueError, TypeError):
            raise TypeError("Failed to edit product: 'product_id' and 'stock' must be integers, and 'price' must be a number.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE Product SET Name = ?, Brand = ?, SKU = ?, Category = ?, Stock = ?, Price = ? WHERE ID = ?",
            (name, brand, sku, category, stock, price, product_id),
        )
        conn.commit()

    def remove(product_id: int) -> None:
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to remove product: 'product_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute("DELETE FROM Product WHERE ID = ?", (product_id,))
        conn.commit()
        
    def fetch() -> list:
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Product")
        return cursor.fetchall()