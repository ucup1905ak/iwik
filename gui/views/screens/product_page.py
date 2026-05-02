# views/screens/product_page.py
from controllers.product import ProductController, Product
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
    QFormLayout,
    QMessageBox,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor


# ── Color palette ─────────────────────────────────────────────────────────────
C_BG        = "#F4F5F9"
C_WHITE     = "#FFFFFF"
C_ACCENT    = "#4F6EF7"
C_ACCENT_H  = "#3A57E8"
C_TEXT_PRI  = "#1A1D2E"
C_TEXT_SEC  = "#6B6F80"
C_BORDER    = "#E4E6EE"
C_DANGER    = "#E05252"
C_TAG_BG    = "#EEF1FE"
C_TAG_TEXT  = "#4F6EF7"

# Matikan shadow dulu untuk menghindari repaint lambat di scroll/grid.
# Kalau setelah fix semua stabil dan ingin shadow kembali, ubah ke True.
ENABLE_CARD_SHADOWS = False


# ── Sample data ───────────────────────────────────────────────────────────────
SAMPLE_CATEGORIES = ["Semua", "Makanan", "Minuman", "Snack", "Sembako", "Lainnya"]

SAMPLE_PRODUCTS = [
    Product(id=1,  name="Nasi Goreng Spesial", brand=None, sku="MKN-001", category="Makanan", stock=50,  price=25000),
    Product(id=2,  name="Es Teh Manis",         brand=None, sku="MNM-001", category="Minuman", stock=120, price=5000),
    Product(id=3,  name="Keripik Singkong",     brand=None, sku="SNK-001", category="Snack",   stock=75,  price=8000),
    Product(id=4,  name="Mie Goreng",           brand=None, sku="MKN-002", category="Makanan", stock=30,  price=20000),
    Product(id=5,  name="Kopi Hitam",           brand=None, sku="MNM-002", category="Minuman", stock=90,  price=7000),
    Product(id=6,  name="Beras 5kg",            brand=None, sku="SMB-001", category="Sembako", stock=20,  price=65000),
    Product(id=7,  name="Teh Botol",            brand=None, sku="MNM-003", category="Minuman", stock=200, price=6000),
    Product(id=8,  name="Chiki Snack",          brand=None, sku="SNK-002", category="Snack",   stock=150, price=3000),
    Product(id=9,  name="Ayam Bakar",           brand=None, sku="MKN-003", category="Makanan", stock=15,  price=30000),
    Product(id=10, name="Gula Pasir 1kg",       brand=None, sku="SMB-002", category="Sembako", stock=40,  price=14000),
    Product(id=11, name="Jus Jeruk",            brand=None, sku="MNM-004", category="Minuman", stock=35,  price=12000),
    Product(id=12, name="Pisang Goreng",        brand=None, sku="SNK-003", category="Snack",   stock=0,   price=2000),
]


# ── Category emoji ────────────────────────────────────────────────────────────
CAT_EMOJI = {
    "Makanan": "🍽️",
    "Minuman": "🥤",
    "Snack": "🍿",
    "Sembako": "🛒",
    "Lainnya": "📦",
}


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


