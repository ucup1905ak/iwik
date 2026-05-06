# gui/views/screens/sales_page.py

from datetime import datetime
from controllers.product import ProductController, Product
from controllers.sales import SalesController
from controllers.sales_detail import SalesDetailController
from PyQt6.QtWidgets import (
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
    QMessageBox,
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

# Constants untuk CashierProductCard grid
CASHIER_CARD_WIDTH = 290
CASHIER_CARD_SPACING = 12


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
    """Get button theme for category (untuk active state)"""
    if category == "Semua":
        return {"bg": C_ACCENT, "text": C_WHITE, "border": C_ACCENT}
    cat = _cat_theme(category)
    return {"bg": cat["bg"], "text": cat["text"], "border": cat["text"]}


def _style_cat_btn(btn: QPushButton, cat: str, active: bool):
    """Style category button based on active state"""
    if active:
        theme = _cat_button_theme(cat)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {theme['bg']};
                color: {theme['text']};
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
                border-radius: 10px;
                border: 1.5px solid {theme['border']};
                padding: 0 12px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """)
    else:
        cat_theme = _cat_theme(cat)
        soft_bg = cat_theme["bg"]
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_WHITE};
                color: {cat_theme['text']};
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 500;
                border-radius: 10px;
                border: 1.5px solid {C_BORDER};
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background: {soft_bg};
                border: 1.5px solid {cat_theme['text']};
            }}
        """)


