from controllers.sales import SalesController
from controllers.sales_detail import SalesDetailController
from database.db_master import DatabaseManager
from gui.signals import sales_signals, receivables_signals
from controllers.receivables import ReceivablesController

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFrame,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QStackedWidget,
    QSizePolicy,
    QScrollArea,
    QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPainterPath, QRegion, QFont
from gui.views.components.toast import Toast
from gui.views.components import Avatar


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

RADIUS = 14

C_ROW_ALT    = "#FAFBFF"
C_HEADER_BG  = "#FFFFFF"
C_HEADER_TEXT = "#9EA3B8"
C_DIVIDER    = "#F0F1F7"

PAYMENT_LABELS = {
    "tunai":   "Tunai",
    "qris":   "QRIS",
    None:     "—",
}

PAYMENT_THEME = {
    "tunai": {"bg": "#EEFCEF", "text": "#27AE60", "emoji": "💵"},
    "qris":  {"bg": "#EEF1FE", "text": "#4F6EF7", "emoji": "📱"},
    None:    {"bg": "#F1F3F8", "text": "#6C757D", "emoji": "❓"},
}

FILTER_PAYMENTS = ["Semua", "Tunai", "QRIS"]

PAYMENT_KEY_MAP = {
    "Semua":  None,
    "Tunai":  "tunai",
    "QRIS":   "qris",
}


# ── Helpers ────────────────────────────────────────────────────────────────────
def _payment_theme(payment: str | None) -> dict:
    return PAYMENT_THEME.get(payment, PAYMENT_THEME[None])

def _payment_label(payment: str | None) -> str:
    return PAYMENT_LABELS.get(payment, str(payment) if payment else "—")

def _fmt_currency(amount: float | None) -> str:
    if amount is None:
        return "—"
    return f"Rp {amount:,.0f}".replace(",", ".")


def _fetch_name_maps() -> tuple[dict[int, str], dict[int, str], dict[int, str]]:
    """Return (user_map, product_map, customer_map) dicts id->name."""
    _, cursor = DatabaseManager.require_connection()
    
    cursor.execute("SELECT id, name FROM users")
    user_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT ID, Name FROM Customer")
    customer_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT id, name, price FROM product")
    rows = cursor.fetchall()
    product_map = {row[0]: row[1] for row in rows}
    price_map   = {row[0]: row[2] for row in rows}
    return user_map, product_map, customer_map, price_map