# ═════════════════════════════════════════════════════════════════════════════
# Product Card
# ═════════════════════════════════════════════════════════════════════════════
class ProductCard(QFrame):
    edit_clicked   = pyqtSignal(Product)
    delete_clicked = pyqtSignal(Product)

    def __init__(self, product: Product, parent=None):
        super().__init__(parent)
        self._product = product
        self._build()

    def _build(self):
        product = self._product
        stock = product.stock

        self.setObjectName("ProductCard")
        self.setStyleSheet(f"""
            QFrame#ProductCard {{
                background: {C_WHITE};
                border-radius: 14px;
                border: 1px solid {C_BORDER};
            }}
        """)
        _apply_card_shadow(self)
        self.setFixedHeight(170)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        top = QHBoxLayout()

        cat_tag = QLabel(f"{CAT_EMOJI.get(product.category, '📦')} {product.category}")
        cat_tag.setStyleSheet(f"""
            background: {C_TAG_BG};
            color: {C_TAG_TEXT};
            font-family: 'Segoe UI';
            font-size: 10px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            border: none;
        """)

        if stock == 0:
            stock_color, stock_bg, stock_text = "#E05252", "#FDEAEA", "Habis"
        elif stock < 20:
            stock_color, stock_bg, stock_text = "#E07D2A", "#FDF3EA", f"Sisa {stock}"
        else:
            stock_color, stock_bg, stock_text = "#27AE60", "#E8F8F0", f"Stok {stock}"

        stock_badge = QLabel(stock_text)
        stock_badge.setStyleSheet(f"""
            background: {stock_bg};
            color: {stock_color};
            font-family: 'Segoe UI';
            font-size: 10px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            border: none;
        """)

        top.addWidget(cat_tag)
        top.addStretch()
        top.addWidget(stock_badge)
        layout.addLayout(top)

        name_lbl = QLabel(product.name)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 14px;
            font-weight: 700;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        layout.addWidget(name_lbl)

        brand_text = product.brand
        if brand_text:
            brand_lbl = QLabel(f"Merek: {brand_text}")
            brand_lbl.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size: 11px;
                color: {C_TEXT_SEC};
                background: transparent;
                border: none;
            """)
            layout.addWidget(brand_lbl)

        sku_lbl = QLabel(f"SKU: {product.sku}")
        sku_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 10px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        layout.addWidget(sku_lbl)

        layout.addStretch()

        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        price_lbl = QLabel(_format_price(product.price))
        price_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 15px;
            font-weight: 700;
            color: {C_ACCENT};
            background: transparent;
            border: none;
        """)

        edit_btn = QPushButton("Edit")
        edit_btn.setFixedHeight(30)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_TAG_BG};
                color: {C_ACCENT};
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: 600;
                border-radius: 7px;
                padding: 0 14px;
                border: none;
            }}
            QPushButton:hover {{
                background: {C_ACCENT};
                color: #FFFFFF;
            }}
        """)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self._product))

        del_btn = QPushButton("Hapus")
        del_btn.setFixedHeight(30)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FDEAEA;
                color: {C_DANGER};
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: 600;
                border-radius: 7px;
                padding: 0 14px;
                border: none;
            }}
            QPushButton:hover {{
                background: {C_DANGER};
                color: #FFFFFF;
            }}
        """)
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(self._product))

        bottom.addWidget(price_lbl)
        bottom.addStretch()
        bottom.addWidget(edit_btn)
        bottom.addWidget(del_btn)

        layout.addLayout(bottom)