# ═══════════════════════════════════════════════════════════════════════════════
# Cashier Product Card - horizontal compact layout
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
        stock = product.stock

        self.setObjectName("CashierProductCard")
        self.setFixedSize(CASHIER_CARD_WIDTH, 160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet(f"""
            QFrame#CashierProductCard {{
                background: {C_WHITE};
                border-radius: 14px;
                border: 1.5px solid {C_BORDER};
            }}
            QFrame#CashierProductCard:hover {{
                border: 1.5px solid {C_ACCENT};
            }}
        """)
        _apply_card_shadow(self)

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # ── Image (kiri) fixed width ───────────────────────────────────────
        img_container = QFrame()
        img_container.setFixedWidth(130)
        img_container.setStyleSheet(f"""
            QFrame {{
                background: #FFFFFF;
                border-radius: 10px;
                border: none;
            }}
        """)

        img_layout = QVBoxLayout(img_container)
        img_layout.setContentsMargins(3, 3, 3, 3)
        img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        img_label = QLabel()
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if product.image_path and os.path.exists(product.image_path):
            pixmap = QPixmap(product.image_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    120, 135,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                img_label.setPixmap(scaled)
            else:
                img_label.setText("📦")
                img_label.setStyleSheet(f"font-size: 35px; color: {C_TEXT_SEC};")
        else:
            img_label.setText("📦")
            img_label.setStyleSheet(f"font-size: 35px; color: {C_TEXT_SEC};")

        img_layout.addWidget(img_label)
        root.addWidget(img_container)

        # ── Info (tengah) ──────────────────────────────────────────────
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        # ── Top row: category + stock ──────────────────────────────────────
        top = QHBoxLayout()
        top.setSpacing(4)
        cat = _cat_theme(product.category)

        cat_tag = QLabel(f"{cat['emoji']} {product.category}")
        cat_tag.setStyleSheet(f"""
            background:    {cat['bg']};
            color:         {cat['text']};
            font-family:   'Segoe UI';
            font-size:     9px;
            font-weight:   700;
            padding:       2px 6px;
            border-radius: 5px;
            border:        none;
        """)
        cat_tag.setMaximumWidth(100)

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
            font-size:     9px;
            font-weight:   600;
            padding:       2px 6px;
            border-radius: 5px;
            border:        none;
        """)

        top.addWidget(cat_tag)
        top.addStretch()
        top.addWidget(stock_badge)
        info_layout.addLayout(top)

        # ── Name ───────────────────────────────────────────────────────────
        name_lbl = QLabel(product.name)
        name_lbl.setWordWrap(True)
        name_lbl.setMaximumHeight(28)
        name_lbl.setStyleSheet(f"""
            font-family:  'Segoe UI';
            font-size:    11px;
            font-weight:  600;
            color:        {C_TEXT_PRI};
            background:   transparent;
            border:       none;
        """)
        info_layout.addWidget(name_lbl)

        # ── Brand ──────────────────────────────────────────────────────────
        if product.brand:
            brand_lbl = QLabel(product.brand)
            brand_lbl.setMaximumHeight(16)
            brand_lbl.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size:   9px;
                color:       {C_TEXT_SEC};
                background:  transparent;
                border:      none;
            """)
            info_layout.addWidget(brand_lbl)

        info_layout.addStretch(1)

        # ── Price at bottom ────────────────────────────────────────────────
        price_lbl = QLabel(_format_price(product.price))
        price_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   12px;
            font-weight: 700;
            color:       {C_ACCENT};
            background:  transparent;
            border:      none;
        """)
        info_layout.addWidget(price_lbl)

        root.addWidget(info_container, stretch=1)

    def mousePressEvent(self, event):
        self.clicked.emit(self._product)
        super().mousePressEvent(event)


# ═══════════════════════════════════════════════════════════════════════════════
# Order Item Card (untuk summary di sebelah kanan)
# ═══════════════════════════════════════════════════════════════════════════════
class OrderItemCard(QFrame):
    remove_clicked = pyqtSignal(int)  # emit product_id
    quantity_changed = pyqtSignal(int, int)  # product_id, new_quantity

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

        self.setMinimumHeight(64)
        self.setMaximumHeight(72)

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        # ── Info ───────────────────────────────────────────────────
        info = QVBoxLayout()
        info.setSpacing(2)

        name_lbl = QLabel(self._product.name)
        name_lbl.setWordWrap(True)
        name_lbl.setMaximumHeight(22)
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
        price_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 10px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        info.addWidget(price_lbl)
        root.addLayout(info)

        # ── Quantity ───────────────────────────────────────────────
        qty_frame = QFrame()
        qty_frame.setStyleSheet(f"""
            QFrame {{
                background: {C_TAG_BG};
                border-radius: 6px;
                border: none;
            }}
        """)
        qty_layout = QHBoxLayout(qty_frame)
        qty_layout.setContentsMargins(4, 2, 4, 2)
        qty_layout.setSpacing(4)

        minus_btn = QPushButton("-")
        minus_btn.setFixedSize(24, 24)
        minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        minus_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C_ACCENT};
                border: none;
                font-weight: 600;
                font-size: 12px;
            }}
        """)
        minus_btn.clicked.connect(self._on_minus)

        self._qty_lbl = QLabel(str(self._quantity))
        self._qty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qty_lbl.setFixedWidth(20)
        self._qty_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 600;
            color: {C_ACCENT};
            background: transparent;
            border: none;
        """)

        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(24, 24)
        plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        plus_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C_ACCENT};
                border: none;
                font-weight: 600;
                font-size: 12px;
            }}
        """)
        plus_btn.clicked.connect(self._on_plus)

        qty_layout.addWidget(minus_btn)
        qty_layout.addWidget(self._qty_lbl)
        qty_layout.addWidget(plus_btn)
        root.addWidget(qty_frame)

        # ── Remove ─────────────────────────────────────────────────
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(28, 28)
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

    def _on_minus(self):
        if self._quantity > 1:
            self._quantity -= 1
            self._qty_lbl.setText(str(self._quantity))
            self.quantity_changed.emit(self._product.id, self._quantity)

    def _on_plus(self):
        # Validasi stok
        if self._quantity >= self._product.stock:
            Toast.show_toast(
                f"Stok {self._product.name} hanya {self._product.stock} unit.",
                "error",
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
# Sales Page - Halaman Kasir
# ═══════════════════════════════════════════════════════════════════════════════
class SalesPage(QWidget):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self._user = user
        self._products = []
        self._filtered_products = []
        self._cart = {}  # {product_id: (Product, quantity)}
        self._recent_products = {}  # {product_id: count}
        self._active_category = "Semua"
        self._products_scroll = None

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C_BG};")

        self._build_ui()
        self._load_products()
        
        # Connect signals untuk sinkronisasi dengan halaman lain
        product_signals.product_added.connect(self._on_product_added)
        product_signals.product_edited.connect(self._on_product_edited)
        product_signals.product_deleted.connect(self._on_product_deleted)
        product_signals.product_stock_changed.connect(self._on_product_stock_changed)
        product_signals.products_imported.connect(self._on_products_imported)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # ── Header ──────────────────────────────────────────────────────────
        header = QVBoxLayout()
        header.setSpacing(4)

        page_title = QLabel("Kasir")
        page_title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 27px;
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
        root.addSpacing(12)

        # ── Main content (kiri + kanan) ────────────────────────────────────
        main_container = QHBoxLayout()
        main_container.setSpacing(16)
        main_container.setContentsMargins(0, 0, 0, 0)

        # ── LEFT: Products section ──────────────────────────────────────────
        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # ── Search bar ────────────────────────────────────────────────────
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

        # ── Category buttons ────────────────────────────────────────────
        cat_frame = QFrame()
        cat_frame.setStyleSheet("background: transparent; border: none;")
        cat_layout = QHBoxLayout(cat_frame)
        cat_layout.setContentsMargins(0, 0, 0, 0)
        cat_layout.setSpacing(10)

        self._cat_buttons = {}
        for cat in SAMPLE_CATEGORIES:
            btn = QPushButton(cat)
            btn.setFixedHeight(38)
            btn.setMinimumWidth(90)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, c=cat: self._set_category(c))
            cat_layout.addWidget(btn)
            self._cat_buttons[cat] = btn

        cat_layout.addStretch()
        left_layout.addWidget(cat_frame)

        # ── Products scroll (grid layout) ─────────────────────────────────
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
                margin: 8px 2px 8px 0;
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
        self._products_grid.setContentsMargins(CASHIER_CARD_SPACING, 0, CASHIER_CARD_SPACING, 0)
        self._products_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self._products_scroll.setWidget(products_widget)
        left_layout.addWidget(self._products_scroll, stretch=1)

        main_container.addLayout(left_layout, stretch=1)

        # ── RIGHT: Order Summary ────────────────────────────────────────────
        summary_frame = QFrame()
        summary_frame.setFixedWidth(360)
        summary_frame.setStyleSheet(f"""
            QFrame {{
                background: {C_WHITE};
                border-radius: 14px;
                border: 1.5px solid {C_BORDER};
            }}
        """)
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(12)

        # ── Title ──────────────────────────────────────────────────────
        title = QLabel("Order")
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 16px;
            font-weight: 700;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        summary_layout.addWidget(title)

        # ── Order items scroll ─────────────────────────────────────────
        scroll_items = QScrollArea()
        scroll_items.setWidgetResizable(True)
        scroll_items.setMaximumHeight(280)
        scroll_items.setFrameShape(QFrame.Shape.NoFrame)
        scroll_items.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {C_BORDER};
                border-radius: 3px;
            }}
        """)

        items_widget = QWidget()
        items_widget.setStyleSheet("background: transparent;")
        self._items_layout = QVBoxLayout(items_widget)
        self._items_layout.setSpacing(8)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.addStretch()

        scroll_items.setWidget(items_widget)
        summary_layout.addWidget(scroll_items, stretch=1)

        # ── Divider ────────────────────────────────────────────────────
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background: {C_BORDER}; border: none;")
        summary_layout.addWidget(divider)

        # ── Subtotal ───────────────────────────────────────────────────
        subtotal_row = QHBoxLayout()
        subtotal_lbl = QLabel("Subtotal")
        subtotal_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        subtotal_row.addWidget(subtotal_lbl)
        subtotal_row.addStretch()
        self._subtotal_value = QLabel("Rp 0")
        self._subtotal_value.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            font-weight: 600;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        subtotal_row.addWidget(self._subtotal_value)
        summary_layout.addLayout(subtotal_row)

        # ── Discount ───────────────────────────────────────────────────
        discount_label = QLabel("Diskon")
        discount_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            font-weight: 500;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        summary_layout.addWidget(discount_label)

        discount_frame = QHBoxLayout()
        discount_frame.setSpacing(8)

        self._discount_type = QComboBox()
        self._discount_type.addItem("Rp")
        self._discount_type.addItem("%")
        self._discount_type.setFixedWidth(60)
        self._discount_type.setFixedHeight(36)
        self._discount_type.setStyleSheet(f"""
            QComboBox {{
                background: {C_TAG_BG};
                color: {C_ACCENT};
                border: 1px solid {C_BORDER};
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 0 8px;
            }}
        """)
        self._discount_type.currentTextChanged.connect(self._on_discount_changed)
        discount_frame.addWidget(self._discount_type)

        self._discount_input = QLineEdit()
        self._discount_input.setPlaceholderText("0")
        self._discount_input.setFixedHeight(36)
        self._discount_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C_TAG_BG};
                border: 1px solid {C_BORDER};
                border-radius: 6px;
                font-size: 11px;
                padding: 0 8px;
                color: {C_TEXT_PRI};
            }}
        """)
        self._discount_input.textChanged.connect(self._on_discount_changed)
        discount_frame.addWidget(self._discount_input)

        summary_layout.addLayout(discount_frame)

        # ── Discount display ───────────────────────────────────────────
        discount_display_row = QHBoxLayout()
        discount_lbl = QLabel("Potongan")
        discount_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        discount_display_row.addWidget(discount_lbl)
        discount_display_row.addStretch()
        self._discount_value = QLabel("Rp 0")
        self._discount_value.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            font-weight: 600;
            color: {C_DANGER};
            background: transparent;
            border: none;
        """)
        discount_display_row.addWidget(self._discount_value)
        summary_layout.addLayout(discount_display_row)

        # ── Total ──────────────────────────────────────────────────────
        divider2 = QFrame()
        divider2.setFixedHeight(1)
        divider2.setStyleSheet(f"background: {C_BORDER}; border: none;")
        summary_layout.addWidget(divider2)

        total_row = QHBoxLayout()
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
        self._total_value = QLabel("Rp 0")
        self._total_value.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 14px;
            font-weight: 700;
            color: {C_ACCENT};
            background: transparent;
            border: none;
        """)
        total_row.addWidget(self._total_value)
        summary_layout.addLayout(total_row)

        summary_layout.addSpacing(12)

        # ── Order button ───────────────────────────────────────────────
        order_btn = QPushButton("Proses Order")
        order_btn.setFixedHeight(44)
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
        """)
        order_btn.clicked.connect(self._on_order_clicked)
        summary_layout.addWidget(order_btn)

        main_container.addWidget(summary_frame)
        root.addLayout(main_container, stretch=1)

        self._set_category("Semua")

    def _load_products(self):
        """Load produk dari database"""
        try:
            self._products = ProductController.fetch()
            self._filtered_products = self._products
            self._refresh_products_grid()
        except Exception as e:
            Toast.show_toast(f"Error loading products: {str(e)}", "error", self)

    def _set_category(self, category: str):
        """Filter produk berdasarkan kategori"""
        self._active_category = category

        # Update button style
        for cat, btn in self._cat_buttons.items():
            is_active = (cat == category)
            _style_cat_btn(btn, cat, is_active)

        self._filter_products()

    def _on_search(self):
        """Filter produk berdasarkan search"""
        self._filter_products()

    def _filter_products(self):
        """Apply all filters"""
        query = self._search_input.text().lower()
        
        self._filtered_products = [
            p for p in self._products
            if (self._active_category == "Semua" or p.category == self._active_category)
            and (query == "" or query in p.name.lower() or query in (p.brand or "").lower())
        ]

        self._refresh_products_grid()

    def _get_product_column_count(self) -> int:
        """Calculate jumlah kolom berdasarkan viewport width"""
        if not self._products_scroll:
            return 2
        
        available = self._products_scroll.viewport().width()
        cols = max(1, available // (CASHIER_CARD_WIDTH + CASHIER_CARD_SPACING))
        return cols

    def _clear_products_grid(self):
        """Clear semua widget dari grid"""
        while self._products_grid.count():
            item = self._products_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _refresh_products_grid(self):
        """Refresh tampilan grid produk responsive"""
        self._clear_products_grid()

        if not self._filtered_products:
            # Show empty state
            empty_label = QLabel("📦 Tidak ada produk")
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

        # Add stretch column di akhir untuk push card ke kiri (tidak center)
        last_row = (len(self._filtered_products) - 1) // cols if self._filtered_products else 0
        last_col = (len(self._filtered_products) - 1) % cols if self._filtered_products else 0
        
        # Tambah column stretch setelah kolom terakhir yang ada card
        for col_idx in range(last_col + 1, cols):
            stretch_widget = QWidget()
            self._products_grid.addWidget(stretch_widget, last_row, col_idx)
            self._products_grid.setColumnStretch(col_idx, 1)
        
        # Tambah row stretch di bawah untuk bottom spacing
        self._products_grid.addWidget(QWidget(), last_row + 1, 0)
        self._products_grid.setRowStretch(last_row + 1, 1)

    def _add_to_cart(self, product: Product):
        """Tambah produk ke cart dengan validasi stok"""
        # Validasi: produk habis
        if product.stock <= 0:
            Toast.show_toast("Produk habis.", "error", self)
            return

        # Jika produk sudah ada di cart
        if product.id in self._cart:
            existing_product, qty = self._cart[product.id]
            
            # Validasi: qty tidak boleh melebihi stok
            if qty >= product.stock:
                Toast.show_toast(
                    f"Jumlah {product.name} sudah mencapai batas stok ({product.stock}).",
                    "error",
                    self
                )
                return
            
            self._cart[product.id] = (product, qty + 1)
        else:
            # Produk baru
            self._cart[product.id] = (product, 1)

        # Track recent items
        self._recent_products[product.id] = self._recent_products.get(product.id, 0) + 1

        self._refresh_cart_display()

    def _refresh_cart_display(self):
        """Refresh tampilan cart"""
        # Clear layout (semua kecuali stretch)
        while self._items_layout.count() > 1:
            item = self._items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add items
        for product_id, (product, quantity) in self._cart.items():
            item_card = OrderItemCard(product, quantity)
            item_card.remove_clicked.connect(self._remove_from_cart)
            item_card.quantity_changed.connect(self._on_quantity_changed)
            self._items_layout.insertWidget(self._items_layout.count() - 1, item_card)

        self._update_totals()

    def _on_quantity_changed(self, product_id: int, new_quantity: int):
        """Handle perubahan quantity dengan validasi"""
        if product_id in self._cart:
            product, _ = self._cart[product_id]
            
            # Validasi: tidak boleh melebihi stok
            if new_quantity > product.stock:
                # Revert ke quantity lama
                Toast.show_toast(
                    f"Tidak bisa melebihi stok yang tersedia ({product.stock}).",
                    "error",
                    self
                )
                self._refresh_cart_display()
                return
            
            self._cart[product_id] = (product, new_quantity)
            self._update_totals()

    def _remove_from_cart(self, product_id: int):
        """Hapus produk dari cart"""
        if product_id in self._cart:
            del self._cart[product_id]
            self._refresh_cart_display()

    def _on_discount_changed(self):
        """Handle perubahan diskon"""
        self._update_totals()

    def _calculate_discount(self, subtotal: int) -> tuple:
        """Calculate discount amount - return (discount_amount, final_total)"""
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
        """Update display subtotal, discount, total"""
        subtotal = sum(product.price * qty for product, qty in self._cart.values())

        self._subtotal_value.setText(_format_price(subtotal))

        discount_amount, total = self._calculate_discount(subtotal)
        self._discount_value.setText(_format_price(discount_amount))
        self._total_value.setText(_format_price(total))

    def _on_order_clicked(self):
        """Handle order button click"""
        if not self._cart:
            Toast.show_toast("Cart kosong", "error", self)
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
            # Ambil metadata dari dialog hasil preview
            self._process_order(
                total=total,
                discount=discount_amount,
                payment_method=dialog.payment_method,
                paid_amount=dialog.cash_given if dialog.payment_method == "tunai" else total,
                buyer_name=dialog.buyer_name,
                receipt_path=dialog.receipt_path
            )

    def _process_order(self, total: int, discount: int, payment_method: str, paid_amount: int, buyer_name: str = None, receipt_path: str = None):
        """Process the order and save to database with stock validation"""
        try:
            # Fetch fresh products dari database untuk validasi stok yang akurat
            fresh_products = {p.id: p for p in ProductController.fetch()}
            
            # Validasi stok terbaru sebelum proses
            for product_id, (cart_product, quantity) in self._cart.items():
                fresh = fresh_products.get(product_id)
                
                if not fresh:
                    Toast.show_toast(
                        f"Produk {cart_product.name} tidak ditemukan di database.",
                        "error",
                        self
                    )
                    return
                
                fresh_stock = int(fresh.stock)
                if quantity > fresh_stock:
                    Toast.show_toast(
                        f"Stok {fresh.name} tidak cukup. Sisa stok: {fresh_stock}.",
                        "error",
                        self
                    )
                    return

            # Create sales record
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sales_id = SalesController.add_return_id(
                customer_id=None,
                cashier_id=self._user["id"],
                time=timestamp,
                payment=payment_method,
                paid_amount=paid_amount
            )

            # Track updated stocks untuk signal emit
            updated_stocks = {}

            # Add sales details dan validasi stock deduction
            for product_id, (cart_product, quantity) in self._cart.items():
                # Ambil produk fresh lagi untuk memastikan stok terbaru
                fresh = fresh_products[product_id]
                fresh_stock = int(fresh.stock)
                
                # Tambah sales detail
                SalesDetailController.add(
                    sales_id=sales_id,
                    product_id=product_id,
                    quantity=quantity,
                    discount=discount / len(self._cart) if len(self._cart) > 0 else 0
                )
                
                # Periksa apakah SalesDetailController sudah mengurangi stok
                # Jika belum, lakukan manual stock reduction
                # (Sesuaikan dengan implementasi SalesDetailController)
                # Untuk sekarang, asumsikan perlu manual update
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

            Toast.show_toast("Order berhasil disimpan", "success", self)

            # Emit signal untuk update stok di halaman lain
            for product_id, new_stock in updated_stocks.items():
                product_signals.product_stock_changed.emit(product_id, new_stock)
            
            # Emit signal untuk notifikasi transaksi selesai
            sales_signals.sales_completed.emit(sales_id)

            # Clear cart dan refresh
            self._cart = {}
            self._discount_input.setText("0")
            
            # Reload products dari database untuk tampilkan stok terbaru
            self._products = ProductController.fetch()
            self._filter_products()
            self._refresh_cart_display()

        except Exception as e:
            Toast.show_toast(f"Error: {str(e)}", "error", self)

    # ── Signal handlers untuk sinkronisasi dengan halaman lain ──────────────────
    def _on_product_added(self, product: Product):
        """Handle ketika produk baru ditambahkan dari halaman Produk"""
        if product not in self._products:
            self._products.append(product)
            self._filter_products()

    def _on_product_edited(self, product: Product):
        """Handle ketika produk diedit dari halaman Produk"""
        for i, p in enumerate(self._products):
            if p.id == product.id:
                self._products[i] = product
                break
        self._filter_products()

    def _on_product_deleted(self, product_id: int):
        """Handle ketika produk dihapus dari halaman Produk"""
        self._products = [p for p in self._products if p.id != product_id]
        # Hapus dari cart jika ada
        if product_id in self._cart:
            del self._cart[product_id]
            self._refresh_cart_display()
        self._filter_products()

    def _on_product_stock_changed(self, product_id: int, new_stock: int):
        """Handle ketika stok produk berubah"""
        for i, p in enumerate(self._products):
            if p.id == product_id:
                # Update stock
                from controllers.product import Product as ProductClass
                self._products[i] = ProductClass(
                    id=p.id,
                    name=p.name,
                    brand=p.brand,
                    sku=p.sku,
                    category=p.category,
                    price=p.price,
                    stock=new_stock,
                    image_path=p.image_path
                )
                break
        self._filter_products()

    def _on_products_imported(self, products: list):
        """Handle ketika produk baru diimport dari halaman Produk"""
        for product in products:
            if product not in self._products:
                self._products.append(product)
        self._filter_products()


# ═══════════════════════════════════════════════════════════════════════════════
# Receipt Preview Dialog - Compact struk-like layout
# ═══════════════════════════════════════════════════════════════════════════════
class ReceiptPreviewDialog(QDialog):
    def __init__(self, receipt_text: str, parent=None):
        super().__init__(parent)
        self._receipt_text = receipt_text
        self.action = "cancel"  # cancel, save, or print
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
        """Hitung tinggi preview berdasarkan jumlah baris struk"""
        lines = self._receipt_text.count("\n") + 1
        preview_height = min(max(lines * 13 + 60, 280), 420)
        self._receipt_view.setFixedHeight(preview_height)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────
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

        # ── Content (Receipt paper-like frame) ──────────────────────────
        content_frame = QFrame()
        content_frame.setStyleSheet(f"background: #FAFAF8;")
        content_lay = QVBoxLayout(content_frame)
        content_lay.setContentsMargins(0, 0, 0, 20)
        content_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Receipt paper frame
        receipt_paper = QFrame()
        receipt_paper.setFixedWidth(320)
        receipt_paper.setStyleSheet(f"""
            QFrame {{
                background: #FFFFFF;
                border: 1px solid #DDD9D2;
                border-radius: 10px;
            }}
        """)
        receipt_paper_lay = QVBoxLayout(receipt_paper)
        receipt_paper_lay.setContentsMargins(12, 12, 12, 12)
        receipt_paper_lay.setSpacing(0)

        # Receipt view
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
                margin: 0;
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

        # ── Footer ──────────────────────────────────────────────────────
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
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: #27AE60; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 12px; font-weight: 600;
                border-radius: 8px; border: none;
            }}
            QPushButton:hover {{ background: #229954; }}
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
        """Batal - jangan proses order"""
        self.action = "cancel"
        self.reject()

    def _on_save(self):
        """Save receipt to file dan accept dialog"""
        try:
            # Gunakan project root sebagai base
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
        """Print receipt dengan ukuran kecil, hanya area struk yang ada"""
        try:
            # Simpan file sebagai backup dulu
            project_root = Path(__file__).parent.parent.parent.parent
            receipts_dir = project_root / "assets" / "receipts"
            receipts_dir.mkdir(parents=True, exist_ok=True)
            
            receipt_file = receipts_dir / f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(receipt_file, 'w', encoding='utf-8') as f:
                f.write(self._receipt_text)
            
            # Setup printer untuk ukuran kecil (receipt/thermal printer style)
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setPageSize(QPrinter.PageSize.A6)  # Small paper size (105x148mm)
            printer.setMargins(5, 5, 5, 5, QPrinter.Unit.Millimeter)
            printer.setOrientation(QPrinter.Orientation.Portrait)
            
            print_dialog = QPrintDialog(printer, self)
            
            if print_dialog.exec() == QDialog.DialogCode.Accepted:
                # Create document dengan fixed width untuk receipt
                doc = QTextDocument()
                # Set monospace font dengan ukuran tetap
                font = QFont("Consolas", 8)
                font.setFixedPitch(True)
                doc.setDefaultFont(font)
                
                # Format text dengan preservasi whitespace
                html_text = "<pre style='margin: 0; padding: 0; font-size: 8pt; font-family: Consolas, monospace;'>"
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
    def __init__(self, cart: dict, subtotal: int, discount: int, total: int, user: dict, parent=None):
        super().__init__(parent)
        self._cart = cart
        self._subtotal = subtotal
        self._discount = discount
        self._total = total
        self._user = user
        self._payment_method = "tunai"
        self._buyer_name = ""
        self._cash_given = 0
        self._change = 0
        
        # Properties untuk menyimpan hasil preview
        self.receipt_action = "cancel"
        self.receipt_path = None
        self.buyer_name = ""
        self.payment_method = "tunai"
        self.cash_given = 0
        self.change = 0

        self.setWindowTitle("Konfirmasi Order")
        self.setModal(True)
        self.setFixedWidth(520)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        screen_h = QApplication.primaryScreen().availableGeometry().height()
        self.setMaximumHeight(min(700, screen_h - 80))
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

        # ── Header ──────────────────────────────────────────────────────
        header = QFrame()
        header.setStyleSheet("QFrame { background-color: #FAFAF8; }")
        header_lay = QVBoxLayout(header)
        header_lay.setContentsMargins(36, 30, 36, 0)
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

        subtitle = QLabel("Periksa kembali pesanan Anda sebelum memproses.")
        subtitle.setStyleSheet("font-size:12px;color:#888780;border:none;")
        header_lay.addWidget(subtitle)
        header_lay.addSpacing(16)

        root.addWidget(header)

        # ── Content ─────────────────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet("background: #FAFAF8;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(36, 0, 36, 30)
        cl.setSpacing(0)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider)
        cl.addSpacing(18)

        # ── Buyer Name ──────────────────────────────────────────────────
        buyer_label = QLabel("Nama Pembeli")
        buyer_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 600;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        cl.addWidget(buyer_label)
        cl.addSpacing(4)

        self._buyer_input = QLineEdit()
        self._buyer_input.setPlaceholderText("Opsional - Masukkan nama pembeli")
        self._buyer_input.setFixedHeight(36)
        self._buyer_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 6px;
                font-size: 11px;
                padding: 0 12px;
                color: {C_TEXT_PRI};
            }}
            QLineEdit::placeholder {{
                color: {C_TEXT_SEC};
            }}
        """)
        cl.addWidget(self._buyer_input)
        cl.addSpacing(16)

        # ── Order items (scroll untuk item banyak) ──────────────────────
        items_title = QLabel("Item Pesanan")
        items_title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 600;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        cl.addWidget(items_title)
        cl.addSpacing(8)

        # Scroll area untuk items jika banyak
        items_scroll = QScrollArea()
        items_scroll.setWidgetResizable(True)
        item_count = len(self._cart)
        items_height = min(max(item_count * 56, 100), 200)
        items_scroll.setFixedHeight(items_height)
        items_scroll.setFrameShape(QFrame.Shape.NoFrame)
        items_scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {C_BORDER};
                border-radius: 3px;
                min-height: 20px;
            }}
        """)

        items_container = QWidget()
        items_container.setStyleSheet("background: transparent;")
        items_layout = QVBoxLayout(items_container)
        items_layout.setContentsMargins(0, 0, 0, 0)
        items_layout.setSpacing(8)

        for product, quantity in self._cart.values():
            item_row = self._make_confirm_item_row(product, quantity)
            items_layout.addWidget(item_row)

        items_layout.addStretch()
        items_scroll.setWidget(items_container)
        cl.addWidget(items_scroll)
        cl.addSpacing(12)

        # ── Summary ─────────────────────────────────────────────────────
        divider2 = QFrame()
        divider2.setFixedHeight(1)
        divider2.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider2)
        cl.addSpacing(12)

        subtotal_row = QHBoxLayout()
        subtotal_row.addWidget(QLabel("Subtotal"))
        subtotal_row.addStretch()
        subtotal_row.addWidget(QLabel(_format_price(self._subtotal)))
        cl.addLayout(subtotal_row)
        cl.addSpacing(8)

        if self._discount > 0:
            discount_row = QHBoxLayout()
            discount_row.addWidget(QLabel("Diskon"))
            discount_row.addStretch()
            discount_val = QLabel(_format_price(self._discount))
            discount_val.setStyleSheet(f"color: {C_DANGER}; font-weight: 600;")
            discount_row.addWidget(discount_val)
            cl.addLayout(discount_row)
            cl.addSpacing(8)

        divider3 = QFrame()
        divider3.setFixedHeight(1)
        divider3.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider3)
        cl.addSpacing(12)

        total_row = QHBoxLayout()
        total_lbl = QLabel("Total")
        total_lbl.setStyleSheet("font-size:12px;font-weight:700;border:none;")
        total_row.addWidget(total_lbl)
        total_row.addStretch()
        total_val = QLabel(_format_price(self._total))
        total_val.setStyleSheet(f"font-size:13px;font-weight:700;color:{C_ACCENT};border:none;")
        total_row.addWidget(total_val)
        cl.addLayout(total_row)

        cl.addSpacing(16)

        # ── Payment Method ──────────────────────────────────────────────
        payment_label = QLabel("Metode Pembayaran")
        payment_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 600;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        cl.addWidget(payment_label)
        cl.addSpacing(8)

        # Payment method grid (2 rows x 3 cols, atau sesuai)
        self._payment_group = QButtonGroup()
        payment_grid = QGridLayout()
        payment_grid.setSpacing(8)
        payment_grid.setContentsMargins(0, 0, 0, 0)
        
        payment_methods = [
            ("tunai", "💵 Tunai"),
            ("debit", "💳 Debit"),
            ("kredit", "💳 Kredit"),
            ("qris", "📱 QRIS"),
            ("hutang", "📋 Hutang")
        ]

        for idx, (value, label) in enumerate(payment_methods):
            radio = QRadioButton(label)
            radio.setMinimumHeight(34)
            radio.setMinimumWidth(130)
            radio.setStyleSheet(f"""
                QRadioButton {{
                    color: {C_TEXT_PRI};
                    font-size: 10px;
                    font-weight: 500;
                    background: {C_WHITE};
                    border: 1px solid {C_BORDER};
                    border-radius: 8px;
                    padding: 0 10px;
                }}
                QRadioButton::indicator {{
                    width: 14px;
                    height: 14px;
                    border-radius: 7px;
                    border: 2px solid {C_BORDER};
                    background: {C_WHITE};
                    margin-right: 6px;
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
            """)
            if value == "tunai":
                radio.setChecked(True)
            radio.toggled.connect(lambda checked, v=value: self._on_payment_method_changed(v) if checked else None)
            self._payment_group.addButton(radio, idx)
            
            # Grid layout: row = idx // 3, col = idx % 3
            payment_grid.addWidget(radio, idx // 3, idx % 3)

        cl.addLayout(payment_grid)
        cl.addSpacing(12)

        # ── Cash Payment Fields (hanya tampil untuk tunai) ──────────────
        self._cash_fields_frame = QFrame()
        self._cash_fields_frame.setStyleSheet("background: transparent;")
        cash_layout = QVBoxLayout(self._cash_fields_frame)
        cash_layout.setContentsMargins(0, 0, 0, 0)
        cash_layout.setSpacing(12)

        # Amount given
        cash_label = QLabel("Uang yang Diberikan")
        cash_label.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 11px;
            font-weight: 600;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        cash_layout.addWidget(cash_label)

        self._cash_input = QLineEdit()
        self._cash_input.setPlaceholderText("0")
        self._cash_input.setFixedHeight(36)
        self._cash_input.setValidator(QIntValidator(0, 999_999_999))
        self._cash_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 6px;
                font-size: 11px;
                padding: 0 12px;
                color: {C_TEXT_PRI};
                font-weight: 500;
            }}
            QLineEdit:focus {{
                border: 1px solid {C_ACCENT};
            }}
        """)
        self._cash_input.textChanged.connect(self._on_cash_changed)
        cash_layout.addWidget(self._cash_input)

        # Change display
        change_row = QHBoxLayout()
        change_row.addWidget(QLabel("Kembalian"))
        change_row.addStretch()
        self._change_value = QLabel(_format_price(0))
        self._change_value.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {C_SUCCESS};
            border: none;
        """)
        change_row.addWidget(self._change_value)
        cash_layout.addLayout(change_row)

        cl.addWidget(self._cash_fields_frame)

        root.addWidget(content)

        # ── Footer ──────────────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet("QFrame { background-color: #FAFAF8; }")
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(36, 0, 36, 30)
        footer_lay.setSpacing(10)

        cancel_btn = QPushButton("Batal")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #5F5E5A;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 500;
                border-radius: 10px; border: 1px solid #DDD9D2;
            }
            QPushButton:hover { background: #F1EFE8; border: 1px solid #C8C6BF; }
        """)
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton("Proses & Cetak Struk")
        confirm_btn.setFixedHeight(40)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 600;
                border-radius: 10px; border: none;
            }}
            QPushButton:hover {{ background: {C_ACCENT_H}; }}
        """)
        confirm_btn.clicked.connect(lambda: self._on_confirm())

        footer_lay.addWidget(cancel_btn)
        footer_lay.addWidget(confirm_btn)

        root.addWidget(footer)

    def _make_confirm_item_row(self, product: Product, quantity: int) -> QFrame:
        """Create a compact item row for order confirmation"""
        row_frame = QFrame()
        row_frame.setFixedHeight(54)
        row_frame.setStyleSheet(f"""
            QFrame {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 8px;
            }}
        """)
        
        row_layout = QHBoxLayout(row_frame)
        row_layout.setContentsMargins(10, 8, 10, 8)
        row_layout.setSpacing(8)

        # Info panel (product name + price)
        info_widget = QWidget()
        info_widget.setMaximumWidth(260)
        info_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(1)

        # Product name with elide
        name_label = QLabel(product.name)
        name_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(28)
        from PyQt6.QtGui import QFontMetrics
        metrics = QFontMetrics(name_label.font())
        elided = metrics.elidedText(product.name, Qt.TextElideMode.ElideRight, 200)
        name_label.setText(elided)
        info_layout.addWidget(name_label)

        # Product price
        price_label = QLabel(_format_price(product.price))
        price_label.setStyleSheet(f"""
            font-size: 10px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        info_layout.addWidget(price_label)
        info_layout.addStretch()
        
        row_layout.addWidget(info_widget)

        # Quantity
        qty_label = QLabel(f"x{quantity}")
        qty_label.setFixedWidth(36)
        qty_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        qty_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            color: {C_ACCENT};
            background: transparent;
            border: none;
        """)
        row_layout.addWidget(qty_label)

        # Total price (right aligned)
        total_label = QLabel(_format_price(product.price * quantity))
        total_label.setFixedWidth(90)
        total_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        row_layout.addWidget(total_label)

        return row_frame

    def _on_payment_method_changed(self, method: str):
        """Handle payment method change"""
        self._payment_method = method
        if method == "tunai":
            self._cash_fields_frame.show()
        else:
            self._cash_fields_frame.hide()
        self.adjustSize()

    def _on_cash_changed(self):
        """Calculate change when cash amount changes"""
        try:
            cash_str = self._cash_input.text().strip()
            if cash_str:
                self._cash_given = int(cash_str)
            else:
                self._cash_given = 0
            
            self._change = self._cash_given - self._total
            
            if self._change < 0:
                self._change_value.setText(f"Kurang {_format_price(abs(self._change))}")
                self._change_value.setStyleSheet(f"""
                    font-size: 11px;
                    font-weight: 600;
                    color: {C_DANGER};
                    border: none;
                """)
            else:
                self._change_value.setText(_format_price(self._change))
                self._change_value.setStyleSheet(f"""
                    font-size: 11px;
                    font-weight: 600;
                    color: {C_SUCCESS};
                    border: none;
                """)
        except ValueError:
            self._change_value.setText("Format tidak valid")
            self._change_value.setStyleSheet(f"""
                font-size: 11px;
                font-weight: 600;
                color: {C_DANGER};
                border: none;
            """)

    def _on_confirm(self):
        """Validate pembayaran, show receipt preview, dan handle acceptance"""
        # Validate payment method
        if self._payment_method == "tunai":
            cash_str = self._cash_input.text().strip()
            if not cash_str or int(cash_str) == 0:
                Toast.show_toast("Masukkan jumlah uang tunai!", "error", self)
                return
            if int(cash_str) < self._total:
                Toast.show_toast("Uang tunai tidak cukup!", "error", self)
                return

        # Build receipt text
        receipt_text = self._build_receipt_text()
        
        # Show preview dialog
        preview_dialog = ReceiptPreviewDialog(receipt_text, self)
        
        # Jika user accept (Simpan atau Cetak)
        if preview_dialog.exec() == QDialog.DialogCode.Accepted:
            # Simpan metadata hasil preview ke dialog properties
            self.receipt_action = preview_dialog.action
            self.receipt_path = preview_dialog.saved_path
            self.buyer_name = self._buyer_input.text().strip()
            self.payment_method = self._payment_method
            self.cash_given = self._cash_given if self._payment_method == "tunai" else self._total
            self.change = self._change if self._payment_method == "tunai" else 0
            
            # Accept dialog
            self.accept()
        # Jika user cancel atau reject, jangan accept dialog

    def _build_receipt_text(self) -> str:
        """Build formatted receipt text (36-char fixed width)"""
        RECEIPT_WIDTH = 36
        
        def _line(char: str = "-") -> str:
            return char * RECEIPT_WIDTH
        
        def _center(text: str) -> str:
            return text.center(RECEIPT_WIDTH)
        
        def _truncate(text: str, max_len: int) -> str:
            if len(text) > max_len:
                return text[:max_len - 1] + "…"
            return text
        
        def _row(left: str, right: str) -> str:
            # Align left text to left, right text to right
            left_str = _truncate(left, RECEIPT_WIDTH - 12)
            right_str = _format_price(right) if isinstance(right, int) else str(right)
            spaces = RECEIPT_WIDTH - len(left_str) - len(right_str)
            return left_str + " " * max(1, spaces) + right_str

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_name = self._user.get("name", "Cashier")
        buyer_name = self._buyer_input.text().strip() or "Pembeli Umum"

        payment_display = {
            "tunai": "Tunai",
            "debit": "Kartu Debit",
            "kredit": "Kartu Kredit",
            "qris": "QRIS",
            "hutang": "Hutang"
        }
        payment_text = payment_display.get(self._payment_method, "Tunai")

        lines = [
            _center("WARUNG+"),
            _center("Tanda Terima"),
            _line("="),
            "",
            _row("Tgl", timestamp),
            _row("Kasir", user_name),
            _row("Pembeli", buyer_name),
            "",
            _line("-"),
            _center("BARANG BELANJA"),
            _line("-"),
        ]

        for product, quantity in self._cart.values():
            name = _truncate(product.name, RECEIPT_WIDTH)
            lines.append(name)
            item_total = product.price * quantity
            price_line = f"{quantity}x @ {_format_price(product.price)}"
            lines.append(_row(price_line, item_total))
            lines.append("")

        lines.extend([
            _line("-"),
            _row("Subtotal", self._subtotal),
        ])

        # Diskon selalu tampil untuk konsistensi
        lines.append(_row("Diskon", self._discount))

        lines.extend([
            _line("="),
            _row("TOTAL", self._total),
            "",
            _line("-"),
            _row("Metode", payment_text),
        ])

        if self._payment_method == "tunai":
            lines.extend([
                _row("Tunai", self._cash_given),
                _row("Kembali", self._change),
            ])

        lines.extend([
            _line("-"),
            _center("Terima Kasih!"),
            _center("WARUNG+"),
            _line("="),
        ])

        return "\n".join(lines)