from __future__ import annotations

import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from database.db_master import DatabaseManager

from controllers.user import UserController
from controllers.customer import CustomerController
from controllers.product import ProductController
from controllers.sales import SalesController
from controllers.sales_detail import SalesDetailController
from controllers.supplier import SupplierController
from controllers.purchase import PurchaseController
from controllers.purchase_detail import PurchaseDetailController
from controllers.receivables import ReceivablesController


# ============================================================
# Generate Data Dummy Warung+ - Scope Jan 2025 s/d Hari Ini
# ============================================================
# Data yang dibuat:
# - 100 transaksi sales, tersebar Jan 2025 – hari ini
#   * Variasi volume per bulan agar filter bulanan terlihat berbeda
#   * Selalu ada transaksi hari ini untuk cek moving average harian
# - Purchase ~10 transaksi tersebar 2025–2026
# ============================================================

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH: Path | None = None
ENV_DB_PATH = "WARUNG_DB_PATH"

SALES_TRANSACTION_COUNT = 100
PURCHASE_COUNT = 10
RESET_TRANSACTION_DATA = True


def _resolve_database_path() -> Path:
    env_path = os.environ.get(ENV_DB_PATH)
    if env_path:
        path = Path(env_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if path.exists():
            return path.resolve()
        raise FileNotFoundError(f"Database dari {ENV_DB_PATH} tidak ditemukan: {path}")

    if DB_PATH is not None:
        path = DB_PATH
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if path.exists():
            return path.resolve()
        raise FileNotFoundError(f"Database dari DB_PATH tidak ditemukan: {path}")

    candidates: list[Path] = []
    search_dirs = [PROJECT_ROOT / "database", PROJECT_ROOT]
    patterns = ["*.db", "*.sqlite", "*.sqlite3"]

    for directory in search_dirs:
        if not directory.exists():
            continue
        for pattern in patterns:
            candidates.extend(directory.glob(pattern))

    candidates = [
        p for p in candidates
        if p.is_file() and not p.name.startswith(".") and p.stat().st_size > 0
    ]

    if not candidates:
        raise FileNotFoundError(
            "File database tidak ditemukan. Set WARUNG_DB_PATH atau letakkan .db di folder database/."
        )

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0].resolve()


def connect_database() -> Path:
    db_path = _resolve_database_path()
    if not DatabaseManager.isConected():
        DatabaseManager(str(db_path))
    print(f"Database connected: {db_path}")
    return db_path


def _get_or_create_user(name: str, pin: str, role: int) -> int:
    users = UserController.fetch()
    for user_id, user_name, user_role in users:
        if str(user_name).lower() == name.lower():
            return int(user_id)
    UserController.add(name=name, pin=pin, role=role)
    users = UserController.fetch()
    for user_id, user_name, user_role in users:
        if str(user_name).lower() == name.lower():
            return int(user_id)
    raise RuntimeError(f"Gagal membuat user {name}")


def _get_or_create_customer(name: str, phone: str) -> int:
    existing = CustomerController.get_by_phone(phone)
    if existing:
        return int(existing.id)
    return int(CustomerController.add(name=name, phone=phone))


def _get_or_create_supplier(name: str, phone: str, address: str) -> int:
    suppliers = SupplierController.fetch()
    for s in suppliers:
        if str(s.name).lower() == name.lower():
            return int(s.id)
    SupplierController.add(name=name, phone=phone, address=address)
    suppliers = SupplierController.fetch()
    for s in suppliers:
        if str(s.name).lower() == name.lower():
            return int(s.id)
    raise RuntimeError(f"Gagal membuat supplier {name}")