# ═════════════════════════════════════════════════════════════════════════════
# Add / Edit Product Dialog
# ═════════════════════════════════════════════════════════════════════════════
class ProductDialog(QDialog):
    saved = pyqtSignal(dict)

    def __init__(self, product: Product = None, parent=None):
        super().__init__(parent)
        self._product = product
        self._edit_mode = product is not None

        self.setWindowTitle("Edit Produk" if self._edit_mode else "Tambah Produk")
        self.setModal(True)
        self.setFixedSize(440, 470)
        self.setStyleSheet(f"""
            QDialog {{
                background: {C_WHITE};
                font-family: 'Segoe UI';
            }}
        """)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(0)

        title = QLabel("Edit Produk" if self._edit_mode else "Tambah Produk Baru")
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 18px;
            font-weight: 700;
            color: {C_TEXT_PRI};
        """)
        layout.addWidget(title)
        layout.addSpacing(4)

        sub = QLabel("Isi detail produk dengan lengkap dan benar.")
        sub.setStyleSheet(f"font-size: 12px; color: {C_TEXT_SEC};")
        layout.addWidget(sub)
        layout.addSpacing(20)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        def _field(placeholder=""):
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setFixedHeight(38)
            field.setStyleSheet(f"""
                QLineEdit {{
                    background: {C_BG};
                    border: 1px solid {C_BORDER};
                    border-radius: 8px;
                    padding: 0 12px;
                    font-size: 13px;
                    color: {C_TEXT_PRI};
                    font-family: 'Segoe UI';
                }}
                QLineEdit:focus {{
                    border: 1.5px solid {C_ACCENT};
                    background: {C_WHITE};
                }}
            """)
            return field

        def _label(text):
            label = QLabel(text)
            label.setStyleSheet(
                f"font-size: 12px; font-weight: 600; color: {C_TEXT_PRI}; font-family: 'Segoe UI';"
            )
            return label

        self._name_field  = _field("Nama produk")
        self._brand_field = _field("Merek produk")
        self._sku_field   = _field("SKU-001")
        self._price_field = _field("0")
        self._stock_field = _field("0")

        self._cat_combo = QComboBox()
        self._cat_combo.setFixedHeight(38)
        self._cat_combo.setStyleSheet(f"""
            QComboBox {{
                background: {C_BG};
                border: 1px solid {C_BORDER};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 13px;
                color: {C_TEXT_PRI};
                font-family: 'Segoe UI';
            }}
            QComboBox:focus {{ border: 1.5px solid {C_ACCENT}; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
        """)
        for cat in SAMPLE_CATEGORIES[1:]:
            self._cat_combo.addItem(cat)

        form.addRow(_label("Nama Produk"), self._name_field)
        form.addRow(_label("Merek"),       self._brand_field)
        form.addRow(_label("SKU"),         self._sku_field)
        form.addRow(_label("Kategori"),    self._cat_combo)
        form.addRow(_label("Harga (Rp)"),  self._price_field)
        form.addRow(_label("Stok"),        self._stock_field)

        layout.addLayout(form)
        layout.addStretch()

        if self._edit_mode:
            product = self._product
            self._name_field.setText(product.name)
            self._brand_field.setText(product.brand or "")
            self._sku_field.setText(product.sku or "")
            self._price_field.setText(str(product.price))
            self._stock_field.setText(str(product.stock))

            idx = self._cat_combo.findText(product.category or "")
            if idx >= 0:
                self._cat_combo.setCurrentIndex(idx)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Batal")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_BG};
                color: {C_TEXT_SEC};
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
                border-radius: 10px;
                border: 1px solid {C_BORDER};
            }}
            QPushButton:hover {{ background: {C_BORDER}; }}
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Simpan Produk")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT};
                color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
                border-radius: 10px;
                border: none;
            }}
            QPushButton:hover {{ background: {C_ACCENT_H}; }}
        """)
        save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_save(self):
        name = self._name_field.text().strip()
        brand = self._brand_field.text().strip()
        sku = self._sku_field.text().strip()
        category = self._cat_combo.currentText()
        price = self._price_field.text().replace(".", "").replace(",", "")
        stock = self._stock_field.text()

        if not name:
            self._name_field.setStyleSheet(self._name_field.styleSheet() + "border: 1.5px solid #E05252;")
            return

        data = {
            "id":       self._product.id if self._edit_mode else None,
            "name":     name,
            "brand":    brand,
            "sku":      sku,
            "category": category,
            "price":    price,
            "stock":    stock,
        }
        self.saved.emit(data)
        self.accept()


# ═════════════════════════════════════════════════════════════════════════════
# Product Page
# ═════════════════════════════════════════════════════════════════════════════
class ProductPage(QWidget):
    def __init__(self, user: dict = None, parent=None):
        super().__init__(parent)
        self._user = user or {}

        self._products = self._load_products()
        self._active_category = "Semua"
        self._search_query = ""

        self._grid_initialized = False
        self._render_token = 0
        self._pending_refresh = False
        self._stat_value_labels: dict[str, tuple[QLabel, QLabel]] = {}

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C_BG};")
        self._build_ui()

    def _load_products(self) -> list[Product]:
        return ProductController.fetch()

        # Jangan render grid di constructor.
        # Render pertama dilakukan di showEvent agar widget sudah visible di QStackedWidget.

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(0)

        header = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Manajemen Produk")
        page_title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 22px;
            font-weight: 700;
            color: {C_TEXT_PRI};
            background: transparent;
        """)

        subtitle = QLabel("Kelola semua produk warungmu di sini")
        subtitle.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 13px;
            color: {C_TEXT_SEC};
            background: transparent;
        """)

        title_col.addWidget(page_title)
        title_col.addWidget(subtitle)

        add_btn = QPushButton("+ Tambah Produk")
        add_btn.setFixedHeight(42)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT};
                color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
                border-radius: 10px;
                padding: 0 20px;
                border: none;
            }}
            QPushButton:hover {{ background: {C_ACCENT_H}; }}
        """)
        add_btn.clicked.connect(self._open_add_dialog)

        header.addLayout(title_col)
        header.addStretch()
        header.addWidget(add_btn)

        layout.addLayout(header)
        layout.addSpacing(20)

        layout.addLayout(self._build_stats_row())
        layout.addSpacing(20)

        layout.addLayout(self._build_filter_bar())
        layout.addSpacing(16)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet("background: transparent;")
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet("background: transparent;")
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(14)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)

        self._scroll.setWidget(self._grid_container)
        layout.addWidget(self._scroll, stretch=1)

    def _calc_stats(self) -> dict[str, str]:
        total = len(self._products)
        out_stock = sum(1 for p in self._products if p.stock == 0)
        low_stock = sum(1 for p in self._products if 0 < p.stock < 20)
        categories = len(set(p.category for p in self._products if p.category))

        return {
            "total": str(total),
            "out_stock": str(out_stock),
            "low_stock": str(low_stock),
            "categories": str(categories),
        }

    def _build_stats_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(14)

        values = self._calc_stats()

        stats = [
            ("total",      "Total Produk", values["total"],      "#4F6EF7", "#EEF1FE"),
            ("out_stock",  "Stok Habis",   values["out_stock"],  "#E05252", "#FDEAEA"),
            ("low_stock",  "Stok Menipis", values["low_stock"],  "#E07D2A", "#FDF3EA"),
            ("categories", "Kategori",     values["categories"], "#27AE60", "#E8F8F0"),
        ]

        for key, label, value, color, bg in stats:
            row.addWidget(self._stat_card(key, label, value, color, bg))

        return row

    def _stat_card(self, key: str, label: str, value: str, color: str, bg: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {C_WHITE};
                border-radius: 12px;
                border: 1px solid {C_BORDER};
            }}
        """)
        card.setFixedHeight(76)
        _apply_card_shadow(card)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        indicator = QFrame()
        indicator.setFixedSize(40, 40)
        indicator.setStyleSheet(f"background: {bg}; border-radius: 10px; border: none;")

        dot = QLabel(value)
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dot.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 18px;
            font-weight: 700;
            color: {color};
            background: transparent;
            border: none;
        """)
        dot.setParent(indicator)
        dot.setGeometry(0, 0, 40, 40)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 22px;
            font-weight: 700;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)

        lbl_lbl = QLabel(label)
        lbl_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 11px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)

        self._stat_value_labels[key] = (dot, val_lbl)

        text_col.addWidget(val_lbl)
        text_col.addWidget(lbl_lbl)

        layout.addWidget(indicator)
        layout.addLayout(text_col)
        layout.addStretch()

        return card

    def _build_filter_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("🔍  Cari produk...")
        search.setFixedHeight(38)
        search.setStyleSheet(f"""
            QLineEdit {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
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
        search.textChanged.connect(self._on_search_changed)
        search.setMinimumWidth(240)

        bar.addWidget(search)
        bar.addSpacing(6)

        self._cat_buttons: dict[str, QPushButton] = {}
        for cat in SAMPLE_CATEGORIES:
            btn = self._cat_btn(cat)
            self._cat_buttons[cat] = btn
            bar.addWidget(btn)

        bar.addStretch()
        return bar

    def _cat_btn(self, cat: str) -> QPushButton:
        is_active = cat == self._active_category
        btn = QPushButton(cat)
        btn.setFixedHeight(36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_cat_btn(btn, is_active)
        btn.clicked.connect(lambda checked, selected=cat: self._on_cat_changed(selected))
        return btn

    def _style_cat_btn(self, btn: QPushButton, active: bool):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C_ACCENT};
                    color: #FFFFFF;
                    font-family: 'Segoe UI';
                    font-size: 12px;
                    font-weight: 600;
                    border-radius: 8px;
                    padding: 0 14px;
                    border: none;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C_WHITE};
                    color: {C_TEXT_SEC};
                    font-family: 'Segoe UI';
                    font-size: 12px;
                    font-weight: 400;
                    border-radius: 8px;
                    padding: 0 14px;
                    border: 1px solid {C_BORDER};
                }}
                QPushButton:hover {{
                    background: {C_TAG_BG};
                    color: {C_ACCENT};
                    border: 1px solid {C_ACCENT};
                }}
            """)

    # ── Data / filter logic ───────────────────────────────────────────────────
    def _filtered_products(self) -> list[Product]:
        result = self._products

        if self._active_category != "Semua":
            result = [p for p in result if p.category == self._active_category]

        if self._search_query:
            query = self._search_query.lower()
            result = [
                p for p in result
                if query in p.name.lower() or (p.sku and query in p.sku.lower())
            ]

        return result

    def _clear_grid(self):
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

    def _refresh_grid(self):
        self._render_token += 1
        token = self._render_token

        if not self.isVisible():
            self._pending_refresh = True
            return

        self._pending_refresh = False
        self._clear_grid()

        products = self._filtered_products()

        if not products:
            empty = QLabel("Tidak ada produk ditemukan.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size: 14px;
                color: {C_TEXT_SEC};
                padding: 60px;
            """)
            self._grid_layout.addWidget(empty, 0, 0, 1, 3)
            self._grid_container.adjustSize()
            self._grid_container.update()
            self._scroll.viewport().update()
            return

        # Dataset sample kecil: render langsung agar tidak terasa muncul bertahap.
        # Jika nanti data besar, batch rendering tetap tersedia.
        if len(products) <= 60:
            self._render_all_cards(products, token)
        else:
            self._render_batch_cards(products, 0, batch_size=12, token=token)

    def _render_all_cards(self, products: list[Product], token: int):
        if token != self._render_token:
            return
        if not self.isVisible():
            self._pending_refresh = True
            return

        cols = 3

        for i, product in enumerate(products):
            card = ProductCard(product)
            card.edit_clicked.connect(self._open_edit_dialog)
            card.delete_clicked.connect(self._delete_product)
            self._grid_layout.addWidget(card, i // cols, i % cols)

        self._fill_grid_remainder(len(products), cols)
        self._grid_container.adjustSize()
        self._grid_container.update()
        self._scroll.viewport().update()

    def _render_batch_cards(
        self,
        products: list[Product],
        start_idx: int,
        batch_size: int = 12,
        token: int | None = None,
    ):
        if token is None:
            token = self._render_token
        if token != self._render_token:
            return
        if not self.isVisible():
            self._pending_refresh = True
            return

        end_idx = min(start_idx + batch_size, len(products))
        cols = 3

        for i in range(start_idx, end_idx):
            product = products[i]
            card = ProductCard(product)
            card.edit_clicked.connect(self._open_edit_dialog)
            card.delete_clicked.connect(self._delete_product)
            self._grid_layout.addWidget(card, i // cols, i % cols)

        self._grid_container.adjustSize()
        self._grid_container.update()
        self._scroll.viewport().update()

        if end_idx < len(products):
            QTimer.singleShot(
                0,
                lambda idx=end_idx, t=token: self._render_batch_cards(products, idx, batch_size, t),
            )
        else:
            self._fill_grid_remainder(len(products), cols)

    def _fill_grid_remainder(self, item_count: int, cols: int):
        remainder = item_count % cols
        if not remainder:
            return

        row = item_count // cols
        for j in range(cols - remainder):
            spacer = QWidget()
            spacer.setStyleSheet("background: transparent;")
            self._grid_layout.addWidget(spacer, row, remainder + j)

    def _refresh_stats(self):
        values = self._calc_stats()

        for key, value in values.items():
            labels = self._stat_value_labels.get(key)
            if labels:
                dot, val_lbl = labels
                dot.setText(value)
                val_lbl.setText(value)

    # ── Events ────────────────────────────────────────────────────────────────
    def _on_search_changed(self, text: str):
        self._search_query = text.strip()
        self._refresh_grid()

    def _on_cat_changed(self, cat: str):
        old_btn = self._cat_buttons.get(self._active_category)
        if old_btn:
            self._style_cat_btn(old_btn, False)

        self._active_category = cat

        new_btn = self._cat_buttons.get(cat)
        if new_btn:
            self._style_cat_btn(new_btn, True)

        self._refresh_grid()

    def _open_add_dialog(self):
        dlg = ProductDialog(parent=self)
        dlg.saved.connect(self._add_product)
        dlg.exec()

    def _open_edit_dialog(self, product: Product):
        dlg = ProductDialog(product=product, parent=self)
        dlg.saved.connect(self._update_product)
        dlg.exec()

    def _add_product(self, data: dict):
        try:
            ProductController.add(
                name=data["name"],
                price=data["price"],
                stock=data["stock"],
                brand=data.get("brand"),
                sku=data["sku"],
                category=data["category"]
            )
            self._products = self._load_products()
            self._refresh_stats()
            self._refresh_grid()
        except TypeError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _update_product(self, data: dict):
        try:
            ProductController.edit(
                product_id=data["id"],
                name=data["name"],
                brand=data.get("brand"),
                stock=data["stock"],
                price=data["price"],
                sku=data["sku"],
                category=data["category"]
            )
            self._products = self._load_products()
            self._refresh_stats()
            self._refresh_grid()
        except TypeError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _delete_product(self, product: Product):
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Hapus Produk")
        confirm.setText(f"Hapus <b>{product.name}</b>?")
        confirm.setInformativeText("Tindakan ini tidak dapat dibatalkan.")
        confirm.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        confirm.setDefaultButton(QMessageBox.StandardButton.Cancel)
        confirm.setStyleSheet(f"""
            QMessageBox {{
                background: {C_WHITE};
                font-family: 'Segoe UI';
            }}
            QPushButton {{
                min-width: 80px;
                height: 32px;
                border-radius: 8px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
                border: none;
            }}
        """)

        if confirm.exec() == QMessageBox.StandardButton.Yes:
            try:
                ProductController.remove(product.id)
                self._products = self._load_products()
                self._refresh_stats()
                self._refresh_grid()
            except TypeError as e:
                QMessageBox.critical(self, "Error", str(e))

    def showEvent(self, event):
        super().showEvent(event)

        if not self._grid_initialized or self._pending_refresh:
            self._grid_initialized = True
            self._pending_refresh = False
            QTimer.singleShot(0, self._refresh_grid)