def _fetch_transactions() -> list[dict]:
    user_map, product_map, customer_map, price_map = _fetch_name_maps()
    sales = SalesController.fetch()
    details = SalesDetailController.fetch()
    receivables = ReceivablesController.fetch()  # ← tambah ini

    # index receivables by sales_id
    receivable_by_sale = {r.sales_id: r for r in receivables}  # ← tambah ini

    detail_by_sale: dict[int, list] = {}
    for d in details:
        detail_by_sale.setdefault(d.sales_id, []).append(d)

    result = []
    for s in sales:
        cashier_name  = user_map.get(s.cashier_id, f"User #{s.cashier_id}")
        customer_name = customer_map.get(s.customer_id) if s.customer_id else None
        if customer_name is None:
            customer_name = "Pembeli Umum"

        items = []
        for d in detail_by_sale.get(s.id, []):
            items.append({
                "product_name": product_map.get(d.product_id, f"Produk #{d.product_id}"),
                "quantity":     d.quantity,
                "discount":     d.discount or 0.0,
                "price":        price_map.get(d.product_id, 0),
            })

        subtotal = sum(
            d.quantity * price_map.get(d.product_id, 0)
            for d in detail_by_sale.get(s.id, [])
        )

        receivable = receivable_by_sale.get(s.id)
        if receivable:
            total_price = receivable.total_amount
        else:
            total_price = s.total_price or subtotal

        # ── Receivable info ──────────────────────────────────────
        if receivable:
            debt        = receivable.total_amount - receivable.amount_paid
            debt_status = receivable.status
        else:
            # Tidak ada receivable = bayar lunas di tempat
            debt        = 0.0
            debt_status = "paid"
        # ─────────────────────────────────────────────────────────

        result.append({
            "id":            s.id,
            "cashier_name":  cashier_name,
            "customer_name": customer_name,
            "time":          s.time,
            "payment":       s.payment,
            "paid_amount": max(s.paid_amount or 0.0, 0.0),
            "items":         items,
            "total_price":   total_price,
            "debt":          debt,           # ← 0.0 = lunas/tidak ada hutang
            "debt_status":   debt_status,    # ← None = bukan hutang, 'unpaid'/'paid' = hutang
        })

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Transaction Card
# ═══════════════════════════════════════════════════════════════════════════════
class TransactionCard(QFrame):
    CARD_WIDTH = 280
    detail_clicked = pyqtSignal(object)
    delete_clicked = pyqtSignal(object)

    def __init__(self, tx: dict, parent=None):
        super().__init__(parent)
        self._tx = tx
        self._build()

    def _build(self):
        tx = self._tx
        debt        = tx.get("debt", 0.0)
        debt_status = tx.get("debt_status")

        self.setObjectName("TxCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Border merah kalau ada hutang, hijau kalau lunas hutang, default biasa
        if debt_status is not None and debt > 0:
            border_color = "#E05252"
            top_accent   = "#FDEAEA"
        elif debt_status is not None and debt <= 0:
            border_color = "#27AE60"
            top_accent   = "#EEFCEF"
        else:
            border_color = C_BORDER
            top_accent   = C_WHITE

        self.setStyleSheet(f"""
            QFrame#TxCard {{
                background:    {C_WHITE};
                border-radius: 14px;
                border:        1.5px solid {border_color};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top accent strip ──────────────────────────────────────────────────
        top_strip = QFrame()
        top_strip.setFixedHeight(36)
        top_strip.setStyleSheet(f"""
            QFrame {{
                background: {top_accent};
                border-top-left-radius: 13px;
                border-top-right-radius: 13px;
                border-bottom: 1px solid {border_color};
                border-left: none; border-right: none; border-top: none;
            }}
        """)
        strip_lay = QHBoxLayout(top_strip)
        strip_lay.setContentsMargins(14, 0, 14, 0)
        strip_lay.setSpacing(6)

        id_lbl = QLabel(f"#TX{tx['id']:04d}")
        id_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 12px; font-weight: 700;
            color: {C_TEXT_PRI}; background: transparent; border: none;
        """)
        strip_lay.addWidget(id_lbl)

        # Payment badge
        pt = _payment_theme(tx["payment"])
        pay_tag = QLabel(f"{pt['emoji']} {_payment_label(tx['payment'])}")
        pay_tag.setStyleSheet(f"""
            background: {pt['bg']}; color: {pt['text']};
            font-family: 'Segoe UI'; font-size: 9px; font-weight: 700;
            padding: 2px 7px; border-radius: 0px; border: none;
        """)
        strip_lay.addWidget(pay_tag)

        # Debt badge
        if debt_status is not None:
            if debt > 0:
                debt_tag = QLabel("🔴 Hutang")
                debt_tag.setStyleSheet("""
                    background: #FDEAEA; color: #E05252;
                    font-family: 'Segoe UI'; font-size: 9px; font-weight: 700;
                    padding: 2px 7px; border-radius: 5px; border: none;
                """)
            else:
                debt_tag = QLabel("🟢 Lunas")
                debt_tag.setStyleSheet("""
                    background: #EEFCEF; color: #27AE60;
                    font-family: 'Segoe UI'; font-size: 9px; font-weight: 700;
                    padding: 2px 7px; border-radius: 5px; border: none;
                """)
            strip_lay.addWidget(debt_tag)

        strip_lay.addStretch()

        # Waktu di kanan strip
        time_lbl = QLabel(str(tx["time"]))
        time_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 9px; color: {C_TEXT_SEC};
            background: transparent; border: none;
        """)
        strip_lay.addWidget(time_lbl)

        root.addWidget(top_strip)

        # ── Body ──────────────────────────────────────────────────────────────
        body = QVBoxLayout()
        body.setContentsMargins(14, 10, 14, 10)
        body.setSpacing(8)

        # Kasir + Pelanggan
        people_row = QHBoxLayout()
        people_row.setSpacing(0)

        def _info_chip(icon: str, label: str, stretch: bool = True) -> QVBoxLayout:
            col = QVBoxLayout()
            col.setSpacing(1)
            icon_lbl = QLabel(icon + "  " + label)
            icon_lbl.setStyleSheet(f"""
                font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                color: {C_TEXT_PRI}; background: transparent; border: none;
            """)
            icon_lbl.setWordWrap(False)
            col.addWidget(icon_lbl)
            return col

        cashier_col  = _info_chip("👤", tx["cashier_name"])
        customer_col = _info_chip("🙍", tx["customer_name"] if tx["customer_name"] != "Pembeli Umum" else "Umum")

        people_row.addLayout(cashier_col, stretch=1)

        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
        people_row.addWidget(sep)
        people_row.addSpacing(10)

        people_row.addLayout(customer_col, stretch=1)
        body.addLayout(people_row)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
        body.addWidget(div)

        # Harga row
        price_row = QHBoxLayout()
        price_row.setSpacing(0)

        def _price_col(label: str, value: str, color: str = C_TEXT_PRI) -> QVBoxLayout:
            col = QVBoxLayout()
            col.setSpacing(1)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:9px;color:{C_TEXT_SEC};background:transparent;border:none;")
            val = QLabel(value)
            val.setStyleSheet(f"font-family:'Segoe UI';font-size:12px;font-weight:700;color:{color};background:transparent;border:none;")
            col.addWidget(lbl)
            col.addWidget(val)
            return col

        price_row.addLayout(_price_col("Total Harga", _fmt_currency(tx["total_price"])), stretch=1)

        sep2 = QFrame()
        sep2.setFixedWidth(1)
        sep2.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
        price_row.addWidget(sep2)
        price_row.addSpacing(10)

        price_row.addLayout(_price_col("Dibayar", _fmt_currency(tx["paid_amount"]), C_ACCENT), stretch=1)

        if debt_status is not None:
            sep3 = QFrame()
            sep3.setFixedWidth(1)
            sep3.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
            price_row.addWidget(sep3)
            price_row.addSpacing(10)

            debt_color = C_DANGER if debt > 0 else "#27AE60"
            debt_val   = _fmt_currency(debt) if debt > 0 else "Lunas"
            price_row.addLayout(_price_col("Sisa Hutang", debt_val, debt_color), stretch=1)

        body.addLayout(price_row)

        # Divider
        div2 = QFrame()
        div2.setFixedHeight(1)
        div2.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
        body.addWidget(div2)

        # Items preview
        items = tx.get("items", [])
        if items:
            preview_parts = []
            for item in items[:3]:
                preview_parts.append(f"{item['product_name']} ×{item['quantity']}")
            preview_text = "  ·  ".join(preview_parts)
            if len(items) > 3:
                preview_text += f"  +{len(items) - 3} lagi"
            items_lbl = QLabel(f"🛒  {preview_text}")
        else:
            items_lbl = QLabel("🛒  Tidak ada item")

        items_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 10px; color: {C_TEXT_SEC};
            background: transparent; border: none;
        """)
        items_lbl.setWordWrap(True)
        body.addWidget(items_lbl)

        root.addLayout(body)

        # ── Footer: action buttons ────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background: #F7F8FC;
                border-bottom-left-radius: 13px;
                border-bottom-right-radius: 13px;
                border-top: 1px solid {C_DIVIDER};
                border-left: none; border-right: none; border-bottom: none;
            }}
        """)
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(14, 7, 14, 7)
        footer_lay.setSpacing(8)
        footer_lay.addStretch()

        detail_btn = QPushButton("Detail")
        detail_btn.setFixedSize(72, 26)
        detail_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        detail_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_TAG_BG}; color: {C_ACCENT};
                font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                border-radius: 7px; border: none;
            }}
            QPushButton:hover {{ background: {C_ACCENT}; color: #FFFFFF; }}
        """)
        detail_btn.clicked.connect(lambda: self.detail_clicked.emit(self._tx))
        footer_lay.addWidget(detail_btn)

        del_btn = QPushButton("Hapus")
        del_btn.setFixedSize(72, 26)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FDEAEA; color: {C_DANGER};
                font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                border-radius: 7px; border: none;
            }}
            QPushButton:hover {{ background: {C_DANGER}; color: #FFFFFF; }}
        """)
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(self._tx))
        footer_lay.addWidget(del_btn)

        root.addWidget(footer)

        # Hitung tinggi dinamis
        base_h = 36 + 10 + 22 + 1 + 10 + 38 + 1 + 10 + 28 + 1 + 10 + 40
        self.setFixedHeight(base_h + (16 if debt_status is not None else 0))


# ═══════════════════════════════════════════════════════════════════════════════
# Transaction Table View
# ═══════════════════════════════════════════════════════════════════════════════
class TransactionTableView(QTableWidget):
    detail_clicked = pyqtSignal(object)
    delete_clicked = pyqtSignal(object)
    
    ROW_H = 62

    COLUMNS = ["      #", "ID Transaksi", "Kasir", "Pelanggan", "Waktu", "Pembayaran", "Total Harga", "Dibayar", "Aksi"]
    COL_NO    = 0
    COL_ID    = 1
    COL_CASH  = 2
    COL_CUST  = 3
    COL_TIME  = 4
    COL_PAY   = 5
    COL_TOTAL = 6  # ← harga asli
    COL_AMT   = 7  # ← uang dibayar
    COL_ACT   = 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_table()

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
        
    MIN_STRETCH_WIDTH = 200

    def _setup_table(self):
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)

        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        self.setGridStyle(Qt.PenStyle.SolidLine)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.verticalHeader().setVisible(False)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMouseTracking(True)
        self.setCornerButtonEnabled(False)
        self.viewport().setAutoFillBackground(True)

        header = self.horizontalHeader()
        header.setHighlightSections(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setStretchLastSection(False)
        header.setFixedHeight(42)

        header.setSectionResizeMode(self.COL_NO,   QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_ID,   QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_CASH, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COL_CUST, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COL_TIME, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_PAY,  QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_AMT,  QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_ACT,  QHeaderView.ResizeMode.Fixed)

        self.setColumnWidth(self.COL_NO,   44)
        self.setColumnWidth(self.COL_ID,   110)
        self.setColumnWidth(self.COL_TIME, 200)
        self.setColumnWidth(self.COL_PAY,  130)
        self.setColumnWidth(self.COL_TOTAL, 150)
        self.setColumnWidth(self.COL_AMT,  180)
        self.setColumnWidth(self.COL_ACT,  180)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.setStyleSheet(f"""
            QTableWidget {{
                background: {C_WHITE};
                border: 1.5px solid {C_BORDER};
                border-radius: {RADIUS}px;
                font-family: 'Segoe UI'; font-size: 13px; color: {C_TEXT_PRI};
                outline: none; gridline-color: {C_DIVIDER};
                alternate-background-color: #F7F9FC;
            }}
            QTableWidget::item {{
                background: transparent; border: none;
                border-right: 1px solid {C_DIVIDER};
                border-bottom: 1px solid {C_DIVIDER};
                padding: 6px 10px;
            }}
            QTableCornerButton::section {{
                background: {C_HEADER_BG}; border: none;
                border-top-left-radius: {RADIUS}px;
            }}
            QHeaderView {{ background: transparent; border: none; }}
            QHeaderView::section {{
                background: {C_HEADER_BG}; color: {C_HEADER_TEXT};
                font-size: 11px; font-weight: 700; padding-left: 14px;
                border: none; border-right: 1.5px solid {C_DIVIDER};
                border-bottom: 1.5px solid {C_BORDER}; text-transform: uppercase;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: {RADIUS}px; padding-left: 0px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: {RADIUS}px;
                border-right: none; padding-right: 14px;
            }}
            QScrollBar:vertical {{
                background: transparent; width: 5px;
                margin: 8px 2px 8px 0; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {C_BORDER}; border-radius: 3px; min-height: 24px;
            }}
            QScrollBar::handle:vertical:hover {{ background: #B8BCCE; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QScrollBar:horizontal {{
                background: transparent;
                height: 10px;
                margin: 0 8px 2px 8px;
                border-radius: 3px;
            }}
            QScrollBar::handle:horizontal {{
                background: {C_BORDER};
                border-radius: 3px;
                min-width: 24px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: #B8BCCE;
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0;
            }}
        """)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._adjust_columns()
        QTimer.singleShot(0, self._apply_viewport_clip)

    def _adjust_columns(self):
        header = self.horizontalHeader()
        fixed_widths = (
            self.columnWidth(self.COL_NO) +
            self.columnWidth(self.COL_ID) +
            self.columnWidth(self.COL_TIME) +
            self.columnWidth(self.COL_PAY) +
            self.columnWidth(self.COL_TOTAL) +
            self.columnWidth(self.COL_AMT) +
            self.columnWidth(self.COL_ACT)
        )
        available = self.viewport().width()
        # Dibagi 2 karena ada 2 kolom stretch (Kasir + Pelanggan)
        each_stretch = (available - fixed_widths) // 2

        if each_stretch >= self.MIN_STRETCH_WIDTH:
            header.setSectionResizeMode(self.COL_CASH, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(self.COL_CUST, QHeaderView.ResizeMode.Stretch)
        else:
            header.setSectionResizeMode(self.COL_CASH, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(self.COL_CUST, QHeaderView.ResizeMode.Fixed)
            self.setColumnWidth(self.COL_CASH, self.MIN_STRETCH_WIDTH)
            self.setColumnWidth(self.COL_CUST, self.MIN_STRETCH_WIDTH)

    def _show_empty_state(self):
        self.clearContents()
        self.setRowCount(1)
        self.setShowGrid(False)
        self.setRowHeight(0, 240)

        self.setSpan(0, 0, 1, self.columnCount())

        item = QTableWidgetItem()
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        item.setBackground(QColor(C_WHITE))
        self.setItem(0, 0, item)

        outer = QWidget()
        outer.setStyleSheet("background: transparent; border: none;")
        outer_lay = QHBoxLayout(outer)
        outer_lay.setContentsMargins(0, 0, 0, 0)
        outer_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        empty = QWidget()
        empty.setObjectName("EmptyState")
        empty.setStyleSheet(f"""
            QWidget#EmptyState {{ background: {C_WHITE}; border: none; }}
            QLabel {{ background: transparent; border: none; }}
        """)
        lay = QVBoxLayout(empty)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(8)
        lay.addStretch()

        icon = QLabel("🧾")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 46px;")
        title = QLabel("Tidak ada transaksi ditemukan")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-family:'Segoe UI';font-size:16px;font-weight:700;color:{C_TEXT_PRI};")
        sub = QLabel("Coba ubah filter atau kata kunci pencarian.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"font-family:'Segoe UI';font-size:12px;color:{C_TEXT_SEC};")

        lay.addWidget(icon)
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addStretch()

        outer_lay.addWidget(empty)
        self.setCellWidget(0, 0, outer)

    def populate(self, transactions: list):
        self.clearContents()
        self.setRowCount(0)

        if not transactions:
            self._show_empty_state()
            return

        self.setShowGrid(True)
        for i, tx in enumerate(transactions):
            row = self.rowCount()
            self.insertRow(row)
            self.setRowHeight(row, self.ROW_H)

            row_bg = C_ROW_ALT if row % 2 == 1 else C_WHITE
            for col in range(len(self.COLUMNS)):
                ph = QTableWidgetItem()
                ph.setBackground(QColor(row_bg))
                ph.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.setItem(row, col, ph)

            self.setCellWidget(row, self.COL_NO,   self._make_no_cell(i + 1))
            self.setCellWidget(row, self.COL_ID, self._make_id_cell(tx))
            self.setCellWidget(row, self.COL_CASH, self._make_name_cell(tx["cashier_name"]))
            self.setCellWidget(row, self.COL_CUST, self._make_customer_cell(tx["customer_name"]))
            self.setCellWidget(row, self.COL_TIME, self._make_text_cell(tx["time"]))
            self.setCellWidget(row, self.COL_PAY,  self._make_payment_badge(tx["payment"]))
            self.setCellWidget(row, self.COL_TOTAL, self._make_text_cell(_fmt_currency(tx["total_price"])))
            self.setCellWidget(row, self.COL_AMT,  self._make_text_cell(_fmt_currency(tx["paid_amount"]), bold=True))
            self.setCellWidget(row, self.COL_ACT,  self._make_action_buttons(tx))

        QTimer.singleShot(0, self._apply_viewport_clip)

    def _wrap(self, align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter):
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(5, 0, 10, 0)
        lay.setSpacing(0)
        lay.setAlignment(align)
        return w, lay

    def _make_no_cell(self, number: int) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel(str(number))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:12px;color:{C_TEXT_SEC};background:transparent;")
        lay.addWidget(lbl)
        return w

    def _make_id_cell(self, tx: dict) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(10, 4, 6, 4)
        lay.setSpacing(3)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        id_lbl = QLabel(f"#TX{tx['id']:04d}")
        id_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 13px; font-weight: 700;
            color: {C_ACCENT}; background: transparent;
        """)
        lay.addWidget(id_lbl)

        debt        = tx.get("debt", 0.0)
        debt_status = tx.get("debt_status")

        if debt_status is not None:
            if debt > 0:
                badge = QLabel(f"🔴 Hutang")
                badge.setStyleSheet("""
                    background: #FDEAEA; color: #E05252;
                    font-family: 'Segoe UI'; font-size: 9px; font-weight: 700;
                    padding: 1px 6px; border-radius: 4px; border: none;
                """)
            else:
                badge = QLabel("🟢 Lunas")
                badge.setStyleSheet("""
                    background: #EEFCEF; color: #27AE60;
                    font-family: 'Segoe UI'; font-size: 9px; font-weight: 700;
                    padding: 1px 6px; border-radius: 4px; border: none;
                """)
            badge.setFixedWidth(badge.sizeHint().width() + 4)
            lay.addWidget(badge)

        return w

    def _make_text_cell(self, text: str, bold: bool = False, color: str = C_TEXT_PRI) -> QWidget:
        w, lay = self._wrap()
        weight = "700" if bold else "400"
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:13px;font-weight:{weight};color:{color};background:transparent;")
        lay.addWidget(lbl)
        return w

    def _make_name_cell(self, name: str) -> QWidget:
        w, lay = self._wrap()

        parts = name.strip().split()
        initials = (parts[0][0] + parts[1][0]).upper() if len(parts) >= 2 else name[:2].upper()

        palettes = [
            ("#EEF0FD", "#3B52C4"),
            ("#FDF0EC", "#B04A28"),
            ("#E6F1FB", "#185FA5"),
            ("#EAF3DE", "#3B6D11"),
        ]
        idx = (ord(initials[0]) - ord("A")) % len(palettes)
        bg, fg = palettes[idx]

        avatar = Avatar(initials, bg_color=bg, text_color=fg, size=30)
        lay.addWidget(avatar)
        lay.setSpacing(8)

        lbl = QLabel(name)
        lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:13px;font-weight:600;color:{C_TEXT_PRI};background:transparent;")
        lay.addWidget(lbl)
        return w

    def _make_customer_cell(self, customer_name: str) -> QWidget:
        w, lay = self._wrap()
        is_general = customer_name == "Pembeli Umum"
        color = C_TEXT_SEC if is_general else C_TEXT_PRI
        prefix = "👥  " if is_general else "🙍  "
        lbl = QLabel(prefix + customer_name)
        lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:12px;color:{color};background:transparent;")
        lay.addWidget(lbl)
        return w

    def _make_payment_badge(self, payment: str | None) -> QWidget:
        pt = _payment_theme(payment)
        w, lay = self._wrap()
        badge = QLabel(f"{pt['emoji']}  {_payment_label(payment)}")
        badge.setStyleSheet(f"""
            background: {pt['bg']}; color: {pt['text']};
            font-family: 'Segoe UI'; font-size: 11px; font-weight: 700;
            padding: 4px 10px; border-radius: 6px; border: none;
        """)
        lay.addWidget(badge)
        return w

    def _make_action_buttons(self, tx: dict) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(5, 0, 0, 0)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        detail_btn = QPushButton("Detail")
        detail_btn.setFixedSize(60, 28)
        detail_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        detail_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_TAG_BG}; color: {C_ACCENT};
                font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                border-radius: 7px; border: none; padding: 0;
            }}
            QPushButton:hover {{ background: {C_ACCENT}; color: #FFFFFF; }}
        """)
        detail_btn.clicked.connect(lambda: self.detail_clicked.emit(tx))
        lay.addWidget(detail_btn)

        del_btn = QPushButton("Hapus")
        del_btn.setFixedSize(60, 28)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FDEAEA; color: {C_DANGER};
                font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                border-radius: 7px; border: none; padding: 0;
            }}
            QPushButton:hover {{ background: {C_DANGER}; color: #FFFFFF; }}
        """)
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(tx))
        lay.addWidget(del_btn)

        return w