def _get_or_create_product(name, brand, sku, category, stock, price) -> int:
    products = ProductController.fetch()
    for p in products:
        if (p.sku or "").lower() == sku.lower():
            ProductController.edit(
                product_id=p.id, name=name, brand=brand,
                stock=stock, price=price, sku=sku,
                category=category, image_path=p.image_path,
            )
            return int(p.id)
    ProductController.add(name=name, brand=brand, sku=sku, category=category, stock=stock, price=price)
    products = ProductController.fetch()
    for p in products:
        if (p.sku or "").lower() == sku.lower():
            return int(p.id)
    raise RuntimeError(f"Gagal membuat produk {name}")


def _ensure_base_users() -> dict[str, int]:
    return {
        "admin":   _get_or_create_user("Edward",     "123456", 1),
        "kasir_1": _get_or_create_user("Budi Kasir", "111111", 2),
        "kasir_2": _get_or_create_user("Siti Kasir", "222222", 2),
    }


def _ensure_customers() -> list[int]:
    customers = [
        ("Andi Saputra",  "081234567801"),
        ("Rina Amelia",   "081234567802"),
        ("Joko Prasetyo", "081234567803"),
        ("Dewi Lestari",  "081234567804"),
        ("Agus Setiawan", "081234567805"),
        ("Maya Putri",    "081234567806"),
    ]
    return [_get_or_create_customer(n, p) for n, p in customers]


def _ensure_suppliers() -> list[int]:
    suppliers = [
        ("CV Sumber Sembako", "0274000001", "Jl. Kaliurang No. 12"),
        ("PT Minuman Segar",  "0274000002", "Jl. Magelang No. 25"),
        ("Snack Nusantara",   "0274000003", "Jl. Solo No. 40"),
    ]
    return [_get_or_create_supplier(n, p, a) for n, p, a in suppliers]


