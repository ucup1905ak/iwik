# controllers.product
from __future__ import annotations
from typing import NamedTuple, Optional
from database.db_master import DatabaseManager

class Product(NamedTuple):
    id: int
    name: str
    brand: Optional[str]
    sku: Optional[str]
    category: Optional[str]
    stock: int
    price: float
    image_path: Optional[str] = None

class ProductController: 
    """Pembungkus Data Product 
    
    method : add,get,edit,remove,fetch
    """
    def add(name: str, 
            price: float, 
            stock: int, 
            brand: str | None = None, 
            sku: str | None = None, 
            category: str | None = None,
            image_path: str | None = None
            ) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:# TYPE ERROR HANDLING
            price = float(price)
            stock = int(stock)
        except (ValueError, TypeError):
            raise TypeError("Failed to add product: 'price' must be a number and 'stock' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "INSERT INTO Product (Name, Brand, SKU, Category, Stock, Price, ImagePath) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, brand, sku, category, stock, price, image_path),
        )
        conn.commit()

    def get(product_id: int) -> Product | None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try:# TYPE ERROR HANDLING
            product_id = int(product_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to get product: 'product_id' must be an integer.")

        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Product WHERE ID = ?", (product_id,))
        row = cursor.fetchone()
        return Product(*row) if row else None

    def edit(product_id: int, 
             name: str, 
             brand: str | None, 
             stock: int, 
             price: float, 
             sku: str | None = None, 
             category: str | None = None,
             image_path: str | None = None
            ) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        """
        try: # TYPE ERROR HANDLING
            product_id = int(product_id)
            stock = int(stock)
            price = float(price)
        except (ValueError, TypeError):
            raise TypeError("Failed to edit product: 'product_id' and 'stock' must be integers, and 'price' must be a number.")

        conn, cursor = DatabaseManager.require_connection()
        cursor.execute(
            "UPDATE Product SET Name = ?, Brand = ?, SKU = ?, Category = ?, Stock = ?, Price = ?, ImagePath = ? WHERE ID = ?",
            (name, brand, sku, category, stock, price, image_path, product_id),
        )
        conn.commit()
    
    def remove(product_id: int) -> None:
        """Ada Error Handling type nya, nanti dia bakal raise TypeError kalau salah.
        
        Jika produk memiliki referensi di SalesDetail atau PurchaseDetail, akan raise ValueError.
        """
        try:# TYPE ERROR HANDLING
            product_id = int(product_id)
        except (ValueError, TypeError):
            raise TypeError("Failed to remove product: 'product_id' must be an integer.")

        conn, cursor = DatabaseManager.require_connection()
        
        # Check jika ada SalesDetail yang referensi product ini
        cursor.execute("SELECT COUNT(*) FROM SalesDetail WHERE ProductID = ?", (product_id,))
        sales_count = cursor.fetchone()[0]
        
        # Check jika ada PurchaseDetail yang referensi product ini
        cursor.execute("SELECT COUNT(*) FROM PurchaseDetail WHERE ProductID = ?", (product_id,))
        purchase_count = cursor.fetchone()[0]
        
        if sales_count > 0 or purchase_count > 0:
            raise ValueError(
                f"Produk tidak bisa dihapus karena sudah memiliki {sales_count} transaksi penjualan "
                f"dan {purchase_count} transaksi pembelian. Hapus transaksi terkait terlebih dahulu."
            )
        
        cursor.execute("DELETE FROM Product WHERE ID = ?", (product_id,))
        conn.commit()
        
    
    def fetch() -> list[Product] :
        """Bakal **SEMUA** semua data product dalam bentuk list of Product."""
        _, cursor = DatabaseManager.require_connection()
        cursor.execute("SELECT * FROM Product")
        rows = cursor.fetchall()
        return [Product(*row) for row in rows]
    