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
        ("Indomie Goreng",       "Indomie",          "MKN-001", "Makanan",  180,  3500, 25),
        ("Nasi Goreng Spesial",  "Warung Nusantara", "MKN-002", "Makanan",   42, 18000, 14),
        ("Ayam Geprek",          "GeprekZone",       "MKN-003", "Makanan",   35, 22000, 12),
        ("Air Mineral 600ml",    "AquaFresh",        "MNM-001", "Minuman",  220,  4000, 28),
        ("Es Teh Manis",         "Fresh Drink",      "MNM-002", "Minuman",  160,  5000, 24),
        ("Kopi Susu Gula Aren",  "CoffeeDaily",      "MNM-003", "Minuman",   55, 18000, 10),
        ("Keripik Singkong",     "SnackRasa",        "SNK-001", "Snack",      9,  8000,  7),
        ("Biskuit Coklat",       "Crunchy",          "SNK-002", "Snack",     75, 12000,  9),
        ("Wafer Keju",           "Cheezy",           "SNK-003", "Snack",     95, 10000, 11),
        ("Beras Premium 5Kg",    "PanenMakmur",      "SMB-001", "Sembako",   24, 78000,  5),
        ("Minyak Goreng 1L",     "Tropis",           "SMB-002", "Sembako",   16, 21000,  7),
        ("Telur Ayam 1Kg",       "FarmFresh",        "SMB-003", "Sembako",   10, 29000,  6),
        ("Sabun Cuci Piring",    "CleanMax",         "LNY-001", "Lainnya",   33, 14000,  4),
        ("Tisu Gulung",          "SoftCare",         "LNY-002", "Lainnya",   60, 11000,  4),
        ("Sambal Botol Pedas",   "HotTaste",         "LNY-003", "Lainnya",    8, 17000,  3),
    ]
    product_map: dict[int, dict] = {}
    for name, brand, sku, cat, stock, price, weight in rows:
        pid = _get_or_create_product(name, brand, sku, cat, stock, price)
        product_map[pid] = {"name": name, "price": int(price), "weight": int(weight)}
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
    (2026,  5): 5,   # Mei 2026 termasuk hari ini
}

TODAY_TX_COUNT = 5   # Transaksi wajib hari ini


def _build_sale_dates(transaction_count: int) -> list[datetime]:
    """
    Bangun list datetime transaksi:
    - TODAY_TX_COUNT transaksi hari ini (jam siang–sore)
    - Sisa tersebar per bulan sesuai _MONTHLY_QUOTA
    - Total tidak melebihi transaction_count
    """
    now = datetime.now()
    today = now.date()
    dates: list[datetime] = []

    # 1. Transaksi hari ini — jam bervariasi agar chart harian tidak menumpuk
    today_hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    for h in random.sample(today_hours, k=min(TODAY_TX_COUNT, len(today_hours))):
        dates.append(datetime(
            today.year, today.month, today.day,
            h, random.randint(0, 59), random.randint(0, 59),
        ))

    # 2. Transaksi per bulan dari quota
    for (year, month), quota in _MONTHLY_QUOTA.items():
        # Hitung hari valid dalam bulan itu (tidak boleh melebihi hari ini)
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

    # Sebaran purchase: 1–2 per bulan dari Jan 2025 s/d sekarang
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