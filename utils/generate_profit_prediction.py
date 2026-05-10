from __future__ import annotations

from database import db_master


Period = str


def _format_price(value: float | int | None) -> str:
    return f"Rp {float(value or 0):,.0f}".replace(",", ".")


def _period_config(period: Period) -> dict:
    """
    daily   -> prediksi omset hari berikutnya, basis data harian
    weekly  -> prediksi omset minggu berikutnya, basis data mingguan
    monthly -> prediksi omset bulan berikutnya, basis data bulanan
    """
    if period == "weekly":
        return {
            "group_expr": "strftime('%Y-%W', Time)",
            "label_expr": "strftime('%Y-W%W', Time)",
            "default_window": 4,
            "unit_label": "minggu",
            "target_label": "minggu berikutnya",
        }

    if period == "monthly":
        return {
            "group_expr": "strftime('%Y-%m', Time)",
            "label_expr": "strftime('%Y-%m', Time)",
            "default_window": 3,
            "unit_label": "bulan",
            "target_label": "bulan berikutnya",
        }

    return {
        "group_expr": "DATE(Time)",
        "label_expr": "DATE(Time)",
        "default_window": 7,
        "unit_label": "hari",
        "target_label": "hari berikutnya",
    }


def get_omset_data(period: Period = "daily") -> list[tuple[str, float]]:
    """
    Mengambil total omset berdasarkan periode.
    Menggunakan Sales.TotalPrice karena nilai ini adalah total final transaksi
    yang sudah disimpan dari halaman kasir.
    """
    cfg = _period_config(period)
    conn, cursor = db_master.require_connection()

    query = f"""
        SELECT
            {cfg["label_expr"]} AS period_label,
            SUM(COALESCE(TotalPrice, 0)) AS total_omset
        FROM Sales
        GROUP BY {cfg["group_expr"]}
        ORDER BY {cfg["group_expr"]} ASC
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    return [(str(row[0]), float(row[1] or 0)) for row in rows]


def calculate_moving_average_omset(period: Period = "daily", window: int | None = None) -> dict:
    """
    Prediksi omset sederhana menggunakan moving average.

    period:
        daily   -> rata-rata omset harian terakhir
        weekly  -> rata-rata omset mingguan terakhir
        monthly -> rata-rata omset bulanan terakhir

    window:
        Jika None, otomatis:
        daily   = 7 data terakhir
        weekly  = 4 data terakhir
        monthly = 3 data terakhir
    """
    cfg = _period_config(period)
    data = get_omset_data(period)

    if not data:
        return {
            "status": "empty",
            "period": period,
            "period_label": cfg["unit_label"],
            "target_label": cfg["target_label"],
            "data": [],
            "window": window or cfg["default_window"],
            "moving_average": 0,
            "prediction": 0,
            "trend_status": "empty",
            "trend_message": "Belum ada data penjualan untuk membuat prediksi omset.",
            "message": "Belum ada data penjualan.",
        }

    window_size = int(window or cfg["default_window"])
    recent_data = data[-window_size:]

    total_recent = sum(value for _, value in recent_data)
    moving_average = total_recent / len(recent_data)

    # Insight deskriptif sederhana:
    # bandingkan rata-rata data terbaru dengan rata-rata data sebelumnya.
    previous_data = data[-(window_size * 2):-window_size]

    trend_status = "neutral"
    trend_message = "Data penjualan masih terbatas. Prediksi akan lebih stabil setelah data bertambah."

    if previous_data:
        previous_avg = sum(value for _, value in previous_data) / len(previous_data)

        if previous_avg <= 0 and moving_average > 0:
            trend_status = "up"
            trend_message = "Omset mulai terbentuk karena periode sebelumnya belum memiliki penjualan."
        elif previous_avg > 0:
            diff_percent = ((moving_average - previous_avg) / previous_avg) * 100

            if diff_percent > 10:
                trend_status = "up"
                trend_message = f"Omset cenderung naik sekitar {diff_percent:.1f}% dibanding periode sebelumnya."
            elif diff_percent < -10:
                trend_status = "down"
                trend_message = f"Omset cenderung turun sekitar {abs(diff_percent):.1f}% dibanding periode sebelumnya."
            else:
                trend_status = "stable"
                trend_message = "Omset relatif stabil dibanding periode sebelumnya."

    return {
        "status": "success",
        "period": period,
        "period_label": cfg["unit_label"],
        "target_label": cfg["target_label"],
        "data": recent_data,
        "window": len(recent_data),
        "moving_average": moving_average,
        "prediction": moving_average,
        "trend_status": trend_status,
        "trend_message": trend_message,
        "message": (
            f"Prediksi omset {cfg['target_label']} berdasarkan rata-rata "
            f"{len(recent_data)} {cfg['unit_label']} terakhir."
        ),
    }


def generate_omset_insight(period: Period = "daily", window: int | None = None) -> str:
    result = calculate_moving_average_omset(period=period, window=window)

    if result["status"] == "empty":
        return result["message"]

    return (
        f"Berdasarkan rata-rata omset {result['window']} {result['period_label']} terakhir, "
        f"prediksi omset {result['target_label']} adalah sekitar "
        f"{_format_price(result['prediction'])}."
    )


if __name__ == "__main__":
    print(get_omset_data("daily"))
    print(calculate_moving_average_omset("daily"))
    print(generate_omset_insight("daily"))