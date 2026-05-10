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
# Generate Data Dummy Warung+ - Scope 1 Bulan Terakhir
# ============================================================
# Tujuan:
# - Mengisi data dummy untuk mengetes Dashboard secara spesifik.
# - Fokus pada 1 bulan terakhir agar filter harian, mingguan, dan bulanan
#   mudah dicek.
# - Tetap menggunakan controller yang sudah ada.
# - Tidak menjalankan ulang SQL schema.
# - Tidak mengubah controller.
#
# Data yang dibuat:
# - Users admin/kasir
# - Customer
# - Supplier
# - Produk lengkap kategori/stok/harga
# - Sales 30 hari terakhir, termasuk transaksi hari ini
# - SalesDetail
# - Receivables untuk sebagian transaksi hutang
# - Purchases + PurchaseDetail 30 hari terakhir
#
# Cara pakai:
#   py .\generateData.py
#
# Jika database tidak otomatis ditemukan:
#   $env:WARUNG_DB_PATH="database\nama_database_kamu.db"
#   py .\generateData.py
#
# Jika sebelumnya kamu sudah generate data 120 hari dan ingin reset transaksi:
#   ubah RESET_TRANSACTION_DATA = True, lalu jalankan script ini sekali.
# ============================================================


RANDOM_SEED = 42
random.seed(RANDOM_SEED)

PROJECT_ROOT = Path(__file__).resolve().parent

# Kalau auto-detect salah, isi manual di sini:
# DB_PATH = PROJECT_ROOT / "database" / "nama_database_kamu.db"
DB_PATH: Path | None = None

ENV_DB_PATH = "WARUNG_DB_PATH"

# Scope data dashboard.
GENERATE_DAYS = 30
SALES_TRANSACTION_COUNT = 180
PURCHASE_COUNT = 16

# Aman default: tidak menghapus transaksi lama.
# Set True hanya kalau ingin membersihkan data transaksi lama dari hasil dummy sebelumnya.
RESET_TRANSACTION_DATA = False


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
        path for path in candidates
        if path.is_file()
        and not path.name.startswith(".")
        and path.stat().st_size > 0
    ]

    if not candidates:
        raise FileNotFoundError(
            "File database tidak ditemukan. Letakkan file .db/.sqlite di folder database/root project, "
            "atau set WARUNG_DB_PATH."
        )

    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
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
    for supplier in suppliers:
        if str(supplier.name).lower() == name.lower():
            return int(supplier.id)

    SupplierController.add(name=name, phone=phone, address=address)

    suppliers = SupplierController.fetch()
    for supplier in suppliers:
        if str(supplier.name).lower() == name.lower():
            return int(supplier.id)

    raise RuntimeError(f"Gagal membuat supplier {name}")


def _get_or_create_product(
    name: str,
    brand: str,
    sku: str,
    category: str,
    stock: int,
    price: float,
) -> int:
    products = ProductController.fetch()

    for product in products:
        if (product.sku or "").lower() == sku.lower():
            ProductController.edit(
                product_id=product.id,
                name=name,
                brand=brand,
                stock=stock,
                price=price,
                sku=sku,
                category=category,
                image_path=product.image_path,
            )
            return int(product.id)

    ProductController.add(
        name=name,
        brand=brand,
        sku=sku,
        category=category,
        stock=stock,
        price=price,
    )

    products = ProductController.fetch()
    for product in products:
        if (product.sku or "").lower() == sku.lower():
            return int(product.id)

    raise RuntimeError(f"Gagal membuat produk {name}")


def _ensure_base_users() -> dict[str, int]:
    return {
        "admin": _get_or_create_user("Edward", "123456", 1),
        "kasir_1": _get_or_create_user("Budi Kasir", "111111", 2),
        "kasir_2": _get_or_create_user("Siti Kasir", "222222", 2),
    }