def _ensure_products() -> dict[int, dict]:
    rows = [
        ("Indomie Goreng", "Indomie", "MKN-001", "Makanan", 180, 3500, 25),
        ("Indomie Soto", "Indomie", "MKN-002", "Makanan", 160, 3500, 22),
        ("Indomie Ayam Bawang", "Indomie", "MKN-003", "Makanan", 150, 3500, 20),
        ("Mie Sedaap Goreng", "Mie Sedaap", "MKN-004", "Makanan", 150, 3500, 20),
        ("Mie Sedaap Soto", "Mie Sedaap", "MKN-005", "Makanan", 120, 3500, 18),
        ("Sarimi Isi 2 Ayam Bawang", "Sarimi", "MKN-006", "Makanan", 90, 4500, 14),
        ("Supermi Ayam Bawang", "Supermi", "MKN-007", "Makanan", 90, 3500, 12),
        ("Bihun Jagung", "Padamu", "MKN-008", "Makanan", 45, 6500, 7),
        ("Mie Telur 200gr", "Cap 3 Ayam", "MKN-009", "Makanan", 45, 7000, 7),
        ("Sarden Kaleng Kecil", "ABC", "MKN-010", "Makanan", 30, 11500, 5),
        ("Sarden Kaleng Besar", "ABC", "MKN-011", "Makanan", 20, 21000, 4),
        ("Kornet Kaleng Kecil", "Pronas", "MKN-012", "Makanan", 22, 14500, 3),
        ("Abon Sapi Sachet", "BonCabe", "MKN-013", "Makanan", 35, 5000, 4),
        ("Bubur Instan Sachet", "Super Bubur", "MKN-014", "Makanan", 50, 3500, 6),
        ("Agar-Agar Bubuk", "Swallow", "MKN-015", "Makanan", 40, 5000, 4),
        ("Jelly Bubuk", "Nutrijell", "MKN-016", "Makanan", 45, 4500, 5),
        ("Susu Kental Manis Sachet", "Frisian Flag", "MKN-017", "Makanan", 100, 1500, 10),
        ("Susu Kental Manis Kaleng", "Frisian Flag", "MKN-018", "Makanan", 25, 13000, 4),
        ("Roti Tawar Kering Kemasan", "Sari Roti", "MKN-019", "Makanan", 25, 12000, 4),
        ("Meses Coklat Sachet", "Ceres", "MKN-020", "Makanan", 40, 3000, 4),

        ("Kopi Kapal Api Sachet", "Kapal Api", "MNM-001", "Minuman", 180, 1500, 25),
        ("Kopi ABC Susu Sachet", "ABC", "MNM-002", "Minuman", 160, 2000, 22),
        ("Kopi Good Day Cappuccino", "Good Day", "MNM-003", "Minuman", 120, 2500, 18),
        ("Kopi Luwak White Koffie", "Luwak", "MNM-004", "Minuman", 140, 2000, 20),
        ("Torabika Cappuccino Sachet", "Torabika", "MNM-005", "Minuman", 110, 2500, 16),
        ("Indocafe Coffeemix Sachet", "Indocafe", "MNM-006", "Minuman", 100, 2000, 15),
        ("Energen Coklat Sachet", "Energen", "MNM-007", "Minuman", 90, 2500, 12),
        ("Energen Vanila Sachet", "Energen", "MNM-008", "Minuman", 85, 2500, 12),
        ("Milo Sachet", "Milo", "MNM-009", "Minuman", 75, 3000, 10),
        ("Dancow Sachet", "Dancow", "MNM-010", "Minuman", 60, 4000, 8),
        ("Nutrisari Jeruk Sachet", "Nutrisari", "MNM-011", "Minuman", 130, 1500, 18),
        ("Nutrisari Mangga Sachet", "Nutrisari", "MNM-012", "Minuman", 120, 1500, 16),
        ("Marimas Jeruk Sachet", "Marimas", "MNM-013", "Minuman", 150, 1000, 20),
        ("Marimas Anggur Sachet", "Marimas", "MNM-014", "Minuman", 145, 1000, 18),
        ("Pop Ice Coklat Sachet", "Pop Ice", "MNM-015", "Minuman", 90, 1500, 12),
        ("Pop Ice Strawberry Sachet", "Pop Ice", "MNM-016", "Minuman", 90, 1500, 12),
        ("Teh Celup Isi 25", "Sariwangi", "MNM-017", "Minuman", 40, 9000, 7),
        ("Teh Celup Isi 30", "Sosro", "MNM-018", "Minuman", 35, 8500, 6),
        ("Air Mineral 600ml", "Aqua", "MNM-019", "Minuman", 120, 4000, 16),
        ("Air Mineral 1.5L", "Aqua", "MNM-020", "Minuman", 70, 7000, 10),

        ("Biskuit Roma Kelapa", "Roma", "SNK-001", "Snack", 70, 8500, 12),
        ("Biskuit Roma Malkist", "Roma", "SNK-002", "Snack", 65, 9000, 10),
        ("Biskuit Khong Guan", "Khong Guan", "SNK-003", "Snack", 40, 13000, 6),
        ("Wafer Tango Coklat", "Tango", "SNK-004", "Snack", 75, 10000, 10),
        ("Wafer Nabati Keju", "Nabati", "SNK-005", "Snack", 90, 2500, 15),
        ("Wafer Nabati Coklat", "Nabati", "SNK-006", "Snack", 90, 2500, 15),
        ("Chitato Sapi Panggang", "Chitato", "SNK-007", "Snack", 35, 12000, 5),
        ("Qtela Singkong", "Qtela", "SNK-008", "Snack", 45, 9000, 6),
        ("Taro Net", "Taro", "SNK-009", "Snack", 50, 7000, 7),
        ("Momogi Jagung Bakar", "Momogi", "SNK-010", "Snack", 80, 1000, 14),
        ("Kacang Garuda", "Garuda", "SNK-011", "Snack", 60, 2500, 10),
        ("Kacang Dua Kelinci", "Dua Kelinci", "SNK-012", "Snack", 55, 3000, 9),
        ("Permen Kopiko", "Kopiko", "SNK-013", "Snack", 100, 1000, 12),
        ("Permen Relaxa", "Relaxa", "SNK-014", "Snack", 90, 1000, 10),
        ("Coklat SilverQueen Mini", "SilverQueen", "SNK-015", "Snack", 35, 7000, 5),
        ("Chocolatos Wafer Roll", "Chocolatos", "SNK-016", "Snack", 70, 2000, 12),
        ("Beng-Beng", "Mayora", "SNK-017", "Snack", 75, 2500, 12),
        ("Astor Mini", "Astor", "SNK-018", "Snack", 40, 8000, 5),
        ("Keripik Singkong Balado", "Kusuka", "SNK-019", "Snack", 35, 8500, 5),
        ("Kuaci Rebo", "Rebo", "SNK-020", "Snack", 50, 3000, 7),

        ("Beras Ramos 5kg", "Ramos", "SMB-001", "Sembako", 35, 72000, 18),
        ("Beras Pandan Wangi 5kg", "Pandan Wangi", "SMB-002", "Sembako", 28, 78000, 15),
        ("Beras Premium 10kg", "Makmur Jaya", "SMB-003", "Sembako", 20, 145000, 10),
        ("Gula Pasir 1kg", "Gulaku", "SMB-004", "Sembako", 60, 17500, 20),
        ("Gula Pasir 500gr", "Gulaku", "SMB-005", "Sembako", 45, 9500, 12),
        ("Minyak Goreng 1L", "Sania", "SMB-006", "Sembako", 50, 18500, 18),
        ("Minyak Goreng 2L", "Sania", "SMB-007", "Sembako", 35, 36000, 14),
        ("Minyak Goreng 1L", "Bimoli", "SMB-008", "Sembako", 40, 20000, 12),
        ("Tepung Terigu 1kg", "Segitiga Biru", "SMB-009", "Sembako", 38, 14500, 10),
        ("Tepung Terigu 500gr", "Segitiga Biru", "SMB-010", "Sembako", 32, 8000, 8),
        ("Garam Dapur 250gr", "Refina", "SMB-011", "Sembako", 70, 4000, 10),
        ("Garam Dapur 500gr", "Refina", "SMB-012", "Sembako", 50, 7000, 8),
        ("Kecap Manis Sachet", "Bango", "SMB-013", "Sembako", 120, 1500, 18),
        ("Kecap Manis Botol 275ml", "Bango", "SMB-014", "Sembako", 30, 18000, 8),
        ("Saus Sambal Sachet", "ABC", "SMB-015", "Sembako", 130, 1000, 16),
        ("Saus Sambal Botol 275ml", "ABC", "SMB-016", "Sembako", 28, 16000, 7),
        ("Penyedap Rasa Sachet", "Masako", "SMB-017", "Sembako", 160, 1000, 18),
        ("Penyedap Rasa Sachet", "Royco", "SMB-018", "Sembako", 150, 1000, 18),
        ("Merica Bubuk Sachet", "Ladaku", "SMB-019", "Sembako", 80, 1500, 8),
        ("Santan Instan 65ml", "Kara", "SMB-020", "Sembako", 55, 4500, 8),

        ("Sabun Mandi Batang", "Lifebuoy", "LNY-001", "Lainnya", 55, 4500, 8),
        ("Sabun Mandi Batang", "Lux", "LNY-002", "Lainnya", 45, 5000, 7),
        ("Shampoo Sachet", "Sunsilk", "LNY-003", "Lainnya", 150, 1000, 18),
        ("Shampoo Sachet", "Clear", "LNY-004", "Lainnya", 130, 1000, 16),
        ("Pasta Gigi 75gr", "Pepsodent", "LNY-005", "Lainnya", 40, 9500, 7),
        ("Sikat Gigi Dewasa", "Formula", "LNY-006", "Lainnya", 35, 6000, 4),
        ("Detergen Bubuk Sachet", "Rinso", "LNY-007", "Lainnya", 120, 2000, 18),
        ("Detergen Bubuk Sachet", "Daia", "LNY-008", "Lainnya", 110, 1500, 16),
        ("Sabun Cuci Piring Sachet", "Sunlight", "LNY-009", "Lainnya", 140, 1000, 18),
        ("Sabun Cuci Piring 210ml", "Sunlight", "LNY-010", "Lainnya", 45, 6000, 8),
        ("Pewangi Pakaian Sachet", "Molto", "LNY-011", "Lainnya", 100, 1000, 12),
        ("Pewangi Pakaian Sachet", "Downy", "LNY-012", "Lainnya", 90, 1500, 10),
        ("Tisu Gulung", "Nice", "LNY-013", "Lainnya", 50, 5000, 6),
        ("Korek Api Gas", "Tokai", "LNY-014", "Lainnya", 80, 3000, 8),
        ("Lilin Putih Isi 6", "Cap Gajah", "LNY-015", "Lainnya", 45, 8000, 4),
        ("Baterai AA Isi 2", "ABC", "LNY-016", "Lainnya", 40, 9000, 5),
        ("Lampu LED 5 Watt", "Philips", "LNY-017", "Lainnya", 20, 18000, 3),
        ("Pulpen Biru", "Standard", "LNY-018", "Lainnya", 50, 3000, 3),
        ("Buku Tulis 38 Lembar", "Sidu", "LNY-019", "Lainnya", 40, 5000, 3),
        ("Obat Nyamuk Bakar", "Baygon", "LNY-020", "Lainnya", 45, 5000, 4),
    ]

    product_map: dict[int, dict] = {}

    for name, brand, sku, cat, stock, price, weight in rows:
        pid = _get_or_create_product(name, brand, sku, cat, stock, price)
        product_map[pid] = {
            "name": name,
            "price": int(price),
            "weight": int(weight),
        }

    print(f"  Products generated/updated: {len(product_map)}")
    return product_map


