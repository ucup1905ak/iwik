# gui/views/screens/sales_page.py

from datetime import datetime
from controllers.product import ProductController, Product
from controllers.sales import SalesController
from controllers.sales_detail import SalesDetailController
from controllers.customer import CustomerController
from controllers.receivables import ReceivablesController
from PyQt6.QtWidgets import (
    QSpacerItem,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QFrame,
    QGridLayout,
    QComboBox,
    QDialog,
    QGraphicsDropShadowEffect,
    QSizePolicy,
    QRadioButton,
    QButtonGroup,
    QPlainTextEdit,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPixmap, QFont, QIntValidator, QTextDocument
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from gui.views.components.toast import Toast
from gui.signals import product_signals, sales_signals
import os
from pathlib import Path

# ── Color palette ──────────────────────────────────────────────────────────────
C_BG       = "#F4F5F9"
C_WHITE    = "#FFFFFF"
C_ACCENT   = "#4F6EF7"
C_ACCENT_H = "#3A57E8"
C_TEXT_PRI = "#1A1D2E"
C_TEXT_SEC = "#6B6F80"
C_BORDER   = "#E4E6EE"
C_DANGER   = "#E05252"
C_SUCCESS  = "#27AE60"
C_TAG_BG   = "#EEF1FE"
C_TAG_TEXT = "#4F6EF7"

ENABLE_CARD_SHADOWS = False
RADIUS = 14

SAMPLE_CATEGORIES = ["Semua", "Makanan", "Minuman", "Snack", "Sembako", "Lainnya"]

CAT_THEME = {
    "Makanan": {"emoji": "🍽️", "bg": "#FFF4E8", "text": "#E67E22"},
    "Minuman": {"emoji": "🥤",  "bg": "#EAF7FF", "text": "#3498DB"},
    "Snack":   {"emoji": "🍿", "bg": "#FFF0F6", "text": "#E84393"},
    "Sembako": {"emoji": "🛒", "bg": "#EEFCEF", "text": "#27AE60"},
    "Lainnya": {"emoji": "📦", "bg": "#F1F3F8", "text": "#6C757D"},
}

C_ROW_ALT    = "#FAFBFF"
C_HEADER_BG  = "#FFFFFF"
C_HEADER_TEXT = "#9EA3B8"
C_DIVIDER    = "#F0F1F7"

# ── Card dimensions ────────────────────────────────────────────────────────────
CASHIER_CARD_WIDTH   = 320   # lebar minimum kolom grid
CASHIER_CARD_SPACING = 12

SAMPLE_PRODUCTS = [
    Product(id=1,  name="Nasi Goreng Spesial",   brand="Warung Nusantara", sku="MKN-001", category="Makanan", stock=10,  price=25000),
    Product(id=2,  name="Es Teh Manis",           brand="Fresh Drink",      sku="MNM-001", category="Minuman", stock=120, price=5000),
    Product(id=3,  name="Keripik Singkong",       brand="SnackRasa",        sku="SNK-001", category="Snack",   stock=1,   price=8000),
    Product(id=4,  name="Mie Goreng",             brand="MieKu",            sku="MKN-002", category="Makanan", stock=0,   price=20000),
    Product(id=5,  name="Ayam Geprek",            brand="GeprekZone",       sku="MKN-003", category="Makanan", stock=15,  price=22000),
    Product(id=6,  name="Kopi Susu Gula Aren",   brand="CoffeeDaily",      sku="MNM-002", category="Minuman", stock=45,  price=18000),
    Product(id=7,  name="Roti Bakar Coklat",     brand="BakeHouse",        sku="SNK-002", category="Snack",   stock=0,   price=15000),
    Product(id=8,  name="Beras Premium 5Kg",     brand="PanenMakmur",      sku="SMB-001", category="Sembako", stock=18,  price=78000),
    Product(id=9,  name="Minyak Goreng 1L",      brand="Tropis",           sku="SMB-002", category="Sembako", stock=40,  price=21000),
    Product(id=10, name="Air Mineral 600ml",      brand="AquaFresh",        sku="MNM-003", category="Minuman", stock=200, price=4000),
    Product(id=11, name="Susu Coklat Botol",     brand="MilkyDay",         sku="MNM-004", category="Minuman", stock=55,  price=9000),
    Product(id=12, name="Biskuit Coklat",        brand="Crunchy",          sku="SNK-003", category="Snack",   stock=70,  price=12000),
    Product(id=13, name="Indomie Ayam Bawang",   brand="Indomie",          sku="MKN-004", category="Makanan", stock=150, price=3500),
    Product(id=14, name="Telur Ayam 1Kg",        brand="FarmFresh",        sku="SMB-003", category="Sembako", stock=12,  price=29000),
    Product(id=15, name="Gula Pasir 1Kg",        brand="SweetSugar",       sku="SMB-004", category="Sembako", stock=25,  price=16000),
    Product(id=16, name="Jus Jeruk Segar",       brand="FruitPress",       sku="MNM-005", category="Minuman", stock=14,  price=12000),
    Product(id=17, name="Wafer Keju",            brand="Cheezy",           sku="SNK-004", category="Snack",   stock=90,  price=10000),
    Product(id=18, name="Sabun Cuci Piring",     brand="CleanMax",         sku="LNY-001", category="Lainnya", stock=33,  price=14000),
    Product(id=19, name="Tisu Gulung",           brand="SoftCare",         sku="LNY-002", category="Lainnya", stock=60,  price=11000),
    Product(id=20, name="Sambal Botol Pedas",    brand="HotTaste",         sku="LNY-003", category="Lainnya", stock=8,   price=17000),
]


def _cat_theme(category: str) -> dict:
    return CAT_THEME.get(category, {"emoji": "📦", "bg": "#F1F3F8", "text": "#6C757D"})


def _format_price(price: int) -> str:
    return f"Rp {price:,.0f}".replace(",", ".")


def _card_shadow() -> QGraphicsDropShadowEffect:
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(16)
    shadow.setOffset(0, 2)
    shadow.setColor(QColor(0, 0, 0, 18))
    return shadow


def _apply_card_shadow(widget: QWidget):
    if ENABLE_CARD_SHADOWS:
        widget.setGraphicsEffect(_card_shadow())
    else:
        widget.setGraphicsEffect(None)


def _cat_button_theme(category: str) -> dict:
    if category == "Semua":
        return {
            "active_bg":    C_ACCENT,
            "active_text":  "#FFFFFF",
            "inactive_bg":  C_WHITE,
            "inactive_text": C_TEXT_SEC,
            "hover_bg":     C_TAG_BG,
            "hover_text":   C_ACCENT,
            "border":       C_BORDER,
            "hover_border": C_ACCENT,
        }
    cat = _cat_theme(category)
    return {
        "active_bg":    cat["text"],
        "active_text":  "#FFFFFF",
        "inactive_bg":  C_WHITE,
        "inactive_text": cat["text"],
        "hover_bg":     cat["bg"],
        "hover_text":   cat["text"],
        "border":       cat["bg"],
        "hover_border": cat["text"],
    }


def _style_cat_btn(btn: QPushButton, cat: str, active: bool):
    t = _cat_button_theme(cat)
    if active:
        btn.setStyleSheet(f"""
            QPushButton {{
                background:    {t['active_bg']};
                color:         {t['active_text']};
                font-family:   'Segoe UI';
                font-size:     12px;
                font-weight:   700;
                border-radius: 10px;
                padding:       0 16px;
                border:        none;
            }}
        """)
    else:
        btn.setStyleSheet(f"""
            QPushButton {{
                background:    {t['inactive_bg']};
                color:         {t['inactive_text']};
                font-family:   'Segoe UI';
                font-size:     12px;
                font-weight:   600;
                border-radius: 10px;
                padding:       0 16px;
                border:        1px solid {t['border']};
            }}
            QPushButton:hover {{
                background: {t['hover_bg']};
                color:      {t['hover_text']};
                border:     1px solid {t['hover_border']};
            }}
            QPushButton:pressed {{
                padding-top: 1px;
            }}
        """)

# ═══════════════════════════════════════════════════════════════════════════════
# Cashier Product Card  –  horizontal compact layout
# ═══════════════════════════════════════════════════════════════════════════════
class CashierProductCard(QFrame):
    clicked = pyqtSignal(Product)
    CARD_WIDTH = CASHIER_CARD_WIDTH

    def __init__(self, product: Product, parent=None):
        super().__init__(parent)
        self._product = product
        self._build()

    def _build(self):
        product = self._product
        stock   = product.stock

        self.setObjectName("CashierProductCard")
        self.setFixedHeight(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet(f"""
            QFrame#CashierProductCard {{
                background: {C_WHITE};
                border-radius: 14px;
                border: 1.5px solid {C_BORDER};
            }}
            QFrame#CashierProductCard:hover {{
                border: 1.5px solid {C_ACCENT};
                background: #FAFBFF;
            }}
        """)
        _apply_card_shadow(self)

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)

        # ── Image (kiri) – only fixed width, height follows card ───────────
        img_container = QFrame()
        img_container.setFixedWidth(140)
        img_container.setStyleSheet(f"""
            QFrame {{
                background: #FFFFFF;
                border-radius: 10px;
                border: none;
            }}
        """)

        img_layout = QVBoxLayout(img_container)
        img_layout.setContentsMargins(4, 4, 4, 4)
        img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        img_label = QLabel()
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if product.image_path and os.path.exists(product.image_path):
            pixmap = QPixmap(product.image_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    130, 150,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                img_label.setPixmap(scaled)
            else:
                img_label.setText("📦")
                img_label.setStyleSheet(f"font-size: 40px; color: {C_TEXT_SEC};")
        else:
            img_label.setText("📦")
            img_label.setStyleSheet(f"font-size: 40px; color: {C_TEXT_SEC};")

        img_layout.addWidget(img_label)
        root.addWidget(img_container)

        # ── Info (kanan) ───────────────────────────────────────────────────
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        # ── Top row: category tag + stock badge ────────────────────────────
        top = QHBoxLayout()
        top.setSpacing(4)
        top.setContentsMargins(0, 0, 0, 0)
        cat = _cat_theme(product.category)

        cat_tag = QLabel(f"{cat['emoji']} {product.category}")
        cat_tag.setStyleSheet(f"""
            background:    {cat['bg']};
            color:         {cat['text']};
            font-family:   'Segoe UI';
            font-size:     10px;
            font-weight:   700;
            padding:       3px 8px;
            border-radius: 6px;
            border:        none;
        """)

        if stock == 0:
            sc, sb, st = "#E05252", "#FDEAEA", "Habis"
        elif stock < 20:
            sc, sb, st = "#E07D2A", "#FDF3EA", f"Sisa {stock}"
        else:
            sc, sb, st = "#27AE60", "#E8F8F0", f"Stok {stock}"

        stock_badge = QLabel(st)
        stock_badge.setStyleSheet(f"""
            background:    {sb};
            color:         {sc};
            font-family:   'Segoe UI';
            font-size:     10px;
            font-weight:   600;
            padding:       3px 8px;
            border-radius: 6px;
            border:        none;
        """)

        top.addWidget(cat_tag)
        top.addStretch()
        top.addWidget(stock_badge)
        info_layout.addLayout(top)

        # ── Nama produk ────────────────────────────────────────────────────
        name_lbl = QLabel(product.name)
        name_lbl.setWordWrap(True)
        name_lbl.setMaximumHeight(36)
        name_lbl.setStyleSheet(f"""
            font-family:  'Segoe UI';
            font-size:    13px;
            font-weight:  700;
            color:        {C_TEXT_PRI};
            background:   transparent;
            border:       none;
        """)
        info_layout.addWidget(name_lbl)

        # ── Brand ──────────────────────────────────────────────────────────
        if product.brand:
            brand_lbl = QLabel(f"Merek: {product.brand}")
            brand_lbl.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size:   10px;
                color:       {C_TEXT_SEC};
                background:  transparent;
                border:      none;
            """)
            info_layout.addWidget(brand_lbl)

        # ── SKU ────────────────────────────────────────────────────────────
        if product.sku:
            sku_lbl = QLabel(f"SKU: {product.sku}")
            sku_lbl.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size:   9px;
                color:       {C_TEXT_SEC};
                background:  transparent;
                border:      none;
            """)
            info_layout.addWidget(sku_lbl)

        info_layout.addStretch(1)

        # ── Bottom row: harga kiri, tombol tambah kanan ────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(8)
        bottom.setContentsMargins(0, 0, 0, 0)

        price_lbl = QLabel(_format_price(product.price))
        price_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   14px;
            font-weight: 700;
            color:       {C_ACCENT};
            background:  transparent;
            border:      none;
        """)

        

        bottom.addWidget(price_lbl)

        info_layout.addLayout(bottom)
        root.addWidget(info_container, stretch=1)

    def mousePressEvent(self, event):
        self.clicked.emit(self._product)
        super().mousePressEvent(event)


# ═══════════════════════════════════════════════════════════════════════════════
# Order Item Card  –  item di panel order kanan
# ═══════════════════════════════════════════════════════════════════════════════
class OrderItemCard(QFrame):
    remove_clicked = pyqtSignal(int)
    quantity_changed = pyqtSignal(int, int)

    def __init__(self, product: Product, quantity: int = 1, parent=None):
        super().__init__(parent)
        self._product = product
        self._quantity = quantity
        self._build()

    def _build(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 8px;
            }}
        """)
        # Fixed height agar semua item card sejajar
        self.setFixedHeight(64)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 0, 10, 0)
        root.setSpacing(8)

        # ── Info ───────────────────────────────────────────────────────────
        info = QVBoxLayout()
        info.setSpacing(2)
        info.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(self._product.name)
        name_lbl.setWordWrap(False)
        name_lbl.setFixedHeight(20)
        name_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 600;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        info.addWidget(name_lbl)

        price_lbl = QLabel(_format_price(self._product.price))
        price_lbl.setFixedHeight(16)
        price_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 10px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        info.addWidget(price_lbl)
        root.addLayout(info, stretch=1)

        # ── Qty control ────────────────────────────────────────────────────
        qty_frame = QFrame()
        qty_frame.setFixedHeight(30)
        qty_frame.setStyleSheet(f"""
            QFrame {{
                background: {C_TAG_BG};
                border-radius: 6px;
                border: none;
            }}
        """)
        qty_layout = QHBoxLayout(qty_frame)
        qty_layout.setContentsMargins(4, 0, 4, 0)
        qty_layout.setSpacing(2)

        minus_btn = QPushButton("−")
        minus_btn.setFixedSize(22, 22)
        minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        minus_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C_ACCENT};
                border: none;
                font-weight: 700;
                font-size: 14px;
            }}
        """)
        minus_btn.clicked.connect(self._on_minus)

        self._qty_lbl = QLineEdit(str(self._quantity))
        self._qty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qty_lbl.setFixedWidth(36)
        self._qty_lbl.setFixedHeight(22)
        self._qty_lbl.setValidator(QIntValidator(1, self._product.stock))
        self._qty_lbl.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self._qty_lbl.setStyleSheet(f"""
            QLineEdit {{
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: 600;
                color: {C_ACCENT};
                background: transparent;
                border: none;
                padding: 0;
            }}
        """)
        self._qty_lbl.textChanged.connect(self._on_qty_typed)
        self._qty_lbl.editingFinished.connect(self._on_qty_committed)

        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(22, 22)
        plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        plus_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C_ACCENT};
                border: none;
                font-weight: 700;
                font-size: 14px;
            }}
        """)
        plus_btn.clicked.connect(self._on_plus)

        qty_layout.addWidget(minus_btn)
        qty_layout.addWidget(self._qty_lbl)
        qty_layout.addWidget(plus_btn)
        root.addWidget(qty_frame)

        # ── Remove button ──────────────────────────────────────────────────
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(26, 26)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C_DANGER};
                border: 1px solid {C_DANGER};
                border-radius: 4px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{ background: #FEF0F0; }}
        """)
        remove_btn.clicked.connect(self._on_remove)
        root.addWidget(remove_btn)
        
    def _on_qty_typed(self, text: str):
        # Update internal quantity saat mengetik tapi belum commit
        if text and text.isdigit():
            val = int(text)
            if val >= 1:
                self._quantity = val
                self.quantity_changed.emit(self._product.id, self._quantity)

    def _on_qty_committed(self):
        # Saat focus hilang / Enter, validasi dan clamp ke stock
        text = self._qty_lbl.text().strip()
        if not text or not text.isdigit() or int(text) < 1:
            self._quantity = 1
        elif int(text) > self._product.stock:
            self._quantity = self._product.stock
            Toast.show_toast(
                f"Stok {self._product.name} hanya {self._product.stock} unit.",
                "warning",
                self.window()
            )
        else:
            self._quantity = int(text)

        self._qty_lbl.setText(str(self._quantity))
        self.quantity_changed.emit(self._product.id, self._quantity)

    def _on_minus(self):
        if self._quantity > 1:
            self._quantity -= 1
            self._qty_lbl.setText(str(self._quantity))
            self.quantity_changed.emit(self._product.id, self._quantity)

    def _on_plus(self):
        if self._quantity >= self._product.stock:
            Toast.show_toast(
                f"Stok {self._product.name} hanya {self._product.stock} unit.",
                "warning",
                self.window()
            )
            return
        self._quantity += 1
        self._qty_lbl.setText(str(self._quantity))
        self.quantity_changed.emit(self._product.id, self._quantity)

    def _on_remove(self):
        self.remove_clicked.emit(self._product.id)

    def get_quantity(self) -> int:
        return self._quantity

    def set_quantity(self, qty: int):
        self._quantity = qty
        self._qty_lbl.setText(str(self._quantity))


# ═══════════════════════════════════════════════════════════════════════════════
# Sales Page  –  Halaman Kasir
# ═══════════════════════════════════════════════════════════════════════════════
class SalesPage(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self._user = user
        self._products = []
        self._filtered_products = []
        self._cart = {}
        self._recent_products = {}
        self._active_category = "Semua"
        self._products_scroll = None

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C_BG};")

        self._build_ui()
        self._load_products()

        product_signals.product_added.connect(self._on_product_added)
        product_signals.product_edited.connect(self._on_product_edited)
        product_signals.product_deleted.connect(self._on_product_deleted)
        product_signals.product_stock_changed.connect(self._on_product_stock_changed)
        product_signals.products_imported.connect(self._on_products_imported)

    # ──────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        header = QVBoxLayout()
        header.setSpacing(4)
        header.setContentsMargins(0, 0, 0, 0)

        page_title = QLabel("Kasir")
        page_title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 24px;
            font-weight: 700;
            color: {C_TEXT_PRI};
            background: transparent;
        """)

        page_sub = QLabel("Proses transaksi penjualan dengan cepat dan akurat")
        page_sub.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 13px;
            color: {C_TEXT_SEC};
            background: transparent;
        """)

        header.addWidget(page_title)
        header.addWidget(page_sub)
        root.addLayout(header)
        root.addSpacing(20)

        # ── Main container (kiri + kanan) ────────────────────────────────────
        main_container = QHBoxLayout()
        main_container.setSpacing(16)
        main_container.setContentsMargins(0, 0, 0, 0)
        main_container.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ══════════════════════════════════════════════════════════════════════
        # LEFT  –  produk grid
        # ══════════════════════════════════════════════════════════════════════
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Search bar
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("🔍  Cari produk...")
        self._search_input.setFixedHeight(40)
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C_WHITE};
                border: 1.5px solid {C_BORDER};
                border-radius: 10px;
                padding: 0 14px;
                font-family: 'Segoe UI';
                font-size: 13px;
                color: {C_TEXT_PRI};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {C_ACCENT};
            }}
        """)
        self._search_input.textChanged.connect(self._on_search)
        left_layout.addWidget(self._search_input)

        # Category buttons
        cat_frame = QFrame()
        cat_frame.setFixedHeight(38)
        cat_frame.setStyleSheet("background: transparent; border: none;")
        cat_layout = QHBoxLayout(cat_frame)
        cat_layout.setContentsMargins(0, 0, 0, 0)
        cat_layout.setSpacing(8)
        cat_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self._cat_buttons = {}
        for cat in SAMPLE_CATEGORIES:
            btn = QPushButton(cat)
            btn.setFixedHeight(34)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda checked, c=cat: self._set_category(c))
            cat_layout.addWidget(btn)
            self._cat_buttons[cat] = btn

        cat_layout.addStretch()
        left_layout.addWidget(cat_frame)
        left_layout.addSpacing(4)

        # Products scroll area
        self._products_scroll = QScrollArea()
        self._products_scroll.setWidgetResizable(True)
        self._products_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._products_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._products_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._products_scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin: 6px 2px 6px 0;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {C_BORDER};
                border-radius: 3px;
                min-height: 24px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #B8BCCE;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        products_widget = QWidget()
        products_widget.setStyleSheet("background: transparent;")
        self._products_grid = QGridLayout(products_widget)
        self._products_grid.setSpacing(CASHIER_CARD_SPACING)
        self._products_grid.setContentsMargins(0, 0, 0, 0)
        self._products_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self._products_scroll.setWidget(products_widget)
        left_layout.addWidget(self._products_scroll, stretch=1)

        main_container.addLayout(left_layout, stretch=1)

        # ══════════════════════════════════════════════════════════════════════
        # RIGHT  –  order summary panel
        # ══════════════════════════════════════════════════════════════════════
        summary_frame = QFrame()
        summary_frame.setFixedWidth(340)
        summary_frame.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        summary_frame.setStyleSheet(f"""
            QFrame {{
                background: {C_WHITE};
                border-radius: 14px;
                border: 1.5px solid {C_BORDER};
            }}
        """)

        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(10)
        # Tidak pakai AlignTop — biarkan stretch mengatur ruang

        # Panel title
        title = QLabel("Order")
        title.setFixedHeight(24)
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 15px;
            font-weight: 700;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        summary_layout.addWidget(title)

        # Order items scroll  –  stretch=1 agar menyerap sisa ruang
        scroll_items = QScrollArea()
        scroll_items.setWidgetResizable(True)
        scroll_items.setMinimumHeight(80)   # minimal saat cart kosong
        scroll_items.setFrameShape(QFrame.Shape.NoFrame)
        scroll_items.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {C_BORDER};
                border-radius: 2px;
                min-height: 20px;
            }}
        """)

        items_widget = QWidget()
        items_widget.setStyleSheet("background: transparent;")
        self._items_layout = QVBoxLayout(items_widget)
        self._items_layout.setSpacing(6)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._items_layout.addStretch()

        scroll_items.setWidget(items_widget)
        # stretch=1 → area item menyerap ruang bebas, mendorong footer ke bawah
        summary_layout.addWidget(scroll_items, stretch=1)

        # ── Footer block (subtotal → diskon → total → button) ─────────────
        # Seluruh blok ini tidak punya stretch, sehingga selalu menempel
        # tepat di bawah area item dan tidak ada jarak ekstra.

        # Divider atas footer
        summary_layout.addWidget(self._make_divider())

        # Subtotal
        self._subtotal_value = QLabel("Rp 0")
        self._subtotal_value.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            font-weight: 600;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        summary_layout.addLayout(
            self._make_summary_row("Subtotal", self._subtotal_value, secondary=True)
        )

        # Diskon label + inputs dalam satu blok rapat
        discount_label = QLabel("Diskon")
        discount_label.setFixedHeight(18)
        discount_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            font-weight: 500;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        summary_layout.addWidget(discount_label)

        discount_row = QHBoxLayout()
        discount_row.setSpacing(8)
        discount_row.setContentsMargins(0, 0, 0, 0)

        self._discount_type = QComboBox()
        self._discount_type.addItem("Rp")
        self._discount_type.addItem("%")
        self._discount_type.setFixedSize(58, 34)
        self._discount_type.setStyleSheet(f"""
            QComboBox {{
                background:    {C_TAG_BG};
                color:         {C_ACCENT};
                border:        1px solid {C_BORDER};
                border-radius: 6px;
                font-family:   'Segoe UI';
                font-size:     11px;
                font-weight:   600;
                padding:       0 4px 0 8px;
            }}
            QComboBox::drop-down {{
                border:  none;
                width:   24px;
            }}
            QComboBox::down-arrow {{
                width:  8px;
                height: 8px;
            }}
            QComboBox QAbstractItemView {{
                background:                {C_WHITE};
                border:                    1px solid {C_BORDER};
                border-radius:             0px;
                padding:                   2px;
                outline:                   none;
                color:                     {C_ACCENT};
                font-family:               'Segoe UI';
                font-size:                 11px;
                selection-background-color: {C_TAG_BG};
                selection-color:            {C_ACCENT};
            }}
            QComboBox QAbstractItemView::item {{
                height:        28px;
                padding-left:  8px;
                border-radius: 0px;
                color:         {C_ACCENT};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background:    {C_TAG_BG};
                color:         {C_ACCENT};
                border-radius: 0px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background:    {C_TAG_BG};
                color:         {C_ACCENT};
                border-radius: 0px;
            }}
        """)

        arrow_lbl = QLabel("⌄", self._discount_type)
        arrow_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 18px; font-weight: 600;
            color: {C_TEXT_SEC}; background: transparent; border: none;
        """)
        arrow_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        QTimer.singleShot(0, lambda: arrow_lbl.setGeometry(
            self._discount_type.width() - 28, -8, 24, 40
        ))

        self._discount_type.currentTextChanged.connect(self._on_discount_changed)

        self._discount_input = QLineEdit()
        self._discount_input.setPlaceholderText("0")
        self._discount_input.setFixedHeight(34)
        self._discount_input.setValidator(QIntValidator(0, 999_999_999))  # ← tambahkan ini
        self._discount_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C_TAG_BG};
                border: 1px solid {C_BORDER};
                border-radius: 6px;
                font-family: 'Segoe UI';
                font-size: 11px;
                padding: 0 10px;
                color: {C_TEXT_PRI};
            }}
            QLineEdit:focus {{
                border: 1px solid {C_ACCENT};
            }}
        """)
        self._discount_input.textChanged.connect(self._on_discount_changed)

        discount_row.addWidget(self._discount_type)
        discount_row.addWidget(self._discount_input)
        summary_layout.addLayout(discount_row)

        # Potongan
        self._discount_value = QLabel("Rp 0")
        self._discount_value.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            font-weight: 600;
            color: {C_DANGER};
            background: transparent;
            border: none;
        """)
        summary_layout.addLayout(
            self._make_summary_row("Potongan", self._discount_value, secondary=True)
        )

        # Divider sebelum total
        summary_layout.addWidget(self._make_divider())

        # Total
        self._total_value = QLabel("Rp 0")
        self._total_value.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 14px;
            font-weight: 700;
            color: {C_ACCENT};
            background: transparent;
            border: none;
        """)
        total_row = QHBoxLayout()
        total_row.setContentsMargins(0, 0, 0, 0)
        total_lbl = QLabel("Total")
        total_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 13px;
            font-weight: 700;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        total_row.addWidget(total_lbl)
        total_row.addStretch()
        total_row.addWidget(self._total_value)
        summary_layout.addLayout(total_row)

        # Tombol Proses Order – langsung di bawah total, tanpa spacing tambahan
        order_btn = QPushButton("Proses Order")
        order_btn.setFixedHeight(42)
        order_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        order_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT};
                color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
                border-radius: 8px;
                border: none;
            }}
            QPushButton:hover {{
                background: {C_ACCENT_H};
            }}
            QPushButton:pressed {{
                background: #2F4CD9;
            }}
        """)
        order_btn.clicked.connect(self._on_order_clicked)
        summary_layout.addWidget(order_btn)

        main_container.addWidget(summary_frame)
        root.addLayout(main_container, stretch=1)

        self._set_category("Semua")

    # ── Helper: buat divider ───────────────────────────────────────────────────
    def _make_divider(self) -> QFrame:
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {C_BORDER}; border: none;")
        return div

    # ── Helper: buat baris label + value ──────────────────────────────────────
    def _make_summary_row(self, label_text: str, value_widget: QLabel, secondary: bool = False) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label_text)
        lbl.setFixedHeight(18)
        lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            color: {C_TEXT_SEC if secondary else C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        value_widget.setFixedHeight(18)
        if secondary and not value_widget.styleSheet():
            value_widget.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
                color: {C_TEXT_PRI};
                background: transparent;
                border: none;
            """)
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(value_widget)
        return row
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._refresh_products_grid)

    # ── Load products ──────────────────────────────────────────────────────────
    def _load_products(self):
        try:
            self._products = ProductController.fetch()
            # self._products = SAMPLE_PRODUCTS;
            self._filtered_products = self._products
            # Defer ke next event loop tick agar viewport sudah punya ukuran yang benar
            QTimer.singleShot(0, self._refresh_products_grid)
        except Exception as e:
            Toast.show_toast(f"Error loading products: {str(e)}", "error", self)

    # ── Category ───────────────────────────────────────────────────────────────
    def _set_category(self, category: str):
        self._active_category = category
        for cat, btn in self._cat_buttons.items():
            _style_cat_btn(btn, cat, cat == category)
        self._filter_products()

    def _on_search(self):
        self._filter_products()

    def _filter_products(self):
        query = self._search_input.text().lower()
        self._filtered_products = [
            p for p in self._products
            if (self._active_category == "Semua" or p.category == self._active_category)
            and (query == "" or query in p.name.lower() or query in (p.brand or "").lower())
        ]
        self._refresh_products_grid()

    # ── Grid helpers ───────────────────────────────────────────────────────────
    def _get_product_column_count(self) -> int:
        if not self._products_scroll:
            return 2
        available = self._products_scroll.viewport().width()
        if available <= 0:
            # Fallback saat widget belum selesai di-render
            available = self._products_scroll.width() - 20
        if available <= 0:
            return 2
        cols = max(1, available // (CASHIER_CARD_WIDTH + CASHIER_CARD_SPACING))
        return cols

    def _clear_products_grid(self):
        while self._products_grid.count():
            item = self._products_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _refresh_products_grid(self):
        self._clear_products_grid()

        if not self._filtered_products:
            empty_label = QLabel("📦  Tidak ada produk")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size: 14px;
                color: {C_TEXT_SEC};
                padding: 40px;
                background: transparent;
            """)
            self._products_grid.addWidget(empty_label, 0, 0)
            return

        cols = self._get_product_column_count()

        for idx, product in enumerate(self._filtered_products):
            card = CashierProductCard(product)
            card.clicked.connect(lambda p, prod=product: self._add_to_cart(prod))
            row = idx // cols
            col = idx % cols
            self._products_grid.addWidget(card, row, col)

        # Semua kolom dapat stretch yang sama → lebar merata
        for col_idx in range(cols):
            self._products_grid.setColumnStretch(col_idx, 1)

    # ── Cart logic ─────────────────────────────────────────────────────────────
    def _add_to_cart(self, product: Product):
        if product.stock <= 0:
            Toast.show_toast("Produk habis.", "warning", self)
            return

        if product.id in self._cart:
            existing_product, qty = self._cart[product.id]
            if qty >= product.stock:
                Toast.show_toast(
                    f"Jumlah {product.name} sudah mencapai batas stok ({product.stock}).",
                    "warning", self
                )
                return
            self._cart[product.id] = (product, qty + 1)
        else:
            self._cart[product.id] = (product, 1)

        self._recent_products[product.id] = self._recent_products.get(product.id, 0) + 1
        self._refresh_cart_display()

    def _refresh_cart_display(self):
        # Hapus semua item kecuali stretch di akhir
        while self._items_layout.count() > 1:
            item = self._items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for product_id, (product, quantity) in self._cart.items():
            item_card = OrderItemCard(product, quantity)
            item_card.remove_clicked.connect(self._remove_from_cart)
            item_card.quantity_changed.connect(self._on_quantity_changed)
            self._items_layout.insertWidget(self._items_layout.count() - 1, item_card)

        self._update_totals()

    def _on_quantity_changed(self, product_id: int, new_quantity: int):
        if product_id in self._cart:
            product, _ = self._cart[product_id]
            if new_quantity > product.stock:
                Toast.show_toast(
                    f"Tidak bisa melebihi stok yang tersedia ({product.stock}).",
                    "warning", self
                )
                self._refresh_cart_display()
                return
            self._cart[product_id] = (product, new_quantity)
            self._update_totals()

    def _remove_from_cart(self, product_id: int):
        if product_id in self._cart:
            del self._cart[product_id]
            self._refresh_cart_display()

    def _on_discount_changed(self):
        self._update_totals()

    def _calculate_discount(self, subtotal: int) -> tuple:
        discount_str = self._discount_input.text().strip()
        if not discount_str or discount_str == "0":
            return 0, subtotal
        try:
            discount_val = float(discount_str)
        except ValueError:
            return 0, subtotal

        if self._discount_type.currentText() == "%":
            discount_amount = int(subtotal * discount_val / 100)
        else:
            discount_amount = int(discount_val)

        return discount_amount, max(0, subtotal - discount_amount)

    def _update_totals(self):
        subtotal = sum(product.price * qty for product, qty in self._cart.values())
        self._subtotal_value.setText(_format_price(subtotal))
        discount_amount, total = self._calculate_discount(subtotal)
        self._discount_value.setText(_format_price(discount_amount))
        self._total_value.setText(_format_price(total))

    # ── Order ──────────────────────────────────────────────────────────────────
    def _on_order_clicked(self):
        if not self._cart:
            Toast.show_toast("Keranjang kosong. Tambahkan produk terlebih dahulu.", "warning", self)
            return

        subtotal = sum(product.price * qty for product, qty in self._cart.values())
        discount_amount, total = self._calculate_discount(subtotal)

        dialog = OrderConfirmDialog(
            cart=self._cart,
            subtotal=subtotal,
            discount=discount_amount,
            total=total,
            user=self._user,
            parent=self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._process_order(
                total=total,
                discount=discount_amount,
                payment_method=dialog.payment_method,
                paid_amount=dialog.cash_given,
                buyer_name=dialog.buyer_name,
                receipt_path=dialog.receipt_path,
                payment_type=dialog._payment_type,
                customer_id=dialog.customer_id
            )

    def _process_order(self, total: int, discount: int, payment_method: str,
                       paid_amount: int, buyer_name: str = None, receipt_path: str = None,
                       payment_type: str = None, customer_id: int = None):
        try:
            fresh_products = {p.id: p for p in ProductController.fetch()}

            for product_id, (cart_product, quantity) in self._cart.items():
                fresh = fresh_products.get(product_id)
                if not fresh:
                    Toast.show_toast(f"Produk {cart_product.name} tidak ditemukan.", "error", self)
                    return
                if quantity > int(fresh.stock):
                    Toast.show_toast(f"Stok {fresh.name} tidak cukup. Sisa: {fresh.stock}.", "warning", self)
                    return

            # Hitung gross revenue (subtotal) = total + discount
            gross_revenue = total + discount
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sales_id = SalesController.add_return_id(
                customer_id=customer_id,
                cashier_id=self._user["id"],
                time=timestamp,
                payment=payment_method,
                paid_amount=paid_amount,
                total_price=gross_revenue   # ← Simpan gross revenue (subtotal)
            )

            updated_stocks = {}

            for product_id, (cart_product, quantity) in self._cart.items():
                fresh = fresh_products[product_id]
                fresh_stock = int(fresh.stock)

                SalesDetailController.add(
                    sales_id=sales_id,
                    product_id=product_id,
                    quantity=quantity,
                    discount=0  # diskon sudah diperhitungkan di total, tidak perlu per item
                )

                new_stock = fresh_stock - quantity
                updated_stocks[product_id] = new_stock

                ProductController.edit(
                    product_id=fresh.id,
                    name=fresh.name,
                    brand=fresh.brand,
                    stock=new_stock,
                    price=fresh.price,
                    sku=fresh.sku,
                    category=fresh.category,
                    image_path=fresh.image_path
                )

            # Save to Receivables if payment is hutang (credit)
            if payment_type == "hutang" and customer_id:
                ReceivablesController.add(
                    sales_id=sales_id,
                    customer_id=customer_id,
                    total_amount=gross_revenue,  # ← Gunakan gross revenue untuk piutang
                    due_date=None,
                    amount_paid=paid_amount,
                    status='unpaid',
                    payment_method='hutang'
                )

            Toast.show_toast("Order berhasil disimpan", "success", self)

            for product_id, new_stock in updated_stocks.items():
                product_signals.product_stock_changed.emit(product_id, new_stock)

            sales_signals.sales_completed.emit(sales_id)

            self._cart = {}
            self._discount_input.setText("0")
            self._products = ProductController.fetch()
            self._filter_products()
            self._refresh_cart_display()

        except Exception as e:
            Toast.show_toast(f"Error: {str(e)}", "error", self)

    # ── Signal handlers ────────────────────────────────────────────────────────
    def _on_product_added(self, product: Product):
        if product not in self._products:
            self._products.append(product)
            self._filter_products()

    def _on_product_edited(self, product: Product):
        for i, p in enumerate(self._products):
            if p.id == product.id:
                self._products[i] = product
                break
        self._filter_products()

    def _on_product_deleted(self, product_id: int):
        self._products = [p for p in self._products if p.id != product_id]
        if product_id in self._cart:
            del self._cart[product_id]
            self._refresh_cart_display()
        self._filter_products()

    def _on_product_stock_changed(self, product_id: int, new_stock: int):
        for i, p in enumerate(self._products):
            if p.id == product_id:
                from controllers.product import Product as ProductClass
                self._products[i] = ProductClass(
                    id=p.id, name=p.name, brand=p.brand, sku=p.sku,
                    category=p.category, price=p.price, stock=new_stock,
                    image_path=p.image_path
                )
                break
        self._filter_products()

    def _on_products_imported(self, products: list):
        for product in products:
            if product not in self._products:
                self._products.append(product)
        self._filter_products()


# ═══════════════════════════════════════════════════════════════════════════════
# Receipt Preview Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class ReceiptPreviewDialog(QDialog):
    def __init__(self, receipt_text: str, parent=None):
        super().__init__(parent)
        self._receipt_text = receipt_text
        self.action = "cancel"
        self.saved_path = None

        self.setWindowTitle("Preview Struk")
        self.setModal(True)
        self.setFixedWidth(400)
        self.setMaximumHeight(620)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Maximum)
        self.setStyleSheet(f"""
            QDialog {{
                background: #FAFAF8;
                font-family: 'Segoe UI';
            }}
        """)

        self._build_ui()
        self._adjust_height()

    def _adjust_height(self):
        lines = self._receipt_text.count("\n") + 1
        preview_height = min(max(lines * 13 + 60, 280), 420)
        self._receipt_view.setFixedHeight(preview_height)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("QFrame { background-color: #FAFAF8; }")
        header_lay = QVBoxLayout(header)
        header_lay.setContentsMargins(20, 18, 20, 0)
        header_lay.setSpacing(2)

        title = QLabel("Preview Struk")
        title.setStyleSheet("font-size:16px;font-weight:600;color:#1b1b1b;border:none;")
        header_lay.addWidget(title)

        subtitle = QLabel("Periksa struk sebelum menyimpan atau mencetak.")
        subtitle.setStyleSheet("font-size:11px;color:#888780;border:none;")
        header_lay.addWidget(subtitle)
        header_lay.addSpacing(14)
        root.addWidget(header)

        # Receipt paper
        content_frame = QFrame()
        content_frame.setStyleSheet("background: #FAFAF8;")
        content_lay = QVBoxLayout(content_frame)
        content_lay.setContentsMargins(0, 0, 0, 20)
        content_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        receipt_paper = QFrame()
        receipt_paper.setFixedWidth(320)
        receipt_paper.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border: 1px solid #DDD9D2;
                border-radius: 10px;
            }
        """)
        receipt_paper_lay = QVBoxLayout(receipt_paper)
        receipt_paper_lay.setContentsMargins(12, 12, 12, 12)
        receipt_paper_lay.setSpacing(0)

        self._receipt_view = QPlainTextEdit()
        self._receipt_view.setPlainText(self._receipt_text)
        self._receipt_view.setReadOnly(True)
        self._receipt_view.setFont(QFont("Consolas", 8))
        self._receipt_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._receipt_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._receipt_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._receipt_view.setStyleSheet(f"""
            QPlainTextEdit {{
                background: #FFFFFF;
                border: none;
                padding: 0;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 8px;
                color: {C_TEXT_PRI};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {C_BORDER};
                border-radius: 2px;
                min-height: 20px;
            }}
        """)
        receipt_paper_lay.addWidget(self._receipt_view)
        content_lay.addWidget(receipt_paper, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addWidget(content_frame, stretch=0)

        # Footer
        footer = QFrame()
        footer.setStyleSheet("QFrame { background-color: #FAFAF8; }")
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(20, 0, 20, 18)
        footer_lay.setSpacing(10)

        cancel_btn = QPushButton("Batal")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #5F5E5A;
                font-family: 'Segoe UI'; font-size: 12px; font-weight: 500;
                border-radius: 8px; border: 1px solid #DDD9D2;
            }
            QPushButton:hover { background: #F1EFE8; border: 1px solid #C8C6BF; }
        """)
        cancel_btn.clicked.connect(self._on_cancel)

        save_btn = QPushButton("Simpan")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #27AE60; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 12px; font-weight: 600;
                border-radius: 8px; border: none;
            }
            QPushButton:hover { background: #229954; }
        """)
        save_btn.clicked.connect(self._on_save)

        print_btn = QPushButton("Cetak")
        print_btn.setFixedHeight(40)
        print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        print_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 12px; font-weight: 600;
                border-radius: 8px; border: none;
            }}
            QPushButton:hover {{ background: {C_ACCENT_H}; }}
        """)
        print_btn.clicked.connect(self._on_print)

        footer_lay.addWidget(cancel_btn)
        footer_lay.addWidget(save_btn)
        footer_lay.addWidget(print_btn)
        root.addWidget(footer)

    def _on_cancel(self):
        self.action = "cancel"
        self.reject()

    def _on_save(self):
        try:
            project_root = Path(__file__).parent.parent.parent.parent
            receipts_dir = project_root / "assets" / "receipts"
            receipts_dir.mkdir(parents=True, exist_ok=True)
            receipt_file = receipts_dir / f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(receipt_file, 'w', encoding='utf-8') as f:
                f.write(self._receipt_text)
            self.action = "save"
            self.saved_path = str(receipt_file)
            Toast.show_toast("Struk disimpan", "success", self.parent())
            self.accept()
        except Exception as e:
            Toast.show_toast(f"Error menyimpan struk: {str(e)}", "error", self.parent())

    def _on_print(self):
        try:
            project_root = Path(__file__).parent.parent.parent.parent
            receipts_dir = project_root / "assets" / "receipts"
            receipts_dir.mkdir(parents=True, exist_ok=True)
            receipt_file = receipts_dir / f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(receipt_file, 'w', encoding='utf-8') as f:
                f.write(self._receipt_text)

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setPageSize(QPrinter.PageSize.A6)
            printer.setMargins(5, 5, 5, 5, QPrinter.Unit.Millimeter)
            printer.setOrientation(QPrinter.Orientation.Portrait)

            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec() == QDialog.DialogCode.Accepted:
                doc = QTextDocument()
                font = QFont("Consolas", 8)
                font.setFixedPitch(True)
                doc.setDefaultFont(font)
                html_text = "<pre style='margin:0;padding:0;font-size:8pt;font-family:Consolas,monospace;'>"
                for line in self._receipt_text.split('\n'):
                    html_text += line.replace(' ', '&nbsp;') + "<br/>"
                html_text += "</pre>"
                doc.setHtml(html_text)
                doc.print(printer)
                self.action = "print"
                self.saved_path = str(receipt_file)
                Toast.show_toast("Struk berhasil dicetak", "success", self.parent())
                self.accept()
        except Exception as e:
            Toast.show_toast(f"Error mencetak struk: {str(e)}", "error", self.parent())


