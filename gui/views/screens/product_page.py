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
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QRegion

# ── Color palette ──────────────────────────────────────────────────────────────
C_BG       = "#F4F5F9"
C_WHITE    = "#FFFFFF"
C_ACCENT   = "#4F6EF7"
C_ACCENT_H = "#3A57E8"
C_TEXT_PRI = "#1A1D2E"
C_TEXT_SEC = "#6B6F80"
C_BORDER   = "#E4E6EE"
C_DANGER   = "#E05252"
C_TAG_BG   = "#EEF1FE"
C_TAG_TEXT = "#4F6EF7"

ENABLE_CARD_SHADOWS = False
RADIUS = 14

SAMPLE_CATEGORIES = ["Semua", "Makanan", "Minuman", "Snack", "Sembako", "Lainnya"]

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


# ═══════════════════════════════════════════════════════════════════════════════
# Product Card
# ═══════════════════════════════════════════════════════════════════════════════
class ProductCard(QFrame):
    edit_clicked   = pyqtSignal(Product)
    delete_clicked = pyqtSignal(Product)

    CARD_WIDTH  = 320
    CARD_HEIGHT = 170

    def __init__(self, product: Product, parent=None):
        super().__init__(parent)
        self._product = product
        self._build()

    def _build(self):
        product = self._product
        stock   = product.stock

        self.setObjectName("ProductCard")
        self.setFixedHeight(170)

        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.setStyleSheet(f"""
            QFrame#ProductCard {{
                background: {C_WHITE};
                border-radius: 14px;
                border: 1px solid {C_BORDER};
            }}
        """)
        _apply_card_shadow(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # ── Top row ──────────────────────────────────────────────────────────
        top = QHBoxLayout()
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
        layout.addLayout(top)

        # ── Name ──────────────────────────────────────────────────────────────
        name_lbl = QLabel(product.name)
        name_lbl.setWordWrap(True)
        name_lbl.setMaximumHeight(40)
        name_lbl.setStyleSheet(f"""
            font-family:  'Segoe UI';
            font-size:    14px;
            font-weight:  700;
            color:        {C_TEXT_PRI};
            background:   transparent;
            border:       none;
        """)
        layout.addWidget(name_lbl)

        # ── Brand ─────────────────────────────────────────────────────────────
        if product.brand:
            brand_lbl = QLabel(f"Merek: {product.brand}")
            brand_lbl.setMaximumHeight(18)
            brand_lbl.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size:   11px;
                color:       {C_TEXT_SEC};
                background:  transparent;
                border:      none;
            """)
            layout.addWidget(brand_lbl)

        # ── SKU ───────────────────────────────────────────────────────────────
        sku_lbl = QLabel(f"SKU: {product.sku}")
        sku_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   10px;
            color:       {C_TEXT_SEC};
            background:  transparent;
            border:      none;
        """)
        layout.addWidget(sku_lbl)
        layout.addStretch()

        # ── Bottom row ────────────────────────────────────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        price_lbl = QLabel(_format_price(product.price))
        price_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   15px;
            font-weight: 700;
            color:       {C_ACCENT};
            background:  transparent;
            border:      none;
        """)

        edit_btn = QPushButton("Edit")
        edit_btn.setFixedSize(60, 30)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background:    {C_TAG_BG};
                color:         {C_ACCENT};
                font-family:   'Segoe UI';
                font-size:     11px;
                font-weight:   600;
                border-radius: 7px;
                border:        none;
            }}
            QPushButton:hover {{
                background: {C_ACCENT};
                color:      #FFFFFF;
            }}
        """)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self._product))

        del_btn = QPushButton("Hapus")
        del_btn.setFixedSize(70, 30)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background:    #FDEAEA;
                color:         {C_DANGER};
                font-family:   'Segoe UI';
                font-size:     11px;
                font-weight:   600;
                border-radius: 7px;
                border:        none;
            }}
            QPushButton:hover {{
                background: {C_DANGER};
                color:      #FFFFFF;
            }}
        """)
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(self._product))

        bottom.addWidget(price_lbl)
        bottom.addStretch()
        bottom.addWidget(edit_btn)
        bottom.addWidget(del_btn)
        layout.addLayout(bottom)


# ═══════════════════════════════════════════════════════════════════════════════
# Product Table View
# ═══════════════════════════════════════════════════════════════════════════════
class ProductTableView(QTableWidget):
    edit_clicked   = pyqtSignal(Product)
    delete_clicked = pyqtSignal(Product)

    COLUMNS      = ["      #", "Nama Produk", "SKU", "Kategori", "Harga", "Stok", "Aksi"]
    COL_NO       = 0
    COL_NAME     = 1
    COL_SKU      = 2
    COL_CATEGORY = 3
    COL_PRICE    = 4
    COL_STOCK    = 5
    COL_ACTION   = 6
    ROW_H        = 52

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_table()

    # ── Viewport clip (rounded mask) ──────────────────────────────────────────
    def _apply_viewport_clip(self):
        vp = self.viewport()
        w, h = vp.width(), vp.height()
        if w <= 0 or h <= 0:
            return
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, RADIUS, RADIUS)
        region = QRegion(path.toFillPolygon().toPolygon())
        vp.setMask(region)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._apply_viewport_clip)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._apply_viewport_clip)

    def _setup_table(self):
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)

        # ===== TABLE BEHAVIOR =====
        self.setAlternatingRowColors(True)  # 🔥 MATIKAN ZEBRA TOTAL
        self.setShowGrid(True)
        self.setGridStyle(Qt.PenStyle.SolidLine)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.verticalHeader().setVisible(False)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMouseTracking(True)

        self.setCornerButtonEnabled(False)

        # penting biar background tidak “layer aneh”
        self.viewport().setAutoFillBackground(True)

        # ===== HEADER =====
        header = self.horizontalHeader()
        header.setHighlightSections(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setStretchLastSection(False)
        header.setFixedHeight(42)

        header.setSectionResizeMode(self.COL_NO,       QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_NAME,     QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COL_SKU,      QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_CATEGORY, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_PRICE,    QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_STOCK,    QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_ACTION,   QHeaderView.ResizeMode.Fixed)

        self.setColumnWidth(self.COL_NO,       44)
        self.setColumnWidth(self.COL_SKU,      110)
        self.setColumnWidth(self.COL_CATEGORY, 140)
        self.setColumnWidth(self.COL_PRICE,    160)
        self.setColumnWidth(self.COL_STOCK,    130)
        self.setColumnWidth(self.COL_ACTION,   200)

        # ===== STYLE =====
        self.setStyleSheet(f"""
            QTableWidget {{
                background: {C_WHITE};

                border: 1.5px solid {C_BORDER};
                border-radius: {RADIUS}px;

                font-family: 'Segoe UI';
                font-size: 13px;
                color: {C_TEXT_PRI};

                outline: none;

                gridline-color: {C_DIVIDER};
            }}
            
            QTableWidget {{
                background: {C_WHITE};
                alternate-background-color: #F7F9FC;
            }}

            QTableWidget::viewport {{
                background: {C_WHITE};   /* 🔥 FIX utama: hilangkan layer abu-abu */
            }}

            QTableWidget::item {{
                background: transparent;   /* 🔥 jangan override per cell */
                border: none;

                border-right: 1px solid {C_DIVIDER};
                border-bottom: 1px solid {C_DIVIDER};

                padding: 6px 10px;
            }}

            QTableWidget::item:selected {{
                background: #E6EEF9;
            }}

            QTableCornerButton::section {{
                background: {C_HEADER_BG};
                border: none;
                border-top-left-radius: {RADIUS}px;
            }}

            QHeaderView {{
                background: transparent;
                border: none;
            }}

            QHeaderView::section {{
                background: {C_HEADER_BG};
                color: {C_HEADER_TEXT};

                font-size: 11px;
                font-weight: 700;

                padding-left: 14px;

                border: none;
                border-right: 1px solid {C_DIVIDER};
                border-bottom: 1.5px solid {C_BORDER};

                text-transform: uppercase;
            }}

            QHeaderView::section:first {{
                border-top-left-radius: {RADIUS}px;
                padding-left: 0px;
            }}

            QHeaderView::section:last {{
                border-top-right-radius: {RADIUS}px;
                border-right: none;
                padding-right: 14px;
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 5px;
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

            QScrollBar:horizontal {{
                height: 0;
            }}
        """)

    # ── Empty state ───────────────────────────────────────────────────────────
    def _show_empty_state(self):
        self.clearContents()
        self.setRowCount(1)
        self.setSpan(0, 0, 1, self.columnCount())
        self.setRowHeight(0, 240)
        self.setShowGrid(False)

        for col in range(self.columnCount()):
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setBackground(QColor(C_WHITE))
            item.setData(Qt.ItemDataRole.DisplayRole, "")
            self.setItem(0, col, item)

        empty_widget = QWidget()
        empty_widget.setObjectName("EmptyState")
        empty_widget.setStyleSheet(f"""
            QWidget#EmptyState {{
                background: {C_WHITE};
                border:     none;
            }}
            QLabel {{
                background: transparent;
                border:     none;
            }}
        """)

        layout = QVBoxLayout(empty_widget)
        layout.setContentsMargins(0, 34, 0, 34)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("📦")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 46px;")

        title = QLabel("Tidak ada produk ditemukan")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   16px;
            font-weight: 700;
            color:       {C_TEXT_PRI};
        """)

        subtitle = QLabel("Coba ubah filter, kata kunci pencarian,\natau tambahkan produk baru.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   12px;
            color:       {C_TEXT_SEC};
        """)
        
        layout.addStretch()
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        self.setCellWidget(0, 0, empty_widget)
        

    # ── Populate ──────────────────────────────────────────────────────────────
    def populate(self, products: list):
        self.clearContents()
        self.setRowCount(0)

        if not products:
            self._show_empty_state()
            return

        for i, product in enumerate(products):
            row = self.rowCount()
            self.insertRow(row)
            self.setRowHeight(row, self.ROW_H)

            is_alt = row % 2 == 1
            row_bg = C_ROW_ALT if is_alt else C_WHITE

            for col in range(len(self.COLUMNS)):
                ph = QTableWidgetItem()
                ph.setBackground(QColor(row_bg))
                ph.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.setItem(row, col, ph)

            self.setCellWidget(row, self.COL_NO,       self._make_no_cell(i + 1, row_bg))
            self.setCellWidget(row, self.COL_NAME,     self._make_name_cell(product, row_bg))
            self.setCellWidget(row, self.COL_SKU,      self._make_sku_cell(product, row_bg))
            self.setCellWidget(row, self.COL_CATEGORY, self._make_category_badge(product.category, row_bg))
            self.setCellWidget(row, self.COL_PRICE,    self._make_price_cell(product, row_bg))
            self.setCellWidget(row, self.COL_STOCK,    self._make_stock_badge(product.stock, row_bg))
            self.setCellWidget(row, self.COL_ACTION,   self._make_action_buttons(product, row_bg))

        QTimer.singleShot(0, self._apply_viewport_clip)

    # ── Cell helpers ──────────────────────────────────────────────────────────
    def _wrap(self, bg: str, align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter):
        w = QWidget()
        w.setStyleSheet(f"""
            background: transparent;
            border:     none;
        """)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(14, 0, 10, 0)
        lay.setSpacing(0)
        lay.setAlignment(align)
        return w, lay

    def _make_no_cell(self, number: int, bg: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"""
            background: transparent;
            border:     none;
        """)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel(str(number))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   12px;
            color:       {C_TEXT_SEC};
            background:  transparent;
        """)
        lay.addWidget(lbl)
        return w

    def _make_name_cell(self, product, bg: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"""
            background: transparent;
            border:     none;
        """)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(14, 0, 10, 0)
        lay.setSpacing(2)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        name_lbl = QLabel(product.name)
        name_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   13px;
            font-weight: 600;
            color:       {C_TEXT_PRI};
            background:  transparent;
        """)
        lay.addWidget(name_lbl)

        if product.brand:
            sub = QLabel(product.brand)
            sub.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size:   10px;
                color:       {C_TEXT_SEC};
                background:  transparent;
            """)
            lay.addWidget(sub)

        return w

    def _make_sku_cell(self, product, bg: str) -> QWidget:
        w, lay = self._wrap(bg)
        lbl = QLabel(product.sku or "—")
        lbl.setStyleSheet(f"""
            font-family:   'Segoe UI';
            font-size:     11px;
            font-weight:   600;
            color:         {C_TEXT_SEC};
            background:    transparent;
            border-radius: 5px;
            padding:       2px 8px;
        """)
        lay.addWidget(lbl)
        return w

    def _make_category_badge(self, category: str, bg: str) -> QWidget:
        cat = _cat_theme(category)
        w, lay = self._wrap(bg)

        badge = QLabel(f"{cat['emoji']}  {category}")
        badge.setStyleSheet(f"""
            background:    {cat['bg']};
            color:         {cat['text']};
            font-family:   'Segoe UI';
            font-size:     11px;
            font-weight:   700;
            padding:       4px 10px;
            border-radius: 6px;
            border:        none;
        """)
        lay.addWidget(badge)
        return w

    def _make_price_cell(self, product, bg: str) -> QWidget:
        w, lay = self._wrap(bg)
        lbl = QLabel(_format_price(product.price))
        lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   13px;
            font-weight: 700;
            color:       {C_TEXT_PRI};
            background:  transparent;
        """)
        lay.addWidget(lbl)
        return w

    def _make_stock_badge(self, stock: int, bg: str) -> QWidget:
        w, lay = self._wrap(bg)

        if stock == 0:
            color, badge_bg, dot, text = "#D63031", "#FFEAEA", "●", "Habis"
        elif stock < 20:
            color, badge_bg, dot, text = "#E17055", "#FFF3EA", "●", f"Sisa {stock}"
        else:
            color, badge_bg, dot, text = "#00B894", "#E6FAF5", "●", f"{stock} unit"

        pill = QWidget()
        pill.setStyleSheet(f"""
            background:    {badge_bg};
            border-radius: 6px;
            border:        none;
        """)
        pill_lay = QHBoxLayout(pill)
        pill_lay.setContentsMargins(8, 3, 10, 3)
        pill_lay.setSpacing(5)

        dot_lbl = QLabel(dot)
        dot_lbl.setStyleSheet(f"""
            font-size:  8px;
            color:      {color};
            background: transparent;
        """)

        txt_lbl = QLabel(text)
        txt_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   11px;
            font-weight: 600;
            color:       {color};
            background:  transparent;
        """)

        pill_lay.addWidget(dot_lbl)
        pill_lay.addWidget(txt_lbl)
        lay.addWidget(pill)
        return w

    def _make_action_buttons(self, product, bg: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"""
            background: transparent;
            border:     none;
        """)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(12, 0, 0, 0)
        lay.setSpacing(4)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        btn_wrap = QWidget()
        btn_wrap.setStyleSheet("""
            background: transparent;
            border:     none;
        """)
        btn_lay = QHBoxLayout(btn_wrap)
        btn_lay.setContentsMargins(0, 0, 0, 0)
        btn_lay.setSpacing(10)

        edit_btn = QPushButton("Edit")
        edit_btn.setFixedSize(54, 28)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background:    {C_TAG_BG};
                color:         {C_ACCENT};
                font-family:   'Segoe UI';
                font-size:     11px;
                font-weight:   600;
                border-radius: 7px;
                border:        none;
                padding:       0;
            }}
            QPushButton:hover {{
                background: {C_ACCENT};
                color:      #FFFFFF;
            }}
        """)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(product))

        del_btn = QPushButton("Hapus")
        del_btn.setFixedSize(64, 28)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background:    #FDEAEA;
                color:         {C_DANGER};
                font-family:   'Segoe UI';
                font-size:     11px;
                font-weight:   600;
                border-radius: 7px;
                border:        none;
                padding:       0;
            }}
            QPushButton:hover {{
                background: {C_DANGER};
                color:      #FFFFFF;
            }}
        """)
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(product))

        btn_lay.addWidget(edit_btn)
        btn_lay.addWidget(del_btn)
        lay.addWidget(btn_wrap)
        return w