def _clear_transaction_data_if_requested():
    if not RESET_TRANSACTION_DATA:
        return
    print("RESET_TRANSACTION_DATA=True, membersihkan data lama...")
    for r in ReceivablesController.fetch():
        ReceivablesController.remove(r.id)
    for d in SalesDetailController.fetch():
        SalesDetailController.remove(d.id)
    for s in SalesController.fetch():
        SalesController.remove(s.id)
    for d in PurchaseDetailController.fetch():
        PurchaseDetailController.remove(d.id)
    for p in PurchaseController.fetch():
        PurchaseController.remove(p.id)
    print("Data lama berhasil dihapus.")


def _sales_exists() -> bool:
    return len(SalesController.fetch()) > 0


def _purchases_exist() -> bool:
    return len(PurchaseController.fetch()) > 0


def _pick_products_for_sale(product_map: dict[int, dict]) -> list[tuple[int, int, int]]:
    product_ids = list(product_map.keys())
    weights = [product_map[pid]["weight"] for pid in product_ids]
    item_count = random.randint(1, 4)
    picked_ids = random.choices(product_ids, weights=weights, k=item_count)
    qty_by_product: dict[int, int] = {}
    for pid in picked_ids:
        qty_by_product[pid] = qty_by_product.get(pid, 0) + random.randint(1, 2)
    return [
        (pid, qty, random.choice([0, 0, 0, 1000, 2000]))
        for pid, qty in qty_by_product.items()
    ]