# ═══════════════════════════════════════════════════════════════════════════════
# Transaction Detail Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class TransactionDetailDialog(QDialog):
    def __init__(self, tx: dict, parent=None):
        super().__init__(parent)
        self._tx = tx
        self.setWindowTitle(f"Detail Transaksi #TX{tx['id']:04d}")
        self.setModal(True)
        self.setFixedWidth(480)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setSizeGripEnabled(False)
        self.setStyleSheet(f"QDialog {{ background: {C_WHITE}; font-family: 'Segoe UI'; }}")
        self._build_ui()
        self.adjustSize()
        self.setMaximumSize(480, self.height())

    def _build_ui(self):
        tx = self._tx
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #FAFAF8; border: 1px solid #DDD9D2; }")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(36, 30, 36, 30)
        cl.setSpacing(0)

        logo = QLabel("Warung<span style='color:#4F6EF7'>+</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("font-size:14px;color:#5F5E5A;font-weight:500;letter-spacing:1px;border:none;")
        cl.addWidget(logo)
        cl.addSpacing(12)

        title = QLabel(f"Detail Transaksi <span style='color:{C_ACCENT};'>#TX{tx['id']:04d}</span>")
        title.setTextFormat(Qt.TextFormat.RichText)
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)
        cl.addSpacing(4)

        subtitle = QLabel(f"Transaksi pada {tx['time']}")
        subtitle.setStyleSheet("font-size:12px;color:#888780;border:none;")
        cl.addWidget(subtitle)
        cl.addSpacing(16)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider)
        cl.addSpacing(16)

        # Info rows
        def _info_row(label: str, value: str, value_color: str = "#1b1b1b"):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(120)
            lbl.setStyleSheet("font-size:12px;color:#888780;border:none;")
            val = QLabel(value)
            val.setStyleSheet(f"font-size:13px;font-weight:600;color:{value_color};border:none;")
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            cl.addLayout(row)
            cl.addSpacing(8)

        _info_row("Kasir", tx["cashier_name"])
        _info_row("Pelanggan", tx["customer_name"])
        pt = _payment_theme(tx["payment"])
        _info_row("Pembayaran", f"{pt['emoji']} {_payment_label(tx['payment'])}", pt["text"])
        # ── tambah baris ini ──
        subtotal = sum(item["price"] * item["quantity"] for item in tx.get("items", []))
        diskon = subtotal - tx["total_price"]

        if diskon > 0:
            _info_row("Subtotal", _fmt_currency(subtotal))
            _info_row("Diskon", f"- {_fmt_currency(diskon)}", "#D08000")

        _info_row("Total Harga", _fmt_currency(tx["total_price"]), C_ACCENT)
        _info_row("Dibayar", _fmt_currency(tx["paid_amount"]))

        kembalian = tx["paid_amount"] - tx["total_price"]
        if kembalian > 0 and tx.get("debt_status") == "paid" and tx.get("debt", 0) == 0:
            _info_row("Kembalian", _fmt_currency(kembalian), "#27AE60")

        cl.addSpacing(8)

        divider2 = QFrame()
        divider2.setFixedHeight(1)
        divider2.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider2)
        cl.addSpacing(12)

        items_title = QLabel("Item Produk")
        items_title.setStyleSheet(f"font-size:13px;font-weight:700;color:{C_TEXT_PRI};border:none;")
        cl.addWidget(items_title)
        cl.addSpacing(8)

        if tx["items"]:
            for item in tx["items"]:
                row = QHBoxLayout()
                prod_lbl = QLabel(f"• {item['product_name']}")
                prod_lbl.setStyleSheet(f"font-size:12px;color:{C_TEXT_PRI};border:none;")
                qty_lbl  = QLabel(f"x{item['quantity']}")
                qty_lbl.setStyleSheet(f"font-size:12px;color:{C_TEXT_SEC};border:none;")
                disc_lbl = QLabel(f"Diskon: {item['discount']:.0f}" if item["discount"] else "")
                disc_lbl.setStyleSheet(f"font-size:11px;color:#D08000;border:none;")
                row.addWidget(prod_lbl)
                row.addStretch()
                row.addWidget(qty_lbl)
                row.addSpacing(10)
                row.addWidget(disc_lbl)
                cl.addLayout(row)
                cl.addSpacing(4)
        else:
            no_items = QLabel("Tidak ada item tercatat.")
            no_items.setStyleSheet(f"font-size:12px;color:{C_TEXT_SEC};border:none;")
            cl.addWidget(no_items)

        cl.addSpacing(20)

        close_btn = QPushButton("Tutup")
        close_btn.setFixedHeight(40)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 600;
                border-radius: 10px; border: none;
            }}
            QPushButton:hover {{ background: {C_ACCENT_H}; }}
        """)
        close_btn.clicked.connect(self.accept)
        cl.addWidget(close_btn)
        root.addWidget(card)


# ═══════════════════════════════════════════════════════════════════════════════
# Delete Transaction Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class DeleteTransactionDialog(QDialog):
    confirmed = pyqtSignal()

    def __init__(self, tx: dict, parent=None):
        super().__init__(parent)
        self._tx = tx
        self.setWindowTitle("Hapus Transaksi")
        self.setModal(True)
        self.setFixedWidth(420)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setSizeGripEnabled(False)
        self.setStyleSheet(f"QDialog {{ background: {C_WHITE}; font-family: 'Segoe UI'; }}")
        self._build_ui()
        self.adjustSize()
        self.setMaximumSize(420, self.height())

    def _build_ui(self):
        tx = self._tx
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #FAFAF8; border: 1px solid #DDD9D2; }")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(36, 30, 36, 30)
        cl.setSpacing(0)

        logo = QLabel("Warung<span style='color:#4F6EF7'>+</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("font-size:14px;color:#5F5E5A;font-weight:500;letter-spacing:1px;border:none;")
        cl.addWidget(logo)
        cl.addSpacing(12)

        title = QLabel("Hapus Transaksi?")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)
        cl.addSpacing(4)

        subtitle = QLabel(
            f"Kamu akan menghapus transaksi <b>#TX{tx['id']:04d}</b>.<br>"
            "Tindakan ini tidak dapat dibatalkan."
        )
        subtitle.setTextFormat(Qt.TextFormat.RichText)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size:12px;color:#888780;border:none;")
        cl.addWidget(subtitle)
        cl.addSpacing(16)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider)
        cl.addSpacing(16)

        pt = _payment_theme(tx["payment"])
        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{ background: {C_WHITE}; border: 1px solid #E4E6EE; border-radius: 10px; }}
            QLabel {{ background: transparent; border: none; }}
        """)
        info_lay = QHBoxLayout(info_card)
        info_lay.setContentsMargins(14, 12, 14, 12)
        info_lay.setSpacing(12)

        icon_lbl = QLabel("🧾")
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size:18px;background:#EEF1FE;border-radius:8px;")

        detail = QVBoxLayout()
        detail.setSpacing(2)
        id_lbl = QLabel(f"#TX{tx['id']:04d}  ·  {tx['cashier_name']}")
        id_lbl.setStyleSheet(f"font-size:13px;font-weight:600;color:{C_TEXT_PRI};")
        amt_lbl = QLabel(_fmt_currency(tx["paid_amount"]))
        amt_lbl.setStyleSheet(f"font-size:11px;color:{C_TEXT_SEC};")
        detail.addWidget(id_lbl)
        detail.addWidget(amt_lbl)

        info_lay.addWidget(icon_lbl)
        info_lay.addLayout(detail)
        info_lay.addStretch()
        cl.addWidget(info_card)
        cl.addSpacing(20)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

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

        delete_btn = QPushButton("Ya, Hapus Transaksi")
        delete_btn.setFixedHeight(40)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_DANGER}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 600;
                border-radius: 10px; border: none;
            }}
            QPushButton:hover {{ background: #C94040; }}
        """)
        delete_btn.clicked.connect(self._on_confirm)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(delete_btn)
        cl.addLayout(btn_row)
        root.addWidget(card)

    def _on_confirm(self):
        self.confirmed.emit()
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
# View Toggle
# ═══════════════════════════════════════════════════════════════════════════════
class ViewToggle(QWidget):
    VIEW_TABLE = "table"
    VIEW_CARD  = "card"
    toggled    = pyqtSignal(str)

    def __init__(self, initial: str = VIEW_TABLE, parent=None):
        super().__init__(parent)
        self._current = initial
        self._build()

    def _build(self):
        self.setFixedHeight(38)
        self.setStyleSheet(f"""
            QWidget {{ background: {C_WHITE}; border: 1px solid {C_BORDER}; border-radius: 10px; }}
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
                background: {C_ACCENT}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 12px; font-weight: 600;
                border-radius: 7px; padding: 0 14px; border: none;
            }}
        """
        inactive = f"""
            QPushButton {{
                background: transparent; color: {C_TEXT_SEC};
                font-family: 'Segoe UI'; font-size: 12px; font-weight: 400;
                border-radius: 7px; padding: 0 14px; border: 1px solid transparent;
            }}
            QPushButton:hover {{
                background: {C_TAG_BG}; color: {C_ACCENT}; border: 1px solid {C_ACCENT};
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
# Transaction Page
# ═══════════════════════════════════════════════════════════════════════════════
class TransactionPage(QWidget):
    def __init__(self, user: dict = None, parent=None):
        super().__init__(parent)
        self._user             = user or {}
        self._transactions     = self._load_transactions()
        self._active_filter    = "Semua"
        self._search_query     = ""
        self._view_mode        = ViewToggle.VIEW_TABLE
        self._grid_initialized = False
        self._pending_refresh  = False
        self._render_token     = 0
        self._stat_value_labels: dict[str, tuple] = {}

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C_BG};")
        self._build_ui()
        sales_signals.sales_completed.connect(self._on_sales_completed)
        receivables_signals.receivables_updated.connect(self._on_sales_completed)
        receivables_signals.receivables_paid.connect(self._on_sales_completed)
    
    def _on_sales_completed(self, sales_id: int):
        self._transactions = self._load_transactions()
        self._refresh_stats()
        self._refresh_view()

    def _load_transactions(self) -> list[dict]:
        return _fetch_transactions()

    # ── Build UI ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 17, 32, 28)
        layout.setSpacing(0)

        # ── Header ─────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Manajemen Transaksi")
        page_title.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 27px; font-weight: 700;
            color: {C_TEXT_PRI}; background: transparent;
        """)
        page_sub = QLabel("Lihat dan kelola semua riwayat transaksi di sini")
        page_sub.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 13px;
            color: {C_TEXT_SEC}; background: transparent;
        """)

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)
        header.addLayout(title_col)
        header.addStretch()
        layout.addLayout(header)
        layout.addSpacing(20)

        layout.addLayout(self._build_stats_row())
        layout.addSpacing(20)

        # ── Filter bar + view toggle ───────────────────────────────────────────
        filter_and_toggle = QHBoxLayout()
        filter_and_toggle.setSpacing(10)

        filter_widget = QWidget()
        filter_widget.setStyleSheet("background: transparent;")
        fw_layout = QHBoxLayout(filter_widget)
        fw_layout.setContentsMargins(0, 0, 0, 0)
        fw_layout.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("🔍  Cari kasir atau pelanggan...")
        search.setFixedHeight(38)
        search.setStyleSheet(f"""
            QLineEdit {{
                background: {C_WHITE}; border: 1px solid {C_BORDER};
                border-radius: 10px; padding: 0 14px;
                font-family: 'Segoe UI'; font-size: 13px; color: {C_TEXT_PRI};
            }}
            QLineEdit:focus {{ border: 1.5px solid {C_ACCENT}; }}
        """)
        search.textChanged.connect(self._on_search_changed)
        fw_layout.addWidget(search)
        fw_layout.addSpacing(6)

        self._filter_buttons: dict[str, QPushButton] = {}
        for f in FILTER_PAYMENTS:
            btn = self._filter_btn(f)
            self._filter_buttons[f] = btn
            fw_layout.addWidget(btn)
        fw_layout.addStretch()

        self._view_toggle = ViewToggle(initial=ViewToggle.VIEW_TABLE)
        self._view_toggle.toggled.connect(self._on_view_mode_changed)

        filter_and_toggle.addWidget(filter_widget, stretch=1)
        filter_and_toggle.addWidget(self._view_toggle)
        layout.addLayout(filter_and_toggle)
        layout.addSpacing(16)

        # ── Content stack ──────────────────────────────────────────────────────
        self._content_stack = QStackedWidget()
        self._content_stack.setStyleSheet("background: transparent;")

        # Page 0: Card grid
        self._card_page = QWidget()
        self._card_page.setStyleSheet("background: transparent;")
        card_layout = QVBoxLayout(self._card_page)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollArea > QWidget > QWidget {{ background: transparent; }}
            QScrollBar:vertical {{
                background: transparent; width: 6px;
                margin: 8px 2px 8px 0; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {C_BORDER}; border-radius: 3px; min-height: 28px;
            }}
            QScrollBar::handle:vertical:hover {{ background: #B8BCCE; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0; background: none;
            }}
            QScrollBar:horizontal {{
                background: transparent; height: 8px;
                margin: 0 0 2px 0; border-radius: 3px;
            }}
            QScrollBar::handle:horizontal {{
                background: {C_BORDER}; border-radius: 3px; min-width: 28px;
            }}
            QScrollBar::handle:horizontal:hover {{ background: #B8BCCE; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0; background: none;
            }}
        """)

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet("background: transparent;")
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(14)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self._scroll.setWidget(self._grid_container)
        card_layout.addWidget(self._scroll)

        # Page 1: Table
        self._table_page = QWidget()
        self._table_page.setStyleSheet("background: transparent;")
        table_layout = QVBoxLayout(self._table_page)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self._table_view = TransactionTableView()
        self._table_view.detail_clicked.connect(self._open_detail_dialog)
        self._table_view.delete_clicked.connect(self._delete_transaction)
        table_layout.addWidget(self._table_view)

        self._content_stack.addWidget(self._card_page)   # index 0
        self._content_stack.addWidget(self._table_page)  # index 1
        self._content_stack.setCurrentIndex(1)

        layout.addWidget(self._content_stack, stretch=1)

    # ── Stats ───────────────────────────────────────────────────────────────────
    def _calc_stats(self) -> dict:
        txs = self._transactions
        total_revenue = sum(t["paid_amount"] for t in txs if t["paid_amount"] is not None)
        return {
            "total":   str(len(txs)),
            "revenue": _fmt_currency(total_revenue),
            "member":  str(sum(1 for t in txs if t["customer_name"] != "Pembeli Umum")),
        }

    def _build_stats_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(14)
        values = self._calc_stats()
        stats = [
            ("total",   "Total Transaksi",  values["total"],   "#4F6EF7", "#EEF1FE"),
            ("member",  "Transaksi Member", values["member"],  "#D08000", "#FDF6EC"),
            ("revenue", "Total Pendapatan", values["revenue"], "#27AE60", "#E8F8F0"),
        ]
        for key, label, value, color, bg in stats:
            row.addWidget(self._stat_card(key, label, value, color, bg))
        return row

    def _stat_card(self, key: str, label: str, value: str, color: str, bg: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{ background: {C_WHITE}; border-radius: 12px; border: 1px solid {C_BORDER}; }}
        """)
        card.setFixedHeight(76)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        indicator = QFrame()
        indicator.setFixedSize(40, 40)
        indicator.setStyleSheet(f"background: {bg}; border-radius: 10px; border: none;")

        dot = QLabel(value)
        if key == "revenue":
            dot.setText("🪙")  # bisa emoji coin
        else:
            dot.setText(value)
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dot.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 18px; font-weight: 700;
            color: {color}; background: transparent; border: none;
        """)
        dot.setParent(indicator)
        dot.setGeometry(0, 0, 40, 40)

        val_lbl = QLabel(value)
        val_lbl.setFixedHeight(26)
        val_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 22px; font-weight: 700;
            color: {C_TEXT_PRI}; background: transparent; border: none;
        """)

        lbl_lbl = QLabel(label)
        lbl_lbl.setFixedHeight(14)
        lbl_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 11px;
            color: {C_TEXT_SEC}; background: transparent; border: none;
        """)
        
        

        self._stat_value_labels[key] = (dot, val_lbl)

        text_w = QWidget()
        text_w.setStyleSheet("background: transparent; border: none;")
        tw = QVBoxLayout(text_w)
        tw.setSpacing(3)
        tw.setContentsMargins(0, 0, 0, 0)
        tw.addStretch()
        tw.addWidget(val_lbl)
        tw.addWidget(lbl_lbl)
        tw.addStretch()

        layout.addWidget(indicator)
        layout.addWidget(text_w)
        layout.addStretch()
        return card

    def _refresh_stats(self):
        for key, value in self._calc_stats().items():
            labels = self._stat_value_labels.get(key)
            if labels:
                dot, val_lbl = labels
                dot.setText("🪙" if key == "revenue" else value)  # ← konsisten
                val_lbl.setText(value)

    # ── Filter buttons ─────────────────────────────────────────────────────────
    def _filter_btn(self, label: str) -> QPushButton:
        is_active = label == self._active_filter
        btn = QPushButton(label)
        btn.setFixedHeight(38)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        font = QFont("Segoe UI", 11)
        font.setWeight(600)
        btn.setFont(font)
        self._style_filter_btn(btn, label, is_active)
        btn.clicked.connect(lambda checked=False, s=label: self._on_filter_changed(s))
        return btn

    def _style_filter_btn(self, btn: QPushButton, label: str, active: bool):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C_ACCENT}; color: #FFFFFF;
                    font-family: 'Segoe UI'; font-size: 12px; font-weight: 700;
                    border-radius: 10px; padding: 0 16px; border: none;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C_WHITE}; color: {C_TEXT_SEC};
                    font-family: 'Segoe UI'; font-size: 12px; font-weight: 600;
                    border-radius: 10px; padding: 0 16px; border: 1px solid {C_BORDER};
                }}
                QPushButton:hover {{
                    background: {C_TAG_BG}; color: {C_ACCENT}; border: 1px solid {C_ACCENT};
                }}
            """)

    # ── Data / filter ───────────────────────────────────────────────────────────
    def _filtered_transactions(self) -> list[dict]:
        result = self._transactions
        key = PAYMENT_KEY_MAP.get(self._active_filter)
        if key is not None:
            result = [t for t in result if t["payment"] == key]
        if self._search_query:
            q = self._search_query.lower()
            result = [
                t for t in result
                if q in t["cashier_name"].lower() or q in t["customer_name"].lower()
            ]
        return result

    # ── Refresh ─────────────────────────────────────────────────────────────────
    def _refresh_view(self):
        if self._view_mode == ViewToggle.VIEW_CARD:
            self._refresh_grid()
        else:
            self._refresh_table()

    def _refresh_table(self):
        self._table_view.populate(self._filtered_transactions())
    
    def _get_column_count(self) -> int:
        available = self._scroll.viewport().width()
        cols = available // (
            TransactionCard.CARD_WIDTH +
            self._grid_layout.spacing()
        )

        return max(2, min(4, int(cols)))

    def _refresh_grid(self):
        self._render_token += 1
        token = self._render_token

        if not self.isVisible():
            self._pending_refresh = True
            return

        self._pending_refresh = False
        self._clear_grid()

        txs = self._filtered_transactions()

        if not txs:
            self._grid_layout.setAlignment(
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
            )

            empty_wrap = QWidget()
            empty_wrap.setStyleSheet("background: transparent; border: none;")
            empty_wrap.setMinimumWidth(self._scroll.viewport().width())

            outer = QVBoxLayout(empty_wrap)
            outer.setContentsMargins(0, 33, 2, 0)
            outer.setSpacing(0)
            outer.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

            empty_card = QFrame()
            empty_card.setFixedHeight(260)
            empty_card.setFixedWidth(460)
            empty_card.setStyleSheet(f"""
                QFrame {{
                    background: {C_WHITE};
                    border: 1px solid {C_BORDER};
                    border-radius: 18px;
                }}
                QLabel {{
                    background: transparent;
                    border: none;
                }}
            """)

            card_layout = QVBoxLayout(empty_card)
            card_layout.setContentsMargins(40, 34, 40, 34)
            card_layout.setSpacing(8)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon = QLabel("🧾")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setStyleSheet("font-size: 46px;")

            title = QLabel("Tidak ada transaksi ditemukan")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size:   16px;
                font-weight: 700;
                color:       {C_TEXT_PRI};
            """)

            subtitle = QLabel("Coba ubah filter atau kata kunci pencarian.")
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
            card_layout.addStretch()

            outer.addWidget(empty_card)

            self._grid_layout.addWidget(empty_wrap, 0, 0)

            self._grid_container.adjustSize()
            self._grid_container.update()
            self._scroll.viewport().update()
            return

        self._grid_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        cols = self._get_column_count()

        # reset stretch
        for c in range(10):
            self._grid_layout.setColumnStretch(c, 0)

        # apply stretch
        for c in range(cols):
            self._grid_layout.setColumnStretch(c, 1)

        if len(txs) <= 60:
            self._render_all_cards(txs, token)
        else:
            self._render_batch_cards(
                txs,
                start=0,
                batch_size=12,
                token=token
            )

        self._grid_container.adjustSize()
        self._grid_container.update()
        self._scroll.viewport().update()

    def _render_all_cards(self, txs: list[dict], token: int):
        cols = self._get_column_count()

        for i, tx in enumerate(txs):
            if token != self._render_token:
                return

            card = TransactionCard(tx)

            card.detail_clicked.connect(self._open_detail_dialog)
            card.delete_clicked.connect(self._delete_transaction)

            self._grid_layout.addWidget(
                card,
                i // cols,
                i % cols
            )

    def _render_batch_cards(
        self,
        txs: list[dict],
        start: int,
        batch_size: int,
        token: int
    ):
        if token != self._render_token:
            return

        cols = self._get_column_count()

        end = min(start + batch_size, len(txs))

        for i in range(start, end):
            tx = txs[i]

            card = TransactionCard(tx)

            card.detail_clicked.connect(self._open_detail_dialog)
            card.delete_clicked.connect(self._delete_transaction)

            self._grid_layout.addWidget(
                card,
                i // cols,
                i % cols
            )

        if end < len(txs):
            QTimer.singleShot(
                0,
                lambda: self._render_batch_cards(
                    txs,
                    end,
                    batch_size,
                    token
                )
            )

    def _clear_grid(self):
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._refresh_grid)

    # ── Event handlers ──────────────────────────────────────────────────────────
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

    def _on_filter_changed(self, label: str):
        old = self._active_filter
        if btn := self._filter_buttons.get(old):
            self._style_filter_btn(btn, old, False)
        self._active_filter = label
        if btn := self._filter_buttons.get(label):
            self._style_filter_btn(btn, label, True)
        self._refresh_view()

    def _open_detail_dialog(self, tx: dict):
        dlg = TransactionDetailDialog(tx=tx, parent=self)
        dlg.exec()

    def _delete_transaction(self, tx: dict):
        def do_delete():
            try:
                SalesController.remove(tx["id"])
                self._transactions = self._load_transactions()
                self._refresh_stats()
                self._refresh_view()
                Toast.show_toast(f"Transaksi <b>#TX{tx['id']:04d}</b> berhasil dihapus.", "success", self)
            except Exception as e:
                Toast.show_toast(str(e), "error", self)

        dlg = DeleteTransactionDialog(tx=tx, parent=self)
        dlg.confirmed.connect(do_delete)
        dlg.exec()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._grid_initialized or self._pending_refresh:
            self._grid_initialized = True
            self._pending_refresh  = False
            QTimer.singleShot(0, self._refresh_view)