# ═══════════════════════════════════════════════════════════════════════════════
# Add / Edit Product Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class ProductDialog(QDialog):
    saved = pyqtSignal(dict)

    def __init__(self, product: Product = None, parent=None):
        super().__init__(parent)
        self._product   = product
        self._edit_mode = product is not None

        self.setWindowTitle("Edit Produk" if self._edit_mode else "Tambah Produk")
        self.setModal(True)
        self.setFixedSize(440, 470)
        self.setStyleSheet(f"""
            QDialog {{
                background:  {C_WHITE};
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
            font-size:   18px;
            font-weight: 700;
            color:       {C_TEXT_PRI};
        """)
        layout.addWidget(title)
        layout.addSpacing(4)

        sub = QLabel("Isi detail produk dengan lengkap dan benar.")
        sub.setStyleSheet(f"""
            font-size: 12px;
            color:     {C_TEXT_SEC};
        """)
        layout.addWidget(sub)
        layout.addSpacing(20)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        def _field(ph=""):
            f = QLineEdit()
            f.setPlaceholderText(ph)
            f.setFixedHeight(38)
            f.setStyleSheet(f"""
                QLineEdit {{
                    background:    {C_BG};
                    border:        1px solid {C_BORDER};
                    border-radius: 8px;
                    padding:       0 12px;
                    font-size:     13px;
                    color:         {C_TEXT_PRI};
                    font-family:   'Segoe UI';
                }}
                QLineEdit:focus {{
                    border:     1.5px solid {C_ACCENT};
                    background: {C_WHITE};
                }}
            """)
            return f

        def _label(t):
            lbl = QLabel(t)
            lbl.setStyleSheet(f"""
                font-size:   12px;
                font-weight: 600;
                color:       {C_TEXT_PRI};
                font-family: 'Segoe UI';
            """)
            return lbl

        self._name_field  = _field("Nama produk")
        self._brand_field = _field("Merek produk")
        self._sku_field   = _field("SKU-001")
        self._price_field = _field("0")
        self._stock_field = _field("0")

        self._cat_combo = QComboBox()
        self._cat_combo.setFixedHeight(38)
        self._cat_combo.setStyleSheet(f"""
            QComboBox {{
                background:    {C_BG};
                border:        1px solid {C_BORDER};
                border-radius: 8px;
                padding:       0 12px;
                font-size:     13px;
                color:         {C_TEXT_PRI};
                font-family:   'Segoe UI';
            }}
            QComboBox:focus {{
                border: 1.5px solid {C_ACCENT};
            }}
            QComboBox::drop-down {{
                border: none;
                width:  24px;
            }}
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
            p = self._product
            self._name_field.setText(p.name)
            self._brand_field.setText(p.brand or "")
            self._sku_field.setText(p.sku or "")
            self._price_field.setText(str(p.price))
            self._stock_field.setText(str(p.stock))
            idx = self._cat_combo.findText(p.category or "")
            if idx >= 0:
                self._cat_combo.setCurrentIndex(idx)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("Batal")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background:    {C_BG};
                color:         {C_TEXT_SEC};
                font-family:   'Segoe UI';
                font-size:     13px;
                font-weight:   600;
                border-radius: 10px;
                border:        1px solid {C_BORDER};
            }}
            QPushButton:hover {{
                background: {C_BORDER};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Simpan Produk")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background:    {C_ACCENT};
                color:         #FFFFFF;
                font-family:   'Segoe UI';
                font-size:     13px;
                font-weight:   600;
                border-radius: 10px;
                border:        none;
            }}
            QPushButton:hover {{
                background: {C_ACCENT_H};
            }}
        """)
        save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_save(self):
        name = self._name_field.text().strip()
        if not name:
            self._name_field.setStyleSheet(
                self._name_field.styleSheet() + "border: 1.5px solid #E05252;"
            )
            return
        data = {
            "id":       self._product.id if self._edit_mode else None,
            "name":     name,
            "brand":    self._brand_field.text().strip(),
            "sku":      self._sku_field.text().strip(),
            "category": self._cat_combo.currentText(),
            "price":    self._price_field.text().replace(".", "").replace(",", ""),
            "stock":    self._stock_field.text(),
        }
        self.saved.emit(data)
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
# View Toggle
# ═══════════════════════════════════════════════════════════════════════════════
class ViewToggle(QWidget):
    VIEW_TABLE = "table"
    VIEW_CARD  = "card"
    toggled    = pyqtSignal(str)

    def __init__(self, initial: str = VIEW_CARD, parent=None):
        super().__init__(parent)
        self._current = initial
        self._build()

    def _build(self):
        self.setFixedHeight(38)
        self.setStyleSheet(f"""
            QWidget {{
                background:    {C_WHITE};
                border:        1px solid {C_BORDER};
                border-radius: 10px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self._table_btn = QPushButton("☰  Tabel")
        self._table_btn.setFixedHeight(38)
        self._table_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._table_btn.clicked.connect(lambda: self._select(self.VIEW_TABLE))

        self._card_btn = QPushButton("⊞  Kartu")
        self._card_btn.setFixedHeight(38)
        self._card_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._card_btn.clicked.connect(lambda: self._select(self.VIEW_CARD))

        layout.addWidget(self._table_btn)
        layout.addWidget(self._card_btn)
        self._update_styles()

    def _select(self, mode: str):
        if mode == self._current:
            return
        self._current = mode
        self._update_styles()
        self.toggled.emit(mode)

    def _update_styles(self):
        active = f"""
            QPushButton {{
                background:    {C_ACCENT};
                color:         #FFFFFF;
                font-family:   'Segoe UI';
                font-size:     12px;
                font-weight:   600;
                border-radius: 7px;
                padding:       0 14px;
                border:        none;
            }}
        """
        inactive = f"""
            QPushButton {{
                background:    transparent;
                color:         {C_TEXT_SEC};
                font-family:   'Segoe UI';
                font-size:     12px;
                font-weight:   400;
                border-radius: 7px;
                padding:       0 14px;
                border:        1px solid transparent;
            }}
            QPushButton:hover {{
                background: {C_TAG_BG};
                color:      {C_ACCENT};
                border:     1px solid {C_ACCENT};
            }}
        """
        if self._current == self.VIEW_TABLE:
            self._table_btn.setStyleSheet(active)
            self._card_btn.setStyleSheet(inactive)
        else:
            self._card_btn.setStyleSheet(active)
            self._table_btn.setStyleSheet(inactive)

    def current(self) -> str:
        return self._current


# ═══════════════════════════════════════════════════════════════════════════════
# Product Page
# ═══════════════════════════════════════════════════════════════════════════════
class ProductPage(QWidget):
    def __init__(self, user: dict = None, parent=None):
        super().__init__(parent)
        self._user              = user or {}
        self._products          = self._load_products()
        self._active_category   = "Semua"
        self._search_query      = ""
        self._view_mode         = ViewToggle.VIEW_TABLE
        self._grid_initialized  = False
        self._render_token      = 0
        self._pending_refresh   = False
        self._stat_value_labels: dict[str, tuple[QLabel, QLabel]] = {}

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C_BG};")
        self._build_ui()

    def _load_products(self) -> list[Product]:
        # return SAMPLE_PRODUCTS.copy()
        return ProductController.fetch()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 17, 32, 28)
        layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Manajemen Produk")
        page_title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   27px;
            font-weight: 700;
            color:       {C_TEXT_PRI};
            background:  transparent;
        """)

        page_sub = QLabel("Kelola semua produk warungmu di sini")
        page_sub.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   13px;
            color:       {C_TEXT_SEC};
            background:  transparent;
        """)

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        add_btn = QPushButton("+ Tambah Produk")
        add_btn.setFixedHeight(42)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background:    {C_ACCENT};
                color:         #FFFFFF;
                font-family:   'Segoe UI';
                font-size:     13px;
                font-weight:   600;
                border-radius: 10px;
                padding:       0 20px;
                border:        none;
            }}
            QPushButton:hover {{
                background: {C_ACCENT_H};
            }}
        """)
        add_btn.clicked.connect(self._open_add_dialog)

        header.addLayout(title_col)
        header.addStretch()
        header.addWidget(add_btn)
        layout.addLayout(header)
        layout.addSpacing(20)

        layout.addLayout(self._build_stats_row())
        layout.addSpacing(20)

        # ── Filter bar + view toggle ──────────────────────────────────────────
        filter_and_toggle = QHBoxLayout()
        filter_and_toggle.setSpacing(10)

        filter_widget = QWidget()
        filter_widget.setStyleSheet("background: transparent;")
        fw_layout = QHBoxLayout(filter_widget)
        fw_layout.setContentsMargins(0, 0, 0, 0)
        fw_layout.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("🔍  Cari produk...")
        search.setFixedHeight(38)
        search.setStyleSheet(f"""
            QLineEdit {{
                background:    {C_WHITE};
                border:        1px solid {C_BORDER};
                border-radius: 10px;
                padding:       0 14px;
                font-family:   'Segoe UI';
                font-size:     13px;
                color:         {C_TEXT_PRI};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {C_ACCENT};
            }}
        """)
        search.textChanged.connect(self._on_search_changed)
        fw_layout.addWidget(search)
        fw_layout.addSpacing(6)

        self._cat_buttons: dict[str, QPushButton] = {}
        for cat in SAMPLE_CATEGORIES:
            btn = self._cat_btn(cat)
            self._cat_buttons[cat] = btn
            fw_layout.addWidget(btn)
        fw_layout.addStretch()

        self._view_toggle = ViewToggle(initial=ViewToggle.VIEW_TABLE)
        self._view_toggle.toggled.connect(self._on_view_mode_changed)

        filter_and_toggle.addWidget(filter_widget, stretch=1)
        filter_and_toggle.addWidget(self._view_toggle)
        layout.addLayout(filter_and_toggle)
        layout.addSpacing(16)

        # ── Content stack ─────────────────────────────────────────────────────
        self._content_stack = QStackedWidget()
        self._content_stack.setStyleSheet("background: transparent;")

        # Page 0: Card grid
        self._card_page = QWidget()
        self._card_page.setStyleSheet("background: transparent;")
        card_page_layout = QVBoxLayout(self._card_page)
        card_page_layout.setContentsMargins(0, 0, 0, 0)
        card_page_layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border:     none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background:    transparent;
                width:         6px;
                margin:        8px 2px 8px 0;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background:    {C_BORDER};
                border-radius: 3px;
                min-height:    28px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #B8BCCE;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height:     0;
                background: none;
                border:     none;
            }}
            QScrollBar:horizontal {{
                height:     0;
                background: transparent;
            }}
        """)

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet("background: transparent;")
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setHorizontalSpacing(14)
        self._grid_layout.setVerticalSpacing(14)
        self._grid_layout.setColumnStretch(0, 1)
        self._grid_layout.setColumnStretch(1, 1)
        self._grid_layout.setColumnStretch(2, 1)
        self._grid_layout.setSpacing(14)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self._scroll.setWidget(self._grid_container)
        card_page_layout.addWidget(self._scroll)

        # Page 1: Table
        self._table_page = QWidget()
        self._table_page.setStyleSheet("background: transparent;")
        table_page_layout = QVBoxLayout(self._table_page)
        table_page_layout.setContentsMargins(0, 0, 0, 0)
        table_page_layout.setSpacing(0)

        self._table_view = ProductTableView()
        self._table_view.edit_clicked.connect(self._open_edit_dialog)
        self._table_view.delete_clicked.connect(self._delete_product)
        table_page_layout.addWidget(self._table_view)

        self._content_stack.addWidget(self._card_page)    # index 0
        self._content_stack.addWidget(self._table_page)   # index 1
        self._content_stack.setCurrentIndex(1)

        layout.addWidget(self._content_stack, stretch=1)

    # ── Stats ──────────────────────────────────────────────────────────────────
    def _calc_stats(self) -> dict:
        return {
            "total":      str(len(self._products)),
            "out_stock":  str(sum(1 for p in self._products if p.stock == 0)),
            "low_stock":  str(sum(1 for p in self._products if 0 < p.stock < 20)),
            "categories": str(len(set(p.category for p in self._products if p.category))),
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
                background:    {C_WHITE};
                border-radius: 12px;
                border:        1px solid {C_BORDER};
            }}
        """)
        card.setFixedHeight(76)
        _apply_card_shadow(card)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        indicator = QFrame()
        indicator.setFixedSize(40, 40)
        indicator.setStyleSheet(f"""
            background:    {bg};
            border-radius: 10px;
            border:        none;
        """)

        dot = QLabel(value)
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dot.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   18px;
            font-weight: 700;
            color:       {color};
            background:  transparent;
            border:      none;
        """)
        dot.setParent(indicator)
        dot.setGeometry(0, 0, 40, 40)

        val_lbl = QLabel(value)
        val_lbl.setFixedHeight(26)
        val_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   22px;
            font-weight: 700;
            color:       {C_TEXT_PRI};
            background:  transparent;
            border:      none;
            padding:     0px;
            margin:      0px;
        """)

        lbl_lbl = QLabel(label)
        lbl_lbl.setFixedHeight(14)
        lbl_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   11px;
            color:       {C_TEXT_SEC};
            background:  transparent;
            border:      none;
            padding:     0px;
            margin:      0px;
        """)

        self._stat_value_labels[key] = (dot, val_lbl)

        text_widget = QWidget()
        text_widget.setStyleSheet("background: transparent; border: none;")
        tw_layout = QVBoxLayout(text_widget)
        tw_layout.setSpacing(3)
        tw_layout.setContentsMargins(0, 0, 0, 0)
        tw_layout.addStretch()
        tw_layout.addWidget(val_lbl)
        tw_layout.addWidget(lbl_lbl)
        tw_layout.addStretch()

        layout.addWidget(indicator)
        layout.addWidget(text_widget)
        layout.addStretch()
        return card

    # ── Category button helpers ────────────────────────────────────────────────
    def _build_filter_bar(self) -> QHBoxLayout:
        return QHBoxLayout()

    @staticmethod
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

    def _cat_btn(self, cat: str) -> QPushButton:
        is_active = cat == self._active_category
        btn = QPushButton(cat)
        btn.setFixedHeight(38)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        font = QFont("Segoe UI", 11)
        font.setWeight(600 if is_active else 500)
        btn.setFont(font)
        self._style_cat_btn(btn, cat, is_active)
        btn.clicked.connect(lambda checked=False, s=cat: self._on_cat_changed(s))
        return btn

    def _style_cat_btn(self, btn: QPushButton, cat: str, active: bool):
        t = self._cat_button_theme(cat)
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

    # ── Data / filter logic ────────────────────────────────────────────────────
    def _filtered_products(self) -> list[Product]:
        result = self._products
        if self._active_category != "Semua":
            result = [p for p in result if p.category == self._active_category]
        if self._search_query:
            q = self._search_query.lower()
            result = [p for p in result if q in p.name.lower() or (p.sku and q in p.sku.lower())]
        return result

    def _clear_grid(self):
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

    def _get_column_count(self) -> int:
        available = self._scroll.viewport().width()
        return max(1, available // (ProductCard.CARD_WIDTH + self._grid_layout.spacing()))

    # ── Refresh ────────────────────────────────────────────────────────────────
    def _refresh_view(self):
        if self._view_mode == ViewToggle.VIEW_CARD:
            self._refresh_grid()
        else:
            self._refresh_table()

    def _refresh_table(self):
        self._table_view.populate(self._filtered_products())

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
            empty_wrap = QWidget()
            empty_wrap.setStyleSheet("background: transparent; border: none;")
            outer = QVBoxLayout(empty_wrap)
            outer.setContentsMargins(0, 36, 0, 40)
            outer.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

            empty_card = QFrame()
            empty_card.setFixedHeight(260)
            empty_card.setMinimumWidth(420)
            empty_card.setMaximumWidth(560)
            empty_card.setStyleSheet(f"""
                QFrame {{
                    background:    {C_WHITE};
                    border:        1px solid {C_BORDER};
                    border-radius: 18px;
                }}
                QLabel {{
                    background: transparent;
                    border:     none;
                }}
            """)

            card_layout = QVBoxLayout(empty_card)
            card_layout.setContentsMargins(40, 34, 40, 34)
            card_layout.setSpacing(8)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon = QLabel("📦")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setStyleSheet("font-size: 46px;")

            title = QLabel("Tidak ada produk ditemukan")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size:   16px;
                font-weight: 700;
                color:       {C_TEXT_PRI};
            """)

            subtitle = QLabel("Coba ubah filter, kata kunci pencarian,\natau tambahkan produk baru.")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size:   12px;
                color:       {C_TEXT_SEC};
            """)

            card_layout.addStretch()
            card_layout.addWidget(icon)
            card_layout.addWidget(title)
            card_layout.addWidget(subtitle)
            card_layout.addSpacing(4)
            card_layout.addStretch()
            outer.addWidget(empty_card)

            self._grid_layout.addWidget(empty_wrap, 0, 0, 1, max(1, self._get_column_count()))
            self._grid_container.adjustSize()
            self._grid_container.update()
            self._scroll.viewport().update()
            return

        if len(products) <= 60:
            self._render_all_cards(products, token)
        else:
            self._render_batch_cards(products, 0, batch_size=12, token=token)

    def _render_all_cards(self, products: list, token: int):
        if token != self._render_token or not self.isVisible():
            self._pending_refresh = True
            return
        for i, product in enumerate(products):
            card = ProductCard(product)
            card.edit_clicked.connect(self._open_edit_dialog)
            card.delete_clicked.connect(self._delete_product)
            self._grid_layout.addWidget(card, i // 3, i % 3)
        self._grid_container.adjustSize()
        self._grid_container.update()
        self._scroll.viewport().update()

    def _render_batch_cards(self, products: list, start_idx: int, batch_size: int = 12, token: int = None):
        if token is None:
            token = self._render_token
        if token != self._render_token or not self.isVisible():
            self._pending_refresh = True
            return
        cols    = self._get_column_count()
        end_idx = min(start_idx + batch_size, len(products))
        for i in range(start_idx, end_idx):
            card = ProductCard(products[i])
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._refresh_grid)

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
        for key, value in self._calc_stats().items():
            labels = self._stat_value_labels.get(key)
            if labels:
                dot, val_lbl = labels
                dot.setText(value)
                val_lbl.setText(value)

    # ── Event handlers ─────────────────────────────────────────────────────────
    def _on_view_mode_changed(self, mode: str):
        self._view_mode = mode
        if mode == ViewToggle.VIEW_TABLE:
            self._content_stack.setCurrentIndex(1)
            self._refresh_table()
        else:
            self._content_stack.setCurrentIndex(0)
            self._refresh_grid()

    def _on_search_changed(self, text: str):
        self._search_query = text.strip()
        self._refresh_view()

    def _on_cat_changed(self, cat: str):
        old = self._active_category
        if btn := self._cat_buttons.get(old):
            self._style_cat_btn(btn, old, False)
        self._active_category = cat
        if btn := self._cat_buttons.get(cat):
            self._style_cat_btn(btn, cat, True)
        self._refresh_view()

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
                category=data["category"],
            )
            self._products = self._load_products()
            self._refresh_stats()
            self._refresh_view()
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
                category=data["category"],
            )
            self._products = self._load_products()
            self._refresh_stats()
            self._refresh_view()
        except TypeError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _delete_product(self, product: Product):
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Hapus Produk")
        confirm.setText(f"Hapus <b>{product.name}</b>?")
        confirm.setInformativeText("Tindakan ini tidak dapat dibatalkan.")
        confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        confirm.setDefaultButton(QMessageBox.StandardButton.Cancel)
        confirm.setStyleSheet(f"""
            QMessageBox {{
                background:  {C_WHITE};
                font-family: 'Segoe UI';
            }}
            QPushButton {{
                min-width:     80px;
                height:        32px;
                border-radius: 8px;
                font-family:   'Segoe UI';
                font-size:     12px;
                font-weight:   600;
                border:        none;
            }}
        """)
        if confirm.exec() == QMessageBox.StandardButton.Yes:
            try:
                ProductController.remove(product.id)
                self._products = self._load_products()
                self._refresh_stats()
                self._refresh_view()
            except TypeError as e:
                QMessageBox.critical(self, "Error", str(e))

    def showEvent(self, event):
        super().showEvent(event)
        if not self._grid_initialized or self._pending_refresh:
            self._grid_initialized = True
            self._pending_refresh  = False
            QTimer.singleShot(0, self._refresh_view)