# ------------------------------------------------------------------
# Distribusi transaksi: Jan 2025 – hari ini, variasi per bulan
# ------------------------------------------------------------------
# Kuota per bulan (total ~100):
#   Jan–Mar 2025  : 3–5 tx/bulan  (sepi awal tahun)
#   Apr–Jun 2025  : 6–8 tx/bulan  (mulai ramai)
#   Jul–Sep 2025  : 8–10 tx/bulan (puncak)
#   Okt–Des 2025  : 5–7 tx/bulan  (turun akhir tahun)
#   Jan–Apr 2026  : 4–6 tx/bulan  (awal tahun baru)
#   Hari ini      : 5 tx tetap     (wajib untuk pengecekan)
# ------------------------------------------------------------------

_MONTHLY_QUOTA = {
    (2025,  1): 4,
    (2025,  2): 3,
    (2025,  3): 5,
    (2025,  4): 6,
    (2025,  5): 7,
    (2025,  6): 8,
    (2025,  7): 9,
    (2025,  8): 10,
    (2025,  9): 9,
    (2025, 10): 6,
    (2025, 11): 5,
    (2025, 12): 7,
    (2026,  1): 5,
    (2026,  2): 4,
    (2026,  3): 5,
    (2026,  4): 6,
    (2026,  5): 5,
}