def _ensure_customers() -> list[int]:
    customers = [
        ("Andi Saputra", "081234567801"),
        ("Rina Amelia", "081234567802"),
        ("Joko Prasetyo", "081234567803"),
        ("Dewi Lestari", "081234567804"),
        ("Agus Setiawan", "081234567805"),
        ("Maya Putri", "081234567806"),
        ("Tono Wijaya", "081234567807"),
        ("Nadia Zahra", "081234567808"),
    ]

    return [_get_or_create_customer(name, phone) for name, phone in customers]


def _ensure_suppliers() -> list[int]:
    suppliers = [
        ("CV Sumber Sembako", "0274000001", "Jl. Kaliurang No. 12"),
        ("PT Minuman Segar", "0274000002", "Jl. Magelang No. 25"),
        ("Snack Nusantara", "0274000003", "Jl. Solo No. 40"),
        ("Distributor Harian", "0274000004", "Jl. Bantul No. 18"),
    ]

    return [_get_or_create_supplier(name, phone, address) for name, phone, address in suppliers]


def _ensure_products() -> dict[int, dict]:
    product_rows = [
        # Makanan
        ("Indomie Goreng", "Indomie", "MKN-001", "Makanan", 180, 3500, 25),
        ("Indomie Ayam Bawang", "Indomie", "MKN-002", "Makanan", 140, 3500, 20),
        ("Nasi Goreng Spesial", "Warung Nusantara", "MKN-003", "Makanan", 42, 18000, 14),
        ("Ayam Geprek", "GeprekZone", "MKN-004", "Makanan", 35, 22000, 12),
        ("Mie Goreng Telur", "MieKu", "MKN-005", "Makanan", 18, 15000, 8),

        # Minuman
        ("Air Mineral 600ml", "AquaFresh", "MNM-001", "Minuman", 220, 4000, 28),
        ("Es Teh Manis", "Fresh Drink", "MNM-002", "Minuman", 160, 5000, 24),
        ("Kopi Susu Gula Aren", "CoffeeDaily", "MNM-003", "Minuman", 55, 18000, 10),
        ("Susu Coklat Botol", "MilkyDay", "MNM-004", "Minuman", 44, 9000, 8),
        ("Jus Jeruk Segar", "FruitPress", "MNM-005", "Minuman", 12, 12000, 5),

        # Snack
        ("Keripik Singkong", "SnackRasa", "SNK-001", "Snack", 9, 8000, 7),
        ("Biskuit Coklat", "Crunchy", "SNK-002", "Snack", 75, 12000, 9),
        ("Wafer Keju", "Cheezy", "SNK-003", "Snack", 95, 10000, 11),
        ("Roti Bakar Coklat", "BakeHouse", "SNK-004", "Snack", 0, 15000, 2),
        ("Permen Mint", "Minty", "SNK-005", "Snack", 5, 2000, 2),

        # Sembako
        ("Beras Premium 5Kg", "PanenMakmur", "SMB-001", "Sembako", 24, 78000, 5),
        ("Minyak Goreng 1L", "Tropis", "SMB-002", "Sembako", 16, 21000, 7),
        ("Telur Ayam 1Kg", "FarmFresh", "SMB-003", "Sembako", 10, 29000, 6),
        ("Gula Pasir 1Kg", "SweetSugar", "SMB-004", "Sembako", 6, 16000, 6),
        ("Tepung Terigu 1Kg", "BakePro", "SMB-005", "Sembako", 4, 13000, 3),

        # Lainnya
        ("Sabun Cuci Piring", "CleanMax", "LNY-001", "Lainnya", 33, 14000, 4),
        ("Tisu Gulung", "SoftCare", "LNY-002", "Lainnya", 60, 11000, 4),
        ("Sambal Botol Pedas", "HotTaste", "LNY-003", "Lainnya", 8, 17000, 3),
        ("Korek Api", "ApiJaya", "LNY-004", "Lainnya", 2, 3000, 1),
        ("Kantong Plastik", "PackGo", "LNY-005", "Lainnya", 0, 500, 1),
    ]

    product_map: dict[int, dict] = {}

    for name, brand, sku, category, stock, price, weight in product_rows:
        product_id = _get_or_create_product(
            name=name,
            brand=brand,
            sku=sku,
            category=category,
            stock=stock,
            price=price,
        )
        product_map[product_id] = {
            "name": name,
            "price": int(price),
            "weight": int(weight),
        }

    return product_map


