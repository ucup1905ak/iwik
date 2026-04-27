import os
import sqlite3
import random
from datetime import datetime, timedelta

from api import db_master

def generate_data():
    conn, cursor = db_master.require_connection()

    # =========================
    # CASHIER
    # =========================
    cursor.execute("SELECT COUNT(*) FROM Cashier")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO Cashier (FirstName, LastName, Salary)
            VALUES (?, ?, ?)
        """, [
            ('Budi', 'Santoso', 3000000),
            ('Siti', 'Aminah', 2800000)
        ])

    # =========================
    # CUSTOMER
    # =========================
    cursor.execute("SELECT COUNT(*) FROM Customer")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO Customer (Name, Phone)
            VALUES (?, ?)
        """, [
            ('Andi', '08123456789'),
            ('Rina', '08234567890'),
            ('Joko', '08345678901')
        ])

    # =========================
    # PRODUCT
    # =========================
    cursor.execute("SELECT COUNT(*) FROM Product")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO Product (Name, Brand, Stock, Price)
            VALUES (?, ?, ?, ?)
        """, [
            ('Indomie Goreng', 'Indomie', 100, 3500),
            ('Beras 5kg', 'Ramos', 50, 65000),
            ('Minyak Goreng 1L', 'Bimoli', 40, 18000),
            ('Gula 1kg', 'Gulaku', 30, 14000),
            ('Telur 1kg', 'Lokal', 25, 27000),
            ('Aqua 600ml', 'Aqua', 80, 4000)
        ])

    # =========================
    # SALES - Generate Random Data
    # =========================
    cursor.execute("SELECT COUNT(*) FROM Sales")
    if cursor.fetchone()[0] == 0:
        sales_data = []
        payment_methods = ['cash', 'qris', 'hutang', 'transfer']
        
        # Generate sales records untuk 90 hari terakhir dengan data random
        start_date = datetime.now() - timedelta(days=90)
        
        for i in range(500):  # Generate 500 transaksi
            random_date = start_date + timedelta(days=random.randint(0, 90), hours=random.randint(7, 20), minutes=random.randint(0, 59))
            
            customer_id = random.choice([None, None, None, 1, 2, 3])  # 50% tanpa customer
            cashier_id = random.choice([1, 2])
            payment = random.choice(payment_methods)
            paid_amount = random.randint(25000, 150000)
            
            sales_data.append((
                customer_id,
                cashier_id,
                random_date.strftime('%Y-%m-%d %H:%M:%S'),
                payment,
                paid_amount
            ))
        
        cursor.executemany("""
            INSERT INTO Sales (CustomerID, CashierID, Time, Payment, PaidAmount)
            VALUES (?, ?, ?, ?, ?)
        """, sales_data)

    # =========================
    # SALES DETAIL - Generate Random Data
    # =========================
    cursor.execute("SELECT COUNT(*) FROM SalesDetail")
    if cursor.fetchone()[0] == 0:
        # Get all sales IDs
        cursor.execute("SELECT ID FROM Sales")
        sales_ids = [row[0] for row in cursor.fetchall()]
        
        sales_detail_data = []
        product_ids = [1, 2, 3, 4, 5, 6]
        
        # Generate sales details untuk setiap sales record
        for sales_id in sales_ids:
            num_items = random.randint(1, 4)  # 1-4 items per transaksi
            
            for _ in range(num_items):
                product_id = random.choice(product_ids)
                quantity = random.randint(1, 10)
                discount = random.choice([0, 0, 0, 5000, 10000])  # Mostly no discount
                
                sales_detail_data.append((
                    sales_id,
                    product_id,
                    quantity,
                    discount
                ))
        
        cursor.executemany("""
            INSERT INTO SalesDetail (SalesID, ProductID, Quantity, Discount)
            VALUES (?, ?, ?, ?)
        """, sales_detail_data)

    conn.commit()
    print("✅ Data berhasil digenerate")

if __name__ == "__main__":
    generate_data()