# ═══════════════════════════════════════════════════════════════════════════════
# Order Confirm Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class OrderConfirmDialog(QDialog):
    def __init__(self, cart: dict, subtotal: int, discount: int, total: int,
                 user: dict, parent=None):
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Minimum
        )
        self._cart = cart
        self._subtotal = subtotal
        self._discount = discount
        self._total = total
        self._user = user
        self._payment_method = "tunai"
        self._payment_type = "lunas"  # tunai payment type: lunas or hutang
        self._selected_customer_id = None
        self._paid_amount = 0
        self._remaining = total

        self.receipt_action = "cancel"
        self.receipt_path = None
        self.buyer_name = ""
        self.payment_method = "tunai"
        self.cash_given = 0
        self.change = 0
        self.customer_id = None

        self.setWindowTitle("Konfirmasi Order")
        self.setModal(True)
        self.setFixedWidth(820)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        screen_h = QApplication.primaryScreen().availableGeometry().height()
        self.setMaximumHeight(min(850, screen_h - 80))
        self.setStyleSheet(f"""
            QDialog {{
                background: {C_WHITE};
                font-family: 'Segoe UI';
            }}
        """)

        self._build_ui()
        self.adjustSize()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        header = QFrame()
        header.setStyleSheet("QFrame { background-color: #FAFAF8; }")
        header_lay = QVBoxLayout(header)
        header_lay.setContentsMargins(28, 20, 28, 16)
        header_lay.setSpacing(0)

        logo = QLabel("Warung<span style='color:#4F6EF7'>+</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("font-size:14px;color:#5F5E5A;font-weight:500;letter-spacing:1px;border:none;")
        header_lay.addWidget(logo)
        header_lay.addSpacing(15)

        title = QLabel("Konfirmasi Order")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        header_lay.addWidget(title)
        header_lay.addSpacing(5)

        subtitle = QLabel("Periksa kembali pesanan sebelum memproses.")
        subtitle.setStyleSheet("font-size:12px;color:#888780;border:none;")
        header_lay.addWidget(subtitle)
        root.addWidget(header)
        root.addWidget(self._make_divider())

        # ── Two-column body ──────────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background: #FAFAF8;")
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)

        # ── LEFT column: order summary ────────────────────────────────────
        left_widget = QWidget()
        left_widget.setStyleSheet("background: #FAFAF8;")
        left_lay = QVBoxLayout(left_widget)
        left_lay.setContentsMargins(28, 18, 20, 18)
        left_lay.setSpacing(0)

        # Buyer name
        self._buyer_label = QLabel("Nama Pembeli (Opsional)")
        self._buyer_label.setFixedHeight(18)
        self._buyer_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 600;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)

        left_lay.addWidget(self._buyer_label)
        left_lay.addSpacing(4)
        self._buyer_input = QLineEdit()
        self._buyer_input.setPlaceholderText("Budi Santoso")
        self._buyer_input.setFixedHeight(34)
        self._buyer_input.setStyleSheet(self._input_style())
        left_lay.addWidget(self._buyer_input)
        left_lay.addSpacing(8)
        
        self._buyer_err = QLabel("")
        self._buyer_err.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 10px;
            color: {C_DANGER};
            background: transparent;
            border: none;
        """)
        self._buyer_err.hide()

        left_lay.addWidget(self._buyer_err)

        # Phone number (hanya tampil saat hutang)
        self._phone_label = QLabel("No Telepon")
        self._phone_label.setFixedHeight(18)
        self._phone_label.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
            color: {C_TEXT_PRI}; background: transparent; border: none;
        """)
        self._phone_label.hide()
        left_lay.addWidget(self._phone_label)
        left_lay.addSpacing(4)

        self._phone_input = QLineEdit()
        self._phone_input.setPlaceholderText("08xx...")
        self._phone_input.setFixedHeight(34)
        self._phone_input.setStyleSheet(self._input_style())
        self._phone_input.hide()
        left_lay.addWidget(self._phone_input)
        
        self._phone_err = QLabel("")
        self._phone_err.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 10px;
            color: {C_DANGER};
            background: transparent;
            border: none;
        """)
        self._phone_err.hide()

        left_lay.addWidget(self._phone_err)

        self._dynamic_spacing = QSpacerItem(
            0,
            2,
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed
        )

        left_lay.addItem(self._dynamic_spacing)
        left_lay.addWidget(self._make_divider())
        left_lay.addSpacing(12)

        # Order items
        self._add_field_label(left_lay, "Item Pesanan")
        left_lay.addSpacing(6)

        items_scroll = QScrollArea()
        items_scroll.setWidgetResizable(True)
        item_count = len(self._cart)
        items_scroll.setFixedHeight(min(max(item_count * 56, 72), 168))
        items_scroll.setFrameShape(QFrame.Shape.NoFrame)
        items_scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 5px; }}
            QScrollBar::handle:vertical {{ background: {C_BORDER}; border-radius: 2px; min-height: 20px; }}
        """)
        items_container = QWidget()
        items_container.setStyleSheet("background: transparent;")
        items_layout = QVBoxLayout(items_container)
        items_layout.setContentsMargins(0, 0, 0, 0)
        items_layout.setSpacing(5)
        for product, quantity in self._cart.values():
            items_layout.addWidget(self._make_confirm_item_row(product, quantity))
        items_layout.addStretch()
        items_scroll.setWidget(items_container)
        left_lay.addWidget(items_scroll)
        left_lay.addSpacing(12)
        left_lay.addWidget(self._make_divider())
        left_lay.addSpacing(10)

        # Summary rows
        for label, value in [("Subtotal", _format_price(self._subtotal))]:
            left_lay.addLayout(self._inline_row(label, value, small=True))
            left_lay.addSpacing(4)

        if self._discount > 0:
            row = self._inline_row("Diskon", _format_price(self._discount), small=True)
            row.itemAt(2).widget().setStyleSheet(f"color:{C_DANGER};font-weight:600;font-size:12px;border:none;")
            left_lay.addLayout(row)
            left_lay.addSpacing(4)

        left_lay.addWidget(self._make_divider())
        left_lay.addSpacing(8)

        total_row = self._inline_row("Total", _format_price(self._total))
        total_row.itemAt(0).widget().setStyleSheet("font-size:14px;font-weight:700;border:none;")
        total_row.itemAt(2).widget().setStyleSheet(f"font-size:15px;font-weight:700;color:{C_ACCENT};border:none;")
        left_lay.addLayout(total_row)
        left_lay.addStretch()

        body_lay.addWidget(left_widget, 1)

        # Vertical separator between columns
        v_sep = QFrame()
        v_sep.setFixedWidth(1)
        v_sep.setStyleSheet("background: #DDD9D2; border: none;")
        body_lay.addWidget(v_sep)

        # ── RIGHT column: payment ─────────────────────────────────────────
        right_widget = QWidget()
        right_widget.setStyleSheet("background: #FAFAF8;")
        right_lay = QVBoxLayout(right_widget)
        right_lay.setContentsMargins(20, 18, 28, 18)
        right_lay.setSpacing(0)

        # Payment method
        self._add_field_label(right_lay, "Metode Pembayaran")
        right_lay.addSpacing(6)

        self._payment_group = QButtonGroup()
        payment_grid = QGridLayout()
        payment_grid.setSpacing(6)
        payment_grid.setContentsMargins(0, 0, 0, 0)

        payment_methods = [("tunai", "💵 Tunai"), ("qris", "📱 QRIS")]
        for idx, (value, label) in enumerate(payment_methods):
            radio = QRadioButton(label)
            radio.setFixedHeight(32)
            radio.setMinimumWidth(110)
            radio.setStyleSheet(self._radio_style())
            if value == "tunai":
                radio.setChecked(True)
            radio.toggled.connect(
                lambda checked, v=value: self._on_payment_method_changed(v) if checked else None
            )
            self._payment_group.addButton(radio, idx)
            payment_grid.addWidget(radio, 0, idx)

        right_lay.addLayout(payment_grid)
        right_lay.addSpacing(14)
        right_lay.addWidget(self._make_divider())
        right_lay.addSpacing(12)

        # Cash payment fields (Tunai)
        self._cash_fields_frame = QFrame()
        self._cash_fields_frame.setStyleSheet("background: transparent;")
        cash_layout = QVBoxLayout(self._cash_fields_frame)
        cash_layout.setContentsMargins(0, 0, 0, 0)
        cash_layout.setSpacing(8)

        # Payment type dropdown
        self._add_field_label(cash_layout, "Jenis Pembayaran")
        cash_layout.addSpacing(4)

        self._payment_type_combo = QComboBox()
        self._payment_type_combo.addItem("Lunas", "lunas")
        self._payment_type_combo.addItem("Hutang", "hutang")
        self._payment_type_combo.setFixedHeight(34)
        arrow_lbl = QLabel("⌄", self._payment_type_combo)
        arrow_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 18px; font-weight: 600;
            color: {C_TEXT_SEC}; background: transparent; border: none;
        """)
        arrow_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        QTimer.singleShot(0, lambda: arrow_lbl.setGeometry(self._payment_type_combo.width() - 28, -6, 24, 40))
        self._payment_type_combo.setStyleSheet(self._combo_style())
        self._payment_type_combo.currentIndexChanged.connect(self._on_payment_type_changed)
        cash_layout.addWidget(self._payment_type_combo)
        cash_layout.addSpacing(0)

        # Customer fields (hutang) — side by side
        self._customer_name_label = QLabel("Nama Pelanggan")
        self._customer_name_label.setStyleSheet(f"font-family:'Segoe UI';font-size:11px;font-weight:600;color:{C_TEXT_PRI};background:transparent;border:none;")
        self._customer_name_label.hide()
        cash_layout.addWidget(self._customer_name_label)
        cash_layout.addSpacing(4)

        customer_fields_row = QHBoxLayout()
        customer_fields_row.setSpacing(8)
        customer_fields_row.setContentsMargins(0, 0, 0, 0)

        self._customer_name_input = QLineEdit()
        self._customer_name_input.setPlaceholderText("Nama pelanggan")
        self._customer_name_input.setFixedHeight(34)
        self._customer_name_input.setStyleSheet(self._input_style())
        self._customer_name_input.hide()

        self._customer_phone_label = QLabel("No Telepon")
        self._customer_phone_label.setStyleSheet(f"font-family:'Segoe UI';font-size:11px;font-weight:600;color:{C_TEXT_PRI};background:transparent;border:none;")
        self._customer_phone_label.hide()

        self._customer_phone_input = QLineEdit()
        self._customer_phone_input.setPlaceholderText("08xx...")
        self._customer_phone_input.setFixedHeight(34)
        self._customer_phone_input.setStyleSheet(self._input_style())
        self._customer_phone_input.hide()
        self._phone_input.textChanged.connect(self._on_phone_lookup)

        # Stacked vertically but in pairs using a grid for tight layout
        self._customer_block = QWidget()
        self._customer_block.setStyleSheet("background: transparent;")
        cust_lay = QVBoxLayout(self._customer_block)
        cust_lay.setContentsMargins(0, 0, 0, 0)
        cust_lay.setSpacing(6)

        name_phone_grid = QGridLayout()
        name_phone_grid.setSpacing(8)
        name_phone_grid.setContentsMargins(0, 0, 0, 0)

        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_col.addWidget(self._customer_name_label)
        name_col.addWidget(self._customer_name_input)

        phone_col = QVBoxLayout()
        phone_col.setSpacing(4)
        phone_col.addWidget(self._customer_phone_label)
        phone_col.addWidget(self._customer_phone_input)

        name_phone_grid.addLayout(name_col, 0, 0)
        name_phone_grid.addLayout(phone_col, 0, 1)
        cust_lay.addLayout(name_phone_grid)
        self._customer_block.hide()
        cash_layout.addWidget(self._customer_block)

        # Cash input
        self._cash_label = QLabel("Uang yang Diberikan")
        self._cash_label.setStyleSheet(f"font-family:'Segoe UI';font-size:11px;font-weight:600;color:{C_TEXT_PRI};background:transparent;border:none;")
        cash_layout.addWidget(self._cash_label)
        cash_layout.addSpacing(4)

        self._cash_input = QLineEdit()
        self._cash_input.setPlaceholderText("0")
        self._cash_input.setFixedHeight(34)
        self._cash_input.setValidator(QIntValidator(0, 999_999_999))
        self._cash_input.setStyleSheet(self._input_style())
        self._cash_input.textChanged.connect(self._on_cash_changed)
        cash_layout.addWidget(self._cash_input)
        cash_layout.addSpacing(8)

        # Remaining/Change display
        remaining_row = QHBoxLayout()
        remaining_row.setContentsMargins(0, 0, 0, 0)
        self._remaining_label = QLabel("Kembalian")
        self._remaining_label.setStyleSheet(f"font-size:12px;color:{C_TEXT_SEC};border:none;")
        remaining_row.addWidget(self._remaining_label)
        remaining_row.addStretch()
        self._remaining_value = QLabel(_format_price(0))
        self._remaining_value.setStyleSheet(f"font-size:12px;font-weight:600;color:{C_SUCCESS};border:none;")
        remaining_row.addWidget(self._remaining_value)
        cash_layout.addLayout(remaining_row)

        right_lay.addWidget(self._cash_fields_frame)
        right_lay.addStretch()

        body_lay.addWidget(right_widget, 1)
        root.addWidget(body)
        root.addWidget(self._make_divider())

        # ── Footer ──────────────────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet("QFrame { background-color: #FAFAF8; }")
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(28, 14, 28, 20)
        footer_lay.setSpacing(8)

        cancel_btn = QPushButton("Batal")
        cancel_btn.setFixedHeight(38)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #5F5E5A;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 500;
                border-radius: 10px; border: 1px solid #DDD9D2; padding: 0 18px;
            }
            QPushButton:hover { background: #F1EFE8; border: 1px solid #C8C6BF; }
        """)
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton("Proses && Cetak Struk")
        confirm_btn.setFixedHeight(38)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 600;
                border-radius: 10px; border: none; padding: 0 18px;
            }}
            QPushButton:hover {{ background: {C_ACCENT_H}; }}
            QPushButton:pressed {{ background: #2F4CD9; }}
        """)
        confirm_btn.clicked.connect(self._on_confirm)

        footer_lay.addStretch()
        footer_lay.addWidget(cancel_btn)
        footer_lay.addWidget(confirm_btn)
        root.addWidget(footer)

        # Initialize UI state
        self._on_payment_type_changed(0)
        
        
    def _on_phone_lookup(self, phone: str):
        phone = phone.strip()

        if not phone:
            self._buyer_input.setText("")
            self._buyer_input.setReadOnly(False)
            self._buyer_input.setStyleSheet(self._input_style())
            self._selected_customer_id = None
            return

        try:
            customer = CustomerController.get_by_phone(phone)

            if customer:
                self._buyer_input.setText(customer.name)
                self._buyer_input.setReadOnly(True)

                self._selected_customer_id = customer.id

                self._buyer_input.setStyleSheet(
                    self._input_style() +
                    "QLineEdit { border: 1px solid #27AE60; }"
                )

            else:
                self._selected_customer_id = None
                self._buyer_input.setText("")
                self._buyer_input.setReadOnly(False)   # ← tambahkan ini
                self._buyer_input.setStyleSheet(self._input_style())

        except Exception as e:
            Toast.show_toast("No Telepon Error!", "error", self)

    # ── Dialog helpers ─────────────────────────────────────────────────────────
    def _make_divider(self) -> QFrame:
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background: #DDD9D2; border: none;")
        return div

    def _add_field_label(self, layout: QVBoxLayout, text: str):
        lbl = QLabel(text)
        lbl.setFixedHeight(18)
        lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 600;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        layout.addWidget(lbl)

    def _inline_row(self, left: str, right: str, small: bool = False) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        fs = "12px" if small else "13px"
        lbl = QLabel(left)
        lbl.setStyleSheet(f"font-size:{fs};color:{C_TEXT_SEC if small else C_TEXT_PRI};border:none;")
        val = QLabel(right)
        val.setStyleSheet(f"font-size:{fs};font-weight:600;color:{C_TEXT_PRI};border:none;")
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        return row

    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 6px;
                font-family: 'Segoe UI';
                font-size: 11px;
                padding: 0 12px;
                color: {C_TEXT_PRI};
            }}
            QLineEdit:focus {{
                border: 1px solid {C_ACCENT};
            }}
        """

    def _radio_style(self) -> str:
        return f"""
            QRadioButton {{
                color: {C_TEXT_PRI};
                font-family: 'Segoe UI';
                font-size: 10px;
                font-weight: 500;
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 8px;
                padding: 0 10px;
            }}
            QRadioButton::indicator {{
                width: 13px;
                height: 13px;
                border-radius: 7px;
                border: 2px solid {C_BORDER};
                background: {C_WHITE};
                margin-right: 5px;
            }}
            QRadioButton::indicator:checked {{
                background: {C_ACCENT};
                border: 2px solid {C_ACCENT};
            }}
            QRadioButton:checked {{
                background: {C_TAG_BG};
                color: {C_ACCENT};
                border: 1px solid {C_ACCENT};
                font-weight: 600;
            }}
        """

    def _combo_style(self) -> str:
        return f"""
            QComboBox {{
                background:    #FFFFFF;
                border:        1px solid #DDD9D2;
                border-radius: 6px;
                padding:       0 10px;
                font-size:     12px;
                color:         #1b1b1b;
                font-family:   'Segoe UI';
            }}
            QComboBox:focus {{
                border: 1px solid #4F6EF7;
            }}
            QComboBox:hover {{
                border: 1px solid #B4B0AA;
            }}
            QComboBox::drop-down {{
                border:        none;
                width:         24px;
                padding-right: 4px;
            }}
            QComboBox::down-arrow {{
                width:  8px;
                height: 8px;
            }}

            QComboBox QAbstractItemView {{
                background:                #FFFFFF;
                border:                    1px solid #DDD9D2;
                border-radius:             0px;
                padding:                   2px;
                outline:                   none;
                color:                     #1b1b1b;
                font-family:               'Segoe UI';
                font-size:                 12px;
                selection-background-color: #EEF1FE;
                selection-color:            #4F6EF7;
            }}
            QComboBox QAbstractItemView::item {{
                height:        28px;
                padding-left:  8px;
                border-radius: 0px;
                color:         #1b1b1b;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background:    #F4F5F9;
                color:         #1b1b1b;
                border-radius: 0px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background:    #EEF1FE;
                color:         #4F6EF7;
                border-radius: 0px;
            }}
        """

    def _make_confirm_item_row(self, product: Product, quantity: int) -> QFrame:
        row_frame = QFrame()
        row_frame.setFixedHeight(52)

        row_frame.setStyleSheet(f"""
            QFrame {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 8px;
            }}
        """)

        row_layout = QHBoxLayout(row_frame)
        row_layout.setContentsMargins(10, 0, 10, 0)
        row_layout.setSpacing(8)

        # =========================
        # ICON BARANG
        # =========================
        theme = CAT_THEME.get(product.category, CAT_THEME["Lainnya"])

        item_icon = QLabel(theme["emoji"])

        item_icon.setFixedSize(36, 36)

        item_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        item_icon.setStyleSheet(f"""
            font-size: 18px;
            background: {theme['bg']};
            border-radius: 8px;
            color: {theme['text']};
        """)

        row_layout.addWidget(item_icon)

        # =========================
        # INFO PRODUK
        # =========================
        info_widget = QWidget()
        info_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )

        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        from PyQt6.QtGui import QFontMetrics

        name_label = QLabel()
        name_label.setFixedHeight(20)

        name_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)

        metrics = QFontMetrics(name_label.font())

        elided = metrics.elidedText(
            product.name,
            Qt.TextElideMode.ElideRight,
            200
        )

        name_label.setText(elided)

        info_layout.addWidget(name_label)

        price_label = QLabel(_format_price(product.price))
        price_label.setFixedHeight(16)

        price_label.setStyleSheet(f"""
            font-size: 10px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)

        info_layout.addWidget(price_label)

        row_layout.addWidget(info_widget)

        # =========================
        # QTY
        # =========================
        qty_label = QLabel(f"×{quantity}")

        qty_label.setFixedWidth(32)

        qty_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter |
            Qt.AlignmentFlag.AlignVCenter
        )

        qty_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {C_ACCENT};
            background: transparent;
            border: none;
        """)

        row_layout.addWidget(qty_label)

        # =========================
        # TOTAL
        # =========================
        total_label = QLabel(_format_price(product.price * quantity))

        total_label.setFixedWidth(90)

        total_label.setAlignment(
            Qt.AlignmentFlag.AlignRight |
            Qt.AlignmentFlag.AlignVCenter
        )

        total_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)

        row_layout.addWidget(total_label)

        return row_frame

    # ── Payment logic ──────────────────────────────────────────────────────────
    def _load_customers(self):
        pass  # No need to load customers, user will input manually

    def _on_payment_method_changed(self, method: str):
        
        self._payment_method = method
        self._cash_fields_frame.show()

        # refresh UI
        self._on_payment_type_changed(
            self._payment_type_combo.currentIndex()
        )

        QTimer.singleShot(0, self.adjustSize)


    def _on_payment_type_changed(self, index: int):
        self._payment_type = self._payment_type_combo.currentData()

        # =========================================================
        # HUTANG
        # =========================================================
        if self._payment_type == "hutang":

            # validator:
            # maksimal pembayaran = total - 1
            self._dynamic_spacing.changeSize(
                0,
                16,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Fixed
            )
            self._buyer_label.setText("Nama Pembeli")

            max_cash = int(max(0, self._total - 1))

            self._cash_input.setValidator(
                QIntValidator(0, max_cash)
            )

            # tampilkan no telepon
            self._phone_label.show()
            self._phone_input.show()
            

            # cash field
            self._cash_label.setText("Uang yang Dibayarkan")
            self._cash_label.show()

            self._cash_input.show()

            # remaining
            self._remaining_label.setText("Sisa Bayar")
            self._remaining_label.show()

            self._remaining_value.setStyleSheet(
                f"""
                font-size:12px;
                font-weight:600;
                color:{C_DANGER};
                border:none;
                """
            )

            self._remaining_value.show()

        # =========================================================
        # LUNAS
        # =========================================================
        else:
            self._dynamic_spacing.changeSize(
                0,
                2,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Fixed
            )

            self._buyer_label.setText("Nama Pembeli (Opsional)")
            # validator normal
            self._cash_input.setValidator(
                QIntValidator(0, 999_999_999)
            )

            # sembunyikan no telepon
            self._phone_label.hide()
            self._phone_input.hide()

            self._remaining_label.setText("Kembalian")

            # =========================
            # TUNAI
            # =========================
            if self._payment_method == "tunai":

                self._cash_label.setText("Uang yang Diberikan")

                self._cash_label.show()
                self._cash_input.show()

                self._remaining_label.show()

                self._remaining_value.setStyleSheet(
                    f"""
                    font-size:12px;
                    font-weight:600;
                    color:{C_SUCCESS};
                    border:none;
                    """
                )

                self._remaining_value.show()

            # =========================
            # QRIS
            # =========================
            else:

                self._cash_label.hide()
                self._cash_input.hide()

                self._remaining_label.hide()
                self._remaining_value.hide()

        self._on_cash_changed()

        # refresh layout
        self.layout().invalidate()
        self.layout().activate()

        # biar bisa mengecil lagi
        self.setMinimumHeight(0)

        self.adjustSize()
        self.resize(self.sizeHint())


    def _on_cash_changed(self):
        try:

            # QRIS lunas tidak perlu kalkulasi
            if self._payment_method == "qris" and self._payment_type == "lunas":
                return

            cash_str = self._cash_input.text().strip()
            self._paid_amount = int(cash_str) if cash_str else 0

            # =====================================================
            # HUTANG
            # =====================================================
            if self._payment_type == "hutang":

                # proteksi tambahan
                if self._paid_amount >= self._total:

                    Toast.show_toast(
                        "Pembayaran hutang harus kurang dari total!",
                        "error",
                        self
                    )

                    self._cash_input.blockSignals(True)

                    self._cash_input.setText(
                        str(int(max(0, self._total - 1)))
                    )

                    self._cash_input.blockSignals(False)

                    self._paid_amount = max(
                        0,
                        self._total - 1
                    )

                self._remaining = (
                    self._total - self._paid_amount
                )

                # masih ada hutang
                if self._remaining > 0:

                    self._remaining_value.setText(
                        _format_price(self._remaining)
                    )

                    self._remaining_value.setStyleSheet(
                        f"""
                        font-size:12px;
                        font-weight:600;
                        color:{C_DANGER};
                        border:none;
                        """
                    )

                # lunas
                elif self._remaining == 0:

                    self._remaining_value.setText(
                        _format_price(0)
                    )

                    self._remaining_value.setStyleSheet(
                        f"""
                        font-size:12px;
                        font-weight:600;
                        color:{C_SUCCESS};
                        border:none;
                        """
                    )

                # lebih bayar
                else:

                    self._remaining_value.setText(
                        f"Kembali {_format_price(abs(self._remaining))}"
                    )

                    self._remaining_value.setStyleSheet(
                        f"""
                        font-size:12px;
                        font-weight:600;
                        color:{C_SUCCESS};
                        border:none;
                        """
                    )

            # =====================================================
            # TUNAI LUNAS
            # =====================================================
            else:

                self._remaining = (
                    self._paid_amount - self._total
                )

                # uang kurang
                if self._remaining < 0:

                    self._remaining_value.setText(
                        f"Kurang {_format_price(abs(self._remaining))}"
                    )

                    self._remaining_value.setStyleSheet(
                        f"""
                        font-size:12px;
                        font-weight:600;
                        color:{C_DANGER};
                        border:none;
                        """
                    )

                # uang cukup
                else:

                    self._remaining_value.setText(
                        _format_price(self._remaining)
                    )

                    self._remaining_value.setStyleSheet(
                        f"""
                        font-size:12px;
                        font-weight:600;
                        color:{C_SUCCESS};
                        border:none;
                        """
                    )

        except ValueError:

            self._remaining_value.setText(
                "Format tidak valid"
            )

            self._remaining_value.setStyleSheet(
                f"""
                font-size:12px;
                font-weight:600;
                color:{C_DANGER};
                border:none;
                """
            )

    def _on_confirm(self):
        if self._payment_method == "tunai" and self._payment_type == "lunas":
            cash_str = self._cash_input.text().strip()
            if not cash_str or int(cash_str) == 0:
                Toast.show_toast("Masukkan jumlah uang tunai!", "error", self)
                return
            if int(cash_str) < self._total:
                Toast.show_toast("Uang tunai tidak cukup!", "error", self)
                return

        # Validasi hutang: nama pembeli + no telepon wajib
        if self._payment_type == "hutang":
            cash_str = self._cash_input.text().strip()
            paid_amount = int(cash_str) if cash_str else 0

            if paid_amount >= self._total:
                Toast.show_toast("Pembayaran hutang harus kurang dari total.", "error", self)
                return
            buyer_name = self._buyer_input.text().strip()
            if not buyer_name:
                Toast.show_toast("Masukkan nama pembeli untuk hutang!", "error", self)
                return
            phone = self._phone_input.text().strip()
            if not phone:
                Toast.show_toast("Masukkan nomor telepon untuk hutang!", "error", self)
                return

        receipt_text = self._build_receipt_text()
        preview_dialog = ReceiptPreviewDialog(receipt_text, self)

        if preview_dialog.exec() == QDialog.DialogCode.Accepted:
            self.receipt_action = preview_dialog.action
            self.receipt_path = preview_dialog.saved_path
            self.buyer_name = self._buyer_input.text().strip()
            self.payment_method = self._payment_method

            if self._payment_type == "hutang":
                try:
                    phone = self._phone_input.text().strip()
                    existing = CustomerController.get_by_phone(phone)
                    if existing:
                        self.customer_id = existing.id
                    else:
                        self.customer_id = CustomerController.add(
                            name=self._buyer_input.text().strip(),
                            phone=phone,
                        )
                except Exception as e:
                    Toast.show_toast(f"Error menyimpan pelanggan: {str(e)}", "error", self)
                    return
                cash_str = self._cash_input.text().strip()
                self.cash_given = int(cash_str) if cash_str else 0
                self.change = self._total - self.cash_given

            else:  # lunas
                buyer_name = self._buyer_input.text().strip()
                if buyer_name:
                    try:
                        self.customer_id = CustomerController.add(name=buyer_name)
                    except Exception as e:
                        Toast.show_toast(f"Error menyimpan pelanggan: {str(e)}", "error", self)
                        return
                else:
                    self.customer_id = None  # Pembeli Umum

                if self._payment_method == "tunai":
                    self.cash_given = self._paid_amount
                    self.change = self._remaining
                else:  # qris lunas
                    self.cash_given = self._total
                    self.change = 0

            self.accept()

    def _build_receipt_text(self) -> str:
        RECEIPT_WIDTH = 36

        def _line(char: str = "-") -> str:
            return char * RECEIPT_WIDTH

        def _center(text: str) -> str:
            return text.center(RECEIPT_WIDTH)

        def _truncate(text: str, max_len: int) -> str:
            return text[:max_len - 1] + "…" if len(text) > max_len else text

        def _row(left: str, right) -> str:
            left_str = _truncate(left, RECEIPT_WIDTH - 12)
            right_str = _format_price(right) if isinstance(right, int) else str(right)
            spaces = RECEIPT_WIDTH - len(left_str) - len(right_str)
            return left_str + " " * max(1, spaces) + right_str

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_name = self._user.get("name", "Cashier")
        buyer_name = self._buyer_input.text().strip() or "Pembeli Umum"
        payment_text = {"tunai": "Tunai", "qris": "QRIS"}.get(self._payment_method, "Tunai")
        payment_text += f" - {'Lunas' if self._payment_type == 'lunas' else 'Hutang'}"

        lines = [
            _center("WARUNG+"),
            _center("Tanda Terima"),
            _line("="),
            "",
            _row("Tgl", timestamp),
            _row("Kasir", user_name),
            _row("Pembeli", buyer_name),
        ]

        if self._payment_type == "hutang":
            lines.append(_row("Telp", self._phone_input.text().strip()))

        lines += [
            "",
            _line("-"),
            _center("BARANG BELANJA"),
            _line("-"),
        ]

        for product, quantity in self._cart.values():
            lines.append(_truncate(product.name, RECEIPT_WIDTH))
            lines.append(_row(f"{quantity}x @ {_format_price(product.price)}", product.price * quantity))
            lines.append("")

        lines += [
            _line("-"),
            _row("Subtotal", self._subtotal),
            _row("Diskon", self._discount),
            _line("="),
            _row("TOTAL", self._total),
            "",
            _line("-"),
            _row("Metode", payment_text),
        ]

        if self._payment_type == "lunas" and self._payment_method == "tunai":
            lines += [
                _row("Tunai", self._paid_amount),
                _row("Kembali", self._remaining),
            ]
        elif self._payment_type == "hutang":
            lines += [
                _row("Dibayarkan", self._paid_amount),
                _row("Sisa Hutang", self._total - self._paid_amount),
            ]

        lines += [
            _line("-"),
            _center("Terima Kasih!"),
            _center("WARUNG+"),
            _line("="),
        ]

        return "\n".join(lines)