TODAY_TX_COUNT = 5


def _build_sale_dates(transaction_count: int) -> list[datetime]:
    now = datetime.now()
    today = now.date()
    dates: list[datetime] = []

    today_hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    for h in random.sample(today_hours, k=min(TODAY_TX_COUNT, len(today_hours))):
        dates.append(datetime(
            today.year, today.month, today.day,
            h, random.randint(0, 59), random.randint(0, 59),
        ))

    for (year, month), quota in _MONTHLY_QUOTA.items():
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        month_start = datetime(year, month, 1)
        month_end = datetime(year, month, last_day, 23, 59, 59)

        # Potong kalau bulan berjalan
        if month_end.date() >= today:
            month_end = datetime(today.year, today.month, today.day - 1, 23, 59, 59) \
                if today.day > 1 else month_start  # hindari duplikat hari ini
            if month_end < month_start:
                continue  # bulan ini hanya ada hari ini, skip (sudah diisi di atas)

        for _ in range(quota):
            delta_seconds = int((month_end - month_start).total_seconds())
            if delta_seconds <= 0:
                continue
            rand_seconds = random.randint(0, delta_seconds)
            tx_time = month_start + timedelta(seconds=rand_seconds)
            # Batasi jam operasional warung 08:00–21:00
            tx_time = tx_time.replace(
                hour=random.choice([8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20]),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
            )
            dates.append(tx_time)

        if len(dates) >= transaction_count:
            break

    random.shuffle(dates)
    return dates[:transaction_count]


def _generate_sales(user_ids, customer_ids, product_map, transaction_count=SALES_TRANSACTION_COUNT):
    if _sales_exists():
        print("Data Sales sudah ada, skip. Set RESET_TRANSACTION_DATA=True untuk reset.")
        return

    cashier_ids = [user_ids["admin"], user_ids["kasir_1"], user_ids["kasir_2"]]
    payment_methods = ["tunai", "qris"]
    sale_dates = _build_sale_dates(transaction_count)

    print(f"  Generating {len(sale_dates)} transaksi sales...")

    for sale_time in sale_dates:
        payment = random.choices(payment_methods, weights=[60, 40], k=1)[0]
        is_hutang = random.choices([True, False], weights=[10, 90], k=1)[0]
        customer_id: Optional[int] = random.choice(customer_ids) if is_hutang \
            else random.choice([None, None, *customer_ids])

        cart_items = _pick_products_for_sale(product_map)
        subtotal = sum(product_map[pid]["price"] * qty for pid, qty, _ in cart_items)
        total_discount = sum(disc for _, _, disc in cart_items)
        total_price = max(0, subtotal - total_discount)

        paid_amount = (
            random.choice([0, int(total_price * 0.5)])
            if is_hutang else total_price
        )

        sale_id = SalesController.add_return_id(
            customer_id=customer_id,
            cashier_id=random.choice(cashier_ids),
            time=sale_time.strftime("%Y-%m-%d %H:%M:%S"),
            payment=payment,
            paid_amount=paid_amount,
            total_price=total_price,
        )

        for product_id, quantity, discount in cart_items:
            SalesDetailController.add(
                sales_id=sale_id,
                product_id=product_id,
                quantity=quantity,
                discount=discount,
            )

        if is_hutang and customer_id is not None:
            status = "paid" if paid_amount >= total_price else "unpaid"
            due_date = (sale_time + timedelta(days=random.choice([7, 14, 30]))).strftime("%Y-%m-%d")
            ReceivablesController.add(
                sales_id=sale_id,
                customer_id=customer_id,
                total_amount=total_price,
                due_date=due_date,
                amount_paid=paid_amount,
                status=status,
            )


