from database import db_master


def get_sales_data():
    conn, cursor = db_master.require_connection()

    cursor.execute("""
        SELECT 
            DATE(s.Time) AS sale_date,
            SUM(p.Price * sd.Quantity - COALESCE(sd.Discount, 0)) AS total_sales
        FROM Sales s
        JOIN SalesDetail sd ON s.ID = sd.SalesID
        JOIN Product p ON sd.ProductID = p.ID
        GROUP BY DATE(s.Time)
        ORDER BY sale_date ASC
    """)

    return cursor.fetchall()


def calculate_moving_average(days=7):
    sales_data = get_sales_data()

    if not sales_data:
        return {
            "status": "empty",
            "message": "Belum ada data penjualan.",
            "daily_sales": [],
            "moving_average": 0,
            "prediction": 0
        }

    recent_data = sales_data[-days:]

    total_sales = sum(row[1] for row in recent_data)
    moving_average = total_sales / len(recent_data)

    return {
        "status": "success",
        "daily_sales": recent_data,
        "moving_average": moving_average,
        "prediction": moving_average,
        "message": f"Prediksi penjualan berikutnya berdasarkan {len(recent_data)} hari terakhir."
    }


def generate_sales_insight(days=7):
    result = calculate_moving_average(days)

    if result["status"] == "empty":
        return result["message"]

    prediction = result["prediction"]

    return (
        f"Berdasarkan rata-rata penjualan {len(result['daily_sales'])} hari terakhir, "
        f"prediksi omzet penjualan berikutnya adalah sekitar Rp{prediction:,.0f}."
    ).replace(",", ".")


if __name__ == "__main__":
    print(get_sales_data())
    print(calculate_moving_average(7))
    print(generate_sales_insight(7))