def _clear_transaction_data_if_requested():
    if not RESET_TRANSACTION_DATA:
        return

    print("RESET_TRANSACTION_DATA=True, membersihkan data transaksi dan pembelian...")

    # Urutan penting: detail/piutang dulu, header terakhir.
    for receivable in ReceivablesController.fetch():
        ReceivablesController.remove(receivable.id)

    for detail in SalesDetailController.fetch():
        SalesDetailController.remove(detail.id)

    for sale in SalesController.fetch():
        SalesController.remove(sale.id)

    for detail in PurchaseDetailController.fetch():
        PurchaseDetailController.remove(detail.id)

    for purchase in PurchaseController.fetch():
        PurchaseController.remove(purchase.id)

    print("Data transaksi dan pembelian lama berhasil dibersihkan.")


def _sales_exists() -> bool:
    return len(SalesController.fetch()) > 0


def _purchases_exist() -> bool:
    return len(PurchaseController.fetch()) > 0


def _pick_products_for_sale(product_map: dict[int, dict]) -> list[tuple[int, int, int]]:
    product_ids = list(product_map.keys())
    weights = [product_map[pid]["weight"] for pid in product_ids]

    item_count = random.randint(1, 5)
    picked_ids = random.choices(product_ids, weights=weights, k=item_count)

    qty_by_product: dict[int, int] = {}
    for pid in picked_ids:
        qty_by_product[pid] = qty_by_product.get(pid, 0) + random.randint(1, 3)

    result: list[tuple[int, int, int]] = []
    for pid, qty in qty_by_product.items():
        discount = random.choice([0, 0, 0, 0, 1000, 2000, 5000])
        result.append((pid, qty, discount))

    return result


def _build_sale_dates(transaction_count: int) -> list[datetime]:
    """
    Membuat tanggal transaksi hanya dalam 30 hari terakhir.

    Komposisi:
    - Ada transaksi hari ini untuk filter daily.
    - Ada transaksi setiap hari dalam 7 hari terakhir untuk cek mingguan/7 hari.
    - Ada transaksi tersebar dalam 30 hari terakhir untuk cek bulanan.
    """
    now = datetime.now()
    dates: list[datetime] = []

    # 12 transaksi hari ini agar chart harian tidak kosong.
    for _ in range(12):
        dates.append(now.replace(
            hour=random.choice([8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20]),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            microsecond=0,
        ))

    # Pastikan 7 hari terakhir selalu punya transaksi.
    for day_ago in range(0, 7):
        transactions_per_day = random.randint(3, 7)
        base_day = now - timedelta(days=day_ago)
        for _ in range(transactions_per_day):
            dates.append(base_day.replace(
                hour=random.choice([8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20]),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
                microsecond=0,
            ))

    # Sisa transaksi disebar ke 30 hari terakhir.
    while len(dates) < transaction_count:
        day_ago = random.randint(0, GENERATE_DAYS - 1)
        base_day = now - timedelta(days=day_ago)
        dates.append(base_day.replace(
            hour=random.choice([8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20]),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            microsecond=0,
        ))

    random.shuffle(dates)
    return dates[:transaction_count]


def _generate_sales(
    user_ids: dict[str, int],
    customer_ids: list[int],
    product_map: dict[int, dict],
    transaction_count: int = SALES_TRANSACTION_COUNT,
):
    if _sales_exists():
        print("Data Sales sudah ada, skip generate transaksi agar tidak duplikat.")
        print("Jika ingin mengganti data lama menjadi scope 1 bulan, set RESET_TRANSACTION_DATA=True.")
        return

    cashier_ids = [user_ids["admin"], user_ids["kasir_1"], user_ids["kasir_2"]]
    payment_methods = ["cash", "qris", "transfer", "hutang"]
    sale_dates = _build_sale_dates(transaction_count)

    for sale_time in sale_dates:
        payment = random.choices(
            population=payment_methods,
            weights=[50, 25, 15, 10],
            k=1,
        )[0]

        if payment == "hutang":
            customer_id: Optional[int] = random.choice(customer_ids)
        else:
            customer_id = random.choice([None, None, None, *customer_ids])

        cart_items = _pick_products_for_sale(product_map)

        subtotal = 0
        total_discount = 0
        for product_id, quantity, discount in cart_items:
            subtotal += product_map[product_id]["price"] * quantity
            total_discount += discount

        total_price = max(0, subtotal - total_discount)

        if payment == "hutang":
            paid_amount = random.choice([0, int(total_price * 0.25), int(total_price * 0.5)])
        else:
            paid_amount = total_price

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

        if payment == "hutang" and customer_id is not None:
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


def _generate_purchases(
    user_ids: dict[str, int],
    supplier_ids: list[int],
    product_map: dict[int, dict],
    purchase_count: int = PURCHASE_COUNT,
):
    if _purchases_exist():
        print("Data Purchases sudah ada, skip generate pembelian agar tidak duplikat.")
        print("Jika ingin mengganti data lama menjadi scope 1 bulan, set RESET_TRANSACTION_DATA=True.")
        return

    product_ids = list(product_map.keys())
    now = datetime.now()

    for _ in range(purchase_count):
        before_ids = {int(p.id) for p in PurchaseController.fetch()}

        day_ago = random.randint(0, GENERATE_DAYS - 1)
        base_day = now - timedelta(days=day_ago)
        purchase_time = base_day.replace(
            hour=random.randint(7, 16),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
            microsecond=0,
        )

        PurchaseController.add(
            supplier_id=random.choice(supplier_ids),
            user_id=random.choice([user_ids["admin"], user_ids["kasir_1"]]),
            time=purchase_time.strftime("%Y-%m-%d %H:%M:%S"),
            total_amount=0,
        )

        after_ids = {int(p.id) for p in PurchaseController.fetch()}
        new_ids = sorted(after_ids - before_ids)
        purchase_id = new_ids[-1] if new_ids else _get_latest_purchase_id()

        item_count = random.randint(2, 6)
        selected_products = random.sample(product_ids, k=min(item_count, len(product_ids)))

        for product_id in selected_products:
            sell_price = product_map[product_id]["price"]
            purchase_price = int(sell_price * random.uniform(0.55, 0.82))
            quantity = random.randint(5, 40)

            PurchaseDetailController.add(
                purchase_id=purchase_id,
                product_id=product_id,
                quantity=quantity,
                purchase_price=purchase_price,
            )

        PurchaseDetailController.update_purchase_total(purchase_id)


def generate_data():
    print("Generate data dummy Warung+ dimulai...")
    print(f"Scope transaksi: {GENERATE_DAYS} hari terakhir")
    print(f"Target sales   : {SALES_TRANSACTION_COUNT}")
    print(f"Target purchase: {PURCHASE_COUNT}")

    _clear_transaction_data_if_requested()

    user_ids = _ensure_base_users()
    customer_ids = _ensure_customers()
    supplier_ids = _ensure_suppliers()
    product_map = _ensure_products()

    _generate_sales(
        user_ids=user_ids,
        customer_ids=customer_ids,
        product_map=product_map,
        transaction_count=SALES_TRANSACTION_COUNT,
    )

    _generate_purchases(
        user_ids=user_ids,
        supplier_ids=supplier_ids,
        product_map=product_map,
        purchase_count=PURCHASE_COUNT,
    )

    print("Data dummy berhasil digenerate.")
    print(f"- Users      : {len(UserController.fetch())}")
    print(f"- Customers  : {len(CustomerController.fetch())}")
    print(f"- Suppliers  : {len(SupplierController.fetch())}")
    print(f"- Products   : {len(ProductController.fetch())}")
    print(f"- Sales      : {len(SalesController.fetch())}")
    print(f"- Details    : {len(SalesDetailController.fetch())}")
    print(f"- Receivable : {len(ReceivablesController.fetch())}")
    print(f"- Purchases  : {len(PurchaseController.fetch())}")


if __name__ == "__main__":
    try:
        connect_database()
        generate_data()
    finally:
        DatabaseManager.close()