def _get_latest_purchase_id() -> int:
    purchases = PurchaseController.fetch()
    if not purchases:
        raise RuntimeError("Purchase gagal dibuat.")
    return max(int(p.id) for p in purchases)


def _generate_purchases(user_ids, supplier_ids, product_map, purchase_count=PURCHASE_COUNT):
    if _purchases_exist():
        print("Data Purchases sudah ada, skip. Set RESET_TRANSACTION_DATA=True untuk reset.")
        return

    product_ids = list(product_map.keys())
    now = datetime.now()

    import calendar
    purchase_months = list(_MONTHLY_QUOTA.keys())[:purchase_count]

    for (year, month) in purchase_months:
        last_day = calendar.monthrange(year, month)[1]
        day = random.randint(1, last_day)
        try:
            purchase_time = datetime(year, month, day,
                                     random.randint(7, 15),
                                     random.randint(0, 59),
                                     random.randint(0, 59))
        except ValueError:
            continue
        if purchase_time > now:
            purchase_time = now.replace(hour=9, minute=0, second=0)

        before_ids = {int(p.id) for p in PurchaseController.fetch()}
        PurchaseController.add(
            supplier_id=random.choice(supplier_ids),
            user_id=random.choice([user_ids["admin"], user_ids["kasir_1"]]),
            time=purchase_time.strftime("%Y-%m-%d %H:%M:%S"),
            total_amount=0,
        )
        after_ids = {int(p.id) for p in PurchaseController.fetch()}
        new_ids = sorted(after_ids - before_ids)
        purchase_id = new_ids[-1] if new_ids else _get_latest_purchase_id()

        selected = random.sample(product_ids, k=min(random.randint(2, 4), len(product_ids)))
        for pid in selected:
            sell_price = product_map[pid]["price"]
            purchase_price = int(sell_price * random.uniform(0.55, 0.82))
            PurchaseDetailController.add(
                purchase_id=purchase_id,
                product_id=pid,
                quantity=random.randint(5, 30),
                purchase_price=purchase_price,
            )

        PurchaseDetailController.update_purchase_total(purchase_id)


def generate_data():
    print("=" * 50)
    print("Generate data dummy Warung+ (2025–2026)")
    print(f"Target sales   : {SALES_TRANSACTION_COUNT} transaksi")
    print(f"Target purchase: {PURCHASE_COUNT} pembelian")
    print(f"Transaksi hari ini: {TODAY_TX_COUNT} (wajib)")
    print("=" * 50)

    _clear_transaction_data_if_requested()

    user_ids     = _ensure_base_users()
    customer_ids = _ensure_customers()
    supplier_ids = _ensure_suppliers()
    product_map  = _ensure_products()

    _generate_sales(user_ids, customer_ids, product_map, SALES_TRANSACTION_COUNT)
    _generate_purchases(user_ids, supplier_ids, product_map, PURCHASE_COUNT)

    print("\nRingkasan data setelah generate:")
    print(f"  Users      : {len(UserController.fetch())}")
    print(f"  Customers  : {len(CustomerController.fetch())}")
    print(f"  Suppliers  : {len(SupplierController.fetch())}")
    print(f"  Products   : {len(ProductController.fetch())}")
    print(f"  Sales      : {len(SalesController.fetch())}")
    print(f"  Details    : {len(SalesDetailController.fetch())}")
    print(f"  Receivable : {len(ReceivablesController.fetch())}")
    print(f"  Purchases  : {len(PurchaseController.fetch())}")
    print("\nDone.")


if __name__ == "__main__":
    try:
        connect_database()
        generate_data()
    finally:
        DatabaseManager.close()