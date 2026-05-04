from controllers.purchase import PurchaseController
from controllers.purchase_detail import PurchaseDetailController
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFrame,
    QComboBox,
    QDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QStackedWidget,
    QSizePolicy,
    QScrollArea,
    QGridLayout,
    QSpinBox,
    QDoubleSpinBox,
    QScrollBar,
    QDateTimeEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QColor, QPainterPath, QRegion, QFont
from gui.views.components.toast import Toast
# Tambahkan import ini di bagian atas
from controllers.supplier import SupplierController
from controllers.product import ProductController
from controllers.user import UserController

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
C_SUCCESS  = "#27AE60"
C_WARNING  = "#F39C12"

RADIUS = 14

C_ROW_ALT    = "#FAFBFF"
C_HEADER_BG  = "#FFFFFF"
C_HEADER_TEXT = "#9EA3B8"
C_DIVIDER    = "#F0F1F7"

STATUS_THEME = {
    "Lunas":   {"bg": "#EEFCEF", "text": "#27AE60"},
    "Pending": {"bg": "#FFF8E8", "text": "#F39C12"},
    "Belum":   {"bg": "#FDEAEA", "text": "#E05252"},
}

FILTER_STATUS = ["Semua", "Lunas", "Pending", "Belum"]


# ── Helpers ────────────────────────────────────────────────────────────────────
def _fmt_currency(value) -> str:
    if value is None:
        return "—"
    try:
        return f"Rp {float(value):,.0f}".replace(",", ".")
    except Exception:
        return "—"

def _fmt_date(value: str) -> str:
    """Trim datetime string to date only if long."""
    if value and len(value) > 10:
        return value[:10]
    return value or "—"


# ═══════════════════════════════════════════════════════════════════════════════
# Purchase Card
# ═══════════════════════════════════════════════════════════════════════════════
class PurchaseCard(QFrame):
    edit_clicked   = pyqtSignal(object)
    delete_clicked = pyqtSignal(object)
    detail_clicked = pyqtSignal(object)

    def __init__(self, purchase, parent=None):
        super().__init__(parent)
        self._purchase = purchase
        self._build()

    def _build(self):
        p = self._purchase

        self.setObjectName("PurchaseCard")
        self.setFixedHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.setStyleSheet(f"""
            QFrame#PurchaseCard {{
                background: {C_WHITE};
                border-radius: 14px;
                border: 1.5px solid {C_BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 12)
        layout.setSpacing(10)

        # ── TOP (ID + DATE) ─────────────────────────────
        top = QHBoxLayout()

        id_lbl = QLabel(f"#{p.id:04d}")
        id_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 15px; font-weight: 700;
            color: {C_TEXT_PRI}; border: none;
        """)
        top.addWidget(id_lbl)

        top.addStretch()

        date_lbl = QLabel(_fmt_date(p.time))
        date_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 11px;
            color: {C_TEXT_SEC}; border: none;
        """)
        top.addWidget(date_lbl)

        layout.addLayout(top)

        # ── MID (CHIPS) ─────────────────────────────
        mid = QHBoxLayout()
        mid.setSpacing(8)

        supplier = SupplierController.get(p.supplier_id)
        users = UserController.fetch()
        user_map = {u[0]: u[1] for u in users}

        supplier_name = supplier.name if supplier else f"Supplier #{p.supplier_id}"
        user_name = user_map.get(p.user_id, f"User #{p.user_id}")

        def make_chip(text, color, bg):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: 600;
                color: {color};
                background: {bg};
                padding: 3px 10px;
                border-radius: 8px;
                border: none;
            """)
            return lbl

        mid.addWidget(make_chip(supplier_name, C_ACCENT, C_TAG_BG))
        mid.addWidget(make_chip(user_name, C_TEXT_SEC, "#F3F4F6"))

        mid.addStretch()
        layout.addLayout(mid)

        # ── TOTAL (FOCUS AREA) ─────────────────────────────
        total_lbl = QLabel(_fmt_currency(p.total_amount))
        total_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 18px;
            font-weight: 800;
            color: {C_SUCCESS};
            padding-top: 4px;
        """)
        layout.addWidget(total_lbl)

        # spacing visual separator (important UX trick)
        layout.addSpacing(4)

        # ── BOTTOM BUTTONS ─────────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        bottom.addStretch()

        def btn(text, bg, color):
            b = QPushButton(text)
            b.setFixedHeight(30)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{
                    background: {bg};
                    color: {color};
                    font-family: 'Segoe UI';
                    font-size: 11px;
                    font-weight: 600;
                    border-radius: 8px;
                    padding: 0 10px;
                    border: none;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                }}
            """)
            return b

        detail_btn = btn("Detail", "#EEFCEF", C_SUCCESS)
        detail_btn.setFixedWidth(70)
        detail_btn.clicked.connect(lambda: self.detail_clicked.emit(self._purchase))

        edit_btn = btn("Edit", C_TAG_BG, C_ACCENT)
        edit_btn.setFixedWidth(70)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self._purchase))

        del_btn = btn("Hapus", "#FDEAEA", C_DANGER)
        del_btn.setFixedWidth(75)
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(self._purchase))

        bottom.addWidget(detail_btn)
        bottom.addWidget(edit_btn)
        bottom.addWidget(del_btn)

        layout.addLayout(bottom)


# ═══════════════════════════════════════════════════════════════════════════════
# Purchase Table View
# ═══════════════════════════════════════════════════════════════════════════════
class PurchaseTableView(QTableWidget):
    edit_clicked   = pyqtSignal(object)
    delete_clicked = pyqtSignal(object)
    detail_clicked = pyqtSignal(object)

    COLUMNS    = ["      #", "Supplier", "User", "Tanggal", "Total", "Aksi"]
    COL_NO        = 0
    COL_SUPPLIER  = 1
    COL_USER      = 2
    COL_DATE      = 3
    COL_TOTAL     = 4
    COL_ACTION    = 5
    ROW_H         = 52

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

        header.setSectionResizeMode(self.COL_NO,       QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_SUPPLIER, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_USER,     QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_DATE,     QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_TOTAL,    QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COL_ACTION,   QHeaderView.ResizeMode.Fixed)

        self.setColumnWidth(self.COL_NO,       44)
        self.setColumnWidth(self.COL_SUPPLIER, 400)
        self.setColumnWidth(self.COL_USER,     200)
        self.setColumnWidth(self.COL_DATE,     130)
        self.setColumnWidth(self.COL_ACTION,   250)

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
            QScrollBar:horizontal {{ height: 0; }}
        """)

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

        icon = QLabel("🛒")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 46px;")
        title = QLabel("Tidak ada pembelian ditemukan")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-family:'Segoe UI';font-size:16px;font-weight:700;color:{C_TEXT_PRI};")
        sub = QLabel("Coba ubah filter, kata kunci pencarian,\natau tambahkan pembelian baru.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"font-family:'Segoe UI';font-size:12px;color:{C_TEXT_SEC};")

        lay.addWidget(icon)
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addStretch()
        self.setCellWidget(0, 0, empty)

    def populate(self, purchases: list):
        self.clearContents()
        self.setRowCount(0)

        if not purchases:
            self._show_empty_state()
            return

        self.setShowGrid(True)
        suppliers = {s.id: s.name for s in SupplierController.fetch()}
        users = {u[0]: u[1] for u in UserController.fetch()}
        for i, p in enumerate(purchases):
            row = self.rowCount()
            self.insertRow(row)
            self.setRowHeight(row, self.ROW_H)

            row_bg = C_ROW_ALT if row % 2 == 1 else C_WHITE
            for col in range(len(self.COLUMNS)):
                ph = QTableWidgetItem()
                ph.setBackground(QColor(row_bg))
                ph.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.setItem(row, col, ph)

            self.setCellWidget(row, self.COL_NO,       self._make_no_cell(i + 1))
            supplier_name = suppliers.get(p.supplier_id, "Unknown Supplier")
            user_name = users.get(p.user_id, "Unknown User")

            self.setCellWidget(row, self.COL_SUPPLIER, self._make_text_cell(supplier_name))
            self.setCellWidget(row, self.COL_USER,     self._make_text_cell(user_name))
            self.setCellWidget(row, self.COL_DATE,     self._make_text_cell(_fmt_date(p.time)))
            self.setCellWidget(row, self.COL_TOTAL,    self._make_total_cell(p.total_amount))
            self.setCellWidget(row, self.COL_ACTION,   self._make_action_buttons(p))

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

    def _make_text_cell(self, text: str) -> QWidget:
        w, lay = self._wrap()
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:13px;color:{C_TEXT_PRI};background:transparent;")
        lay.addWidget(lbl)
        return w

    def _make_total_cell(self, total) -> QWidget:
        w, lay = self._wrap()
        lbl = QLabel(_fmt_currency(total))
        lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:13px;font-weight:600;color:{C_SUCCESS};background:transparent;")
        lay.addWidget(lbl)
        return w

    def _make_action_buttons(self, purchase) -> QWidget:
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
                background: #EEFCEF; color: {C_SUCCESS};
                font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                border-radius: 7px; border: none; padding: 0;
            }}
            QPushButton:hover {{ background: {C_SUCCESS}; color: #FFFFFF; }}
        """)
        detail_btn.clicked.connect(lambda: self.detail_clicked.emit(purchase))
        lay.addWidget(detail_btn)

        edit_btn = QPushButton("Edit")
        edit_btn.setFixedSize(54, 28)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_TAG_BG}; color: {C_ACCENT};
                font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                border-radius: 7px; border: none; padding: 0;
            }}
            QPushButton:hover {{ background: {C_ACCENT}; color: #FFFFFF; }}
        """)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(purchase))
        lay.addWidget(edit_btn)

        del_btn = QPushButton("Hapus")
        del_btn.setFixedSize(64, 28)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FDEAEA; color: {C_DANGER};
                font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                border-radius: 7px; border: none; padding: 0;
            }}
            QPushButton:hover {{ background: {C_DANGER}; color: #FFFFFF; }}
        """)
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(purchase))
        lay.addWidget(del_btn)

        return w


# ═══════════════════════════════════════════════════════════════════════════════
# Purchase Dialog (Add / Edit)
# ═══════════════════════════════════════════════════════════════════════════════
class PurchaseDialog(QDialog):
    saved = pyqtSignal(dict)

    def __init__(self, parent=None, purchase=None, current_user: dict = None):
        super().__init__(parent)
        self._purchase = purchase
        self._is_edit = purchase is not None
        self._current_user = current_user or {}
        self.setWindowTitle("Edit Pembelian" if self._is_edit else "Tambah Pembelian")
        self.setModal(True)
        self.setFixedWidth(440)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setSizeGripEnabled(False)
        self.setStyleSheet(f"QDialog {{ background: {C_WHITE}; font-family: 'Segoe UI'; }}")
        self._build_ui()
        self.adjustSize()
        self.setMaximumSize(440, self.height())
    
    def _make_datetime(self, parent_layout, label_text: str):
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent; border: none;")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(5)

        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size:12px;font-weight:500;color:#5F5E5A;border:none;")
        wl.addWidget(lbl)

        dt_edit = QDateTimeEdit()
        dt_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        dt_edit.setDateTime(QDateTime.currentDateTime())
        dt_edit.setCalendarPopup(True)
        dt_edit.setFixedHeight(40)
        arrow_lbl = QLabel("⌄", dt_edit)
        arrow_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 18px; font-weight: 600;
            color: {C_TEXT_SEC}; background: transparent; border: none;
        """)
        arrow_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        QTimer.singleShot(0, lambda: arrow_lbl.setGeometry(dt_edit.width() - 28, -4, 24, 40))
        dt_edit.setStyleSheet(f"""
            QDateTimeEdit {{
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }}
            QDateTimeEdit:focus {{ border: 1px solid #4F6EF7; }}
            QDateTimeEdit:hover {{ border: 1px solid #B4B0AA; }}
            QDateTimeEdit::drop-down {{
                border: none; width: 32px;
            }}
            QCalendarWidget QWidget {{
                background: #FFFFFF; color: #1b1b1b;
                font-family: 'Segoe UI'; font-size: 12px;
                alternate-background-color: #F7F9FC;
            }}
            QCalendarWidget QToolButton {{
                background: {C_ACCENT}; color: #FFFFFF;
                border-radius: 6px; padding: 4px 10px;
                font-family: 'Segoe UI'; font-size: 12px; font-weight: 600;
                border: none;
            }}
            QCalendarWidget QToolButton:hover {{ background: {C_ACCENT_H}; }}
            QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
            QCalendarWidget QSpinBox {{
                background: #FFFFFF; border: 1px solid {C_BORDER};
                border-radius: 6px; padding: 2px 6px;
                font-family: 'Segoe UI'; font-size: 12px; color: #1b1b1b;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                background: #FFFFFF; color: #1b1b1b;
                selection-background-color: {C_ACCENT};
                selection-color: #FFFFFF;
            }}
            QCalendarWidget QAbstractItemView:disabled {{ color: #C0C0C0; }}
            QCalendarWidget #qt_calendar_navigationbar {{
                background: #F4F5F9; border-bottom: 1px solid {C_BORDER};
                border-radius: 0px; padding: 4px;
            }}
            QCalendarWidget #qt_calendar_prevmonth,
            QCalendarWidget #qt_calendar_nextmonth {{
                background: transparent; color: {C_ACCENT};
                border: none; border-radius: 6px;
                padding: 4px 8px; font-size: 14px; font-weight: 700;
            }}
            QCalendarWidget #qt_calendar_prevmonth:hover,
            QCalendarWidget #qt_calendar_nextmonth:hover {{
                background: {C_TAG_BG};
            }}
        """)

        err = QLabel("")
        err.setStyleSheet("font-size:11px;color:#E05252;font-family:'Segoe UI';border:none;")
        err.setVisible(False)
        wl.addWidget(dt_edit)
        wl.addWidget(err)

        parent_layout.addWidget(wrap)
        parent_layout.addSpacing(10)
        return dt_edit, err
        
    def _make_field(self, parent_layout, label_text: str, placeholder: str = ""):
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent; border: none;")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(5)

        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size:12px;font-weight:500;color:#5F5E5A;border:none;")
        wl.addWidget(lbl)

        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(40)
        field.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }
            QLineEdit:focus { border: 1px solid #4F6EF7; }
            QLineEdit:hover { border: 1px solid #B4B0AA; }
        """)
        wl.addWidget(field)

        err = QLabel("")
        err.setStyleSheet("font-size:11px;color:#E05252;font-family:'Segoe UI';border:none;")
        err.setVisible(False)
        wl.addWidget(err)

        parent_layout.addWidget(wrap)
        parent_layout.addSpacing(10)
        return field, err

    def _make_spin(self, parent_layout, label_text: str, is_float: bool = False, min_val=0, max_val=9999999):
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent; border: none;")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(5)

        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size:12px;font-weight:500;color:#5F5E5A;border:none;")
        wl.addWidget(lbl)

        spin_style = """
            QDoubleSpinBox, QSpinBox {
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
                height: 40px;
            }
            QDoubleSpinBox:focus, QSpinBox:focus { border: 1px solid #4F6EF7; }
            QDoubleSpinBox:hover, QSpinBox:hover { border: 1px solid #B4B0AA; }
            QDoubleSpinBox::up-button, QSpinBox::up-button,
            QDoubleSpinBox::down-button, QSpinBox::down-button { width: 0; }
        """
        if is_float:
            spin = QDoubleSpinBox()
            spin.setDecimals(2)
        else:
            spin = QSpinBox()
        spin.setMinimum(min_val)
        spin.setMaximum(max_val)
        spin.setFixedHeight(40)
        spin.setStyleSheet(spin_style)
        wl.addWidget(spin)

        err = QLabel("")
        err.setStyleSheet("font-size:11px;color:#E05252;font-family:'Segoe UI';border:none;")
        err.setVisible(False)
        wl.addWidget(err)

        parent_layout.addWidget(wrap)
        parent_layout.addSpacing(10)
        return spin, err

    def _show_field_error(self, field: QLineEdit, err: QLabel, msg: str):
        field.setStyleSheet("""
            QLineEdit {
                background: #FFF8F8; border: 1px solid #E05252;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }
        """)
        err.setText(msg)
        err.setVisible(True)

    def _clear_field_error(self, field: QLineEdit, err: QLabel):
        field.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }
            QLineEdit:focus { border: 1px solid #4F6EF7; }
            QLineEdit:hover { border: 1px solid #B4B0AA; }
        """)
        err.setVisible(False)

    def _make_combo(self, parent_layout, label_text: str):
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent; border: none;")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(5)

        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size:12px;font-weight:500;color:#5F5E5A;border:none;")
        wl.addWidget(lbl)

        combo = QComboBox()
        combo.setFixedHeight(40)
        arrow_lbl = QLabel("⌄", combo)
        arrow_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 18px; font-weight: 600;
            color: {C_TEXT_SEC}; background: transparent; border: none;
        """)
        arrow_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        QTimer.singleShot(0, lambda: arrow_lbl.setGeometry(combo.width() - 28, -4, 24, 40))
        combo.setStyleSheet(f"""
            QComboBox {{
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }}
            QComboBox:focus {{ border: 1px solid #4F6EF7; }}
            QComboBox:hover {{ border: 1px solid #B4B0AA; }}
            QComboBox::drop-down {{
                border: none; width: 28px;
            }}
            QComboBox QAbstractItemView {{
                background: #FFFFFF; border: 1px solid {C_BORDER};
                selection-color: {C_ACCENT}; font-size: 13px;
                font-family: 'Segoe UI'; outline: none;
                padding: 4px;
            }}
        """)

        err = QLabel("")
        err.setStyleSheet("font-size:11px;color:#E05252;font-family:'Segoe UI';border:none;")
        err.setVisible(False)
        wl.addWidget(combo)
        wl.addWidget(err)

        parent_layout.addWidget(wrap)
        parent_layout.addSpacing(10)
        return combo, err

    def _make_readonly_field(self, parent_layout, label_text: str, value: str):
        """Field yang tidak bisa diedit — untuk user yang sedang login."""
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent; border: none;")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(5)

        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size:12px;font-weight:500;color:#5F5E5A;border:none;")
        wl.addWidget(lbl)

        field = QLineEdit(value)
        field.setFixedHeight(40)
        field.setReadOnly(True)
        field.setStyleSheet(f"""
            QLineEdit {{
                background: #F4F5F9; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: {C_TEXT_SEC}; font-family: 'Segoe UI';
            }}
        """)
        wl.addWidget(field)

        parent_layout.addWidget(wrap)
        parent_layout.addSpacing(10)

    def _build_ui(self):
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
        cl.addSpacing(15)

        title = QLabel("Edit Pembelian" if self._is_edit else "Tambah Pembelian Baru")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)
        cl.addSpacing(5)

        subtitle_text = (
            f"Ubah informasi untuk pembelian <b>#{self._purchase.id}</b>."
            if self._is_edit else
            "Isi informasi pembelian baru dari supplier."
        )
        subtitle = QLabel(subtitle_text)
        subtitle.setTextFormat(Qt.TextFormat.RichText)
        subtitle.setStyleSheet("font-size:12px;color:#888780;border:none;")
        cl.addWidget(subtitle)
        cl.addSpacing(16)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider)
        cl.addSpacing(18)

        # ── Supplier dropdown ─────────────────────────────────────────────────
        self._supplier_combo, self._supplier_err = self._make_combo(cl, "Supplier")
        self._suppliers = SupplierController.fetch()
        for s in self._suppliers:
            self._supplier_combo.addItem(f"{s.name}", userData=s.id)

        if not self._suppliers:
            self._supplier_combo.addItem("(Tidak ada supplier)", userData=None)
            self._supplier_combo.setEnabled(False)

        # Preselect supplier saat edit
        if self._is_edit:
            for i, s in enumerate(self._suppliers):
                if s.id == self._purchase.supplier_id:
                    self._supplier_combo.setCurrentIndex(i)
                    break

        # ── User (read-only, dari login) ──────────────────────────────────────
        user_id   = self._current_user.get("id", "")
        user_name = self._current_user.get("name") or self._current_user.get("username") or f"User #{user_id}"
        self._make_readonly_field(cl, "Dibuat oleh", f"{user_name}")

        # ── Waktu & Total ─────────────────────────────────────────────────────
        self._time_edit, self._time_err = self._make_datetime(cl, "Waktu")

        if self._is_edit:
            if self._purchase.time:
                dt = QDateTime.fromString(self._purchase.time[:19], "yyyy-MM-dd HH:mm:ss")
                if dt.isValid():
                    self._time_edit.setDateTime(dt)

        cl.addSpacing(12)

        # ── Tombol ────────────────────────────────────────────────────────────
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

        save_btn = QPushButton("Simpan Perubahan" if self._is_edit else "Tambah Pembelian")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 600;
                border-radius: 10px; border: none;
            }}
            QPushButton:hover {{ background: {C_ACCENT_H}; }}
        """)
        save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        cl.addLayout(btn_row)
        root.addWidget(card)

    def _on_save(self):
        self._supplier_err.setVisible(False)
        self._time_err.setVisible(False)

        valid = True

        supplier_id = self._supplier_combo.currentData()
        if supplier_id is None:
            self._supplier_err.setText("Pilih supplier terlebih dahulu.")
            self._supplier_err.setVisible(True)
            valid = False

        if not valid:
            return

        # Ambil waktu dari QDateTimeEdit, bukan QLineEdit
        time_val = self._time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        payload = {
            "supplier_id":  supplier_id,
            "user_id":      self._current_user.get("id"),
            "time":         time_val,
            "total_amount": 0
        }
        if self._is_edit:
            payload["id"] = self._purchase.id

        self.saved.emit(payload)
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
# Purchase Detail Dialog (view + manage items)
# ═══════════════════════════════════════════════════════════════════════════════
class PurchaseDetailDialog(QDialog):
    data_changed = pyqtSignal()
    def __init__(self, purchase, parent=None):
        super().__init__(parent)
        self._purchase = purchase
        self.setWindowTitle(f"Detail Pembelian #{purchase.id}")
        self.setModal(True)
        self.setFixedWidth(620)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setSizeGripEnabled(False)
        self.setStyleSheet(f"QDialog {{ background: {C_WHITE}; font-family: 'Segoe UI'; }}")
        self._build_ui()
        self._load_details()
        self.adjustSize()
        self.setMaximumSize(620, self.sizeHint().height() + 60)
        
    def _refresh_meta(self):
        self._purchase = PurchaseController.get(self._purchase.id)

        supplier = SupplierController.get(self._purchase.supplier_id)
        user_map = {u[0]: u[1] for u in UserController.fetch()}

        supplier_name = supplier.name if supplier else f"Supplier #{self._purchase.supplier_id}"
        user_name = user_map.get(self._purchase.user_id, f"User #{self._purchase.user_id}")

        self._meta.setText(
            f"{supplier_name}  ·  {user_name}  ·  {_fmt_date(self._purchase.time)}  ·  "
            f"<b style='color:{C_SUCCESS}'>{_fmt_currency(self._purchase.total_amount)}</b>"
        )

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #FAFAF8; border: 1px solid #DDD9D2; }")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(36, 28, 36, 28)
        cl.setSpacing(0)

        logo = QLabel("Warung<span style='color:#4F6EF7'>+</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("font-size:14px;color:#5F5E5A;font-weight:500;letter-spacing:1px;border:none;")
        cl.addWidget(logo)
        cl.addSpacing(10)

        p = self._purchase
        title = QLabel(f"Detail Pembelian #{p.id:04d}")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)
        cl.addSpacing(4)
        supplier = SupplierController.get(p.supplier_id)
        user = UserController.fetch()

        # bikin map user_id → name
        user_map = {u[0]: u[1] for u in user}

        supplier_name = supplier.name if supplier else f"Supplier #{p.supplier_id}"
        user_name = user_map.get(p.user_id, f"User #{p.user_id}")
        
        self._meta = QLabel(
            f"{supplier_name}  ·  {user_name}  ·  {_fmt_date(p.time)}  ·  "
            f"<b style='color:{C_SUCCESS}'>{_fmt_currency(p.total_amount)}</b>"
        )
        self._meta.setTextFormat(Qt.TextFormat.RichText)
        self._meta.setStyleSheet(f"font-size:12px;color:{C_TEXT_SEC};border:none;")
        cl.addWidget(self._meta)
        cl.addSpacing(14)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider)
        cl.addSpacing(14)

        # ── Add detail form ────────────────────────────────────────────────────
        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        def _spin(min_v=0, max_v=9_999_999, is_float=False):
            if is_float:
                s = QDoubleSpinBox(); s.setDecimals(2)
            else:
                s = QSpinBox()
            s.setMinimum(min_v); s.setMaximum(max_v)
            s.setFixedHeight(36)
            s.setStyleSheet("""
                QDoubleSpinBox, QSpinBox {
                    background: #FFFFFF; border: 1px solid #DDD9D2;
                    border-radius: 8px; padding: 0 10px;
                    font-size: 12px; color: #1b1b1b; font-family: 'Segoe UI';
                }
                QDoubleSpinBox:focus, QSpinBox:focus { border: 1px solid #4F6EF7; }
                QDoubleSpinBox::up-button, QSpinBox::up-button,
                QDoubleSpinBox::down-button, QSpinBox::down-button { width: 0; }
            """)
            return s

        # Dropdown produk
        self._products = ProductController.fetch()
        self._new_product_combo = QComboBox()
        self._new_product_combo.setFixedHeight(36)
        arrow_lbl = QLabel("⌄", self._new_product_combo)
        arrow_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 18px; font-weight: 600;
            color: {C_TEXT_SEC}; background: transparent; border: none;
        """)
        arrow_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        QTimer.singleShot(0, lambda: arrow_lbl.setGeometry(self._new_product_combo.width() - 28, -6, 24, 40))
        self._new_product_combo.setStyleSheet(f"""
            QComboBox {{
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 10px;
                font-size: 12px; color: #1b1b1b; font-family: 'Segoe UI';
            }}
            QComboBox:focus {{ border: 1px solid #4F6EF7; }}
            QComboBox::drop-down {{ border: none; width: 24px; }}
            QComboBox QAbstractItemView {{
                background: #FFFFFF; border: 1px solid {C_BORDER};
                selection-background-color: {C_TAG_BG};
                selection-color: {C_ACCENT};
                font-size: 12px; font-family: 'Segoe UI';
                outline: none; padding: 4px;
            }}
        """)
        for p in self._products:
            label = f"{p.name}" + (f" ({p.brand})" if p.brand else "")
            self._new_product_combo.addItem(label, userData=p.id)
        if not self._products:
            self._new_product_combo.addItem("(Tidak ada produk)", userData=None)
            self._new_product_combo.setEnabled(False)

        self._new_qty_spin   = _spin(min_v=1)
        self._new_price_spin = _spin(is_float=False, max_v=999_999_999)

        for lbl_text, widget in [
            ("Produk",      self._new_product_combo),
            ("Qty",         self._new_qty_spin),
            ("Harga (Rp)",  self._new_price_spin),
        ]:
            col = QVBoxLayout(); col.setSpacing(5)
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet(f"font-size:11px;font-weight:500;color:{C_TEXT_SEC};border:none;")
            col.addWidget(lbl); col.addWidget(widget)
            add_row.addLayout(col)

        add_item_btn = QPushButton("+ Tambah")
        add_item_btn.setFixedSize(90, 36)
        add_item_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_item_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 12px; font-weight: 600;
                border-radius: 8px; border: none;
            }}
            QPushButton:hover {{ background: {C_ACCENT_H}; }}
        """)
        add_item_btn.clicked.connect(self._on_add_detail)

        add_col = QVBoxLayout()
        add_col.setSpacing(3)
        add_col.setContentsMargins(0, 0, 0, 0)

        add_col.addWidget(add_item_btn, alignment=Qt.AlignmentFlag.AlignBottom)
        add_row.addLayout(add_col)

        cl.addLayout(add_row)
        cl.addSpacing(12)

        # ── Detail table ──────────────────────────────────────────────────────
        self._detail_table = QTableWidget()
        self._detail_table.setColumnCount(5)
        self._detail_table.setHorizontalHeaderLabels(["#", "Produk", "Qty", "Harga", "Aksi"])
        self._detail_table.setFixedHeight(220)
        self._detail_table.setAlternatingRowColors(True)
        self._detail_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self._detail_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._detail_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._detail_table.verticalHeader().setVisible(False)
        self._detail_table.setFrameShape(QFrame.Shape.NoFrame)
        self._detail_table.setShowGrid(True)
        self._detail_table.setGridStyle(Qt.PenStyle.SolidLine)

        dh = self._detail_table.horizontalHeader()
        dh.setHighlightSections(False)
        dh.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        dh.setFixedHeight(36)
        dh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        dh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        dh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        dh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        dh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._detail_table.setColumnWidth(0, 36)
        self._detail_table.setColumnWidth(1, 100)
        self._detail_table.setColumnWidth(2, 70)
        self._detail_table.setColumnWidth(4, 70)

        self._detail_table.setStyleSheet(f"""
            QTableWidget {{
                background: {C_WHITE}; border: 1px solid {C_BORDER};
                border-radius: 10px; font-family:'Segoe UI'; font-size:12px;
                color:{C_TEXT_PRI}; outline:none; gridline-color:{C_DIVIDER};
                alternate-background-color:#F7F9FC;
            }}
            QTableWidget::item {{
                background: transparent; border: none;
                border-right: 1px solid {C_DIVIDER};
                border-bottom: 1px solid {C_DIVIDER};
                padding: 4px 8px;
            }}
            QHeaderView::section {{
                background: {C_HEADER_BG}; color:{C_HEADER_TEXT};
                font-size:10px; font-weight:700; padding-left:10px;
                border:none; border-right:1px solid {C_DIVIDER};
                border-bottom:1px solid {C_BORDER};
            }}
            QScrollBar:vertical {{
                background:transparent; width:5px; border-radius:3px;
            }}
            QScrollBar::handle:vertical {{
                background:{C_BORDER}; border-radius:3px; min-height:20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
            QScrollBar:horizontal {{ height:0; }}
        """)
        cl.addWidget(self._detail_table)
        cl.addSpacing(16)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cl.addLayout(btn_row)

        root.addWidget(card)

    def _load_details(self):
        all_details = PurchaseDetailController.fetch()
        self._details = [d for d in all_details if d.purchase_id == self._purchase.id]
        self._product_map = {p.id: p.name for p in ProductController.fetch()}
        self._populate_detail_table()

    def _populate_detail_table(self):
        self._detail_table.clearContents()
        self._detail_table.setRowCount(0)

        if not self._details:
            self._detail_table.setRowCount(1)
            self._detail_table.setSpan(0, 0, 1, 5)
            self._detail_table.setRowHeight(0, 80)
            empty_lbl = QLabel("Belum ada item detail.")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet(f"color:{C_TEXT_SEC};font-size:12px;background:transparent;border:none;")
            self._detail_table.setCellWidget(0, 0, empty_lbl)
            return

        for i, d in enumerate(self._details):
            row = self._detail_table.rowCount()
            self._detail_table.insertRow(row)
            self._detail_table.setRowHeight(row, 40)

            def _item(text, align=Qt.AlignmentFlag.AlignLeft):
                it = QTableWidgetItem(text)
                it.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
                it.setFlags(Qt.ItemFlag.ItemIsEnabled)
                return it

            self._detail_table.setItem(row, 0, _item(str(i + 1), Qt.AlignmentFlag.AlignCenter))
            product_name = self._product_map.get(d.product_id, f"Product #{d.product_id}")
            self._detail_table.setItem(row, 1, _item(product_name))
            self._detail_table.setItem(row, 2, _item(str(d.quantity)))
            self._detail_table.setItem(row, 3, _item(_fmt_currency(d.purchase_price)))

            del_w = QWidget()
            del_w.setStyleSheet("background: transparent; border: none;")
            del_lay = QHBoxLayout(del_w)
            del_lay.setContentsMargins(4, 0, 4, 0)
            del_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            del_b = QPushButton("✕")
            del_b.setFixedSize(28, 24)
            del_b.setCursor(Qt.CursorShape.PointingHandCursor)
            del_b.setStyleSheet(f"""
                QPushButton {{
                    background:#FDEAEA; color:{C_DANGER};
                    font-size:11px; font-weight:700;
                    border-radius:6px; border:none;
                }}
                QPushButton:hover {{ background:{C_DANGER}; color:#FFFFFF; }}
            """)
            del_b.clicked.connect(lambda _, did=d.id: self._on_remove_detail(did))
            del_lay.addWidget(del_b)
            self._detail_table.setCellWidget(row, 4, del_w)

    def _on_add_detail(self):
        product_id = self._new_product_combo.currentData()
        if product_id is None:
            QMessageBox.warning(self, "Perhatian", "Pilih produk terlebih dahulu.")
            return

        quantity       = self._new_qty_spin.value()
        purchase_price = self._new_price_spin.value()

        try:
            PurchaseDetailController.add(
                purchase_id=self._purchase.id,
                product_id=product_id,
                quantity=quantity,
                purchase_price=purchase_price,
            )

            # 🔥 WAJIB: update total
            PurchaseDetailController.update_purchase_total(self._purchase.id)

            self._new_qty_spin.setValue(1)
            self._new_price_spin.setValue(0)

            self._load_details()
            self._refresh_meta()
            
            self.data_changed.emit()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_remove_detail(self, detail_id: int):
        try:
            PurchaseDetailController.remove(detail_id)
            PurchaseDetailController.update_purchase_total(self._purchase.id)
            self._load_details()
            self._refresh_meta()
            
            self.data_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Delete Purchase Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class DeletePurchaseDialog(QDialog):
    confirmed = pyqtSignal()

    def __init__(self, purchase, parent=None):
        super().__init__(parent)
        self._purchase = purchase
        self.setWindowTitle("Hapus Pembelian")
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
        p = self._purchase
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #FAFAF8; border: 1px solid #DDD9D2; }")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(36, 30, 36, 30)
        cl.setSpacing(0)

        logo = QLabel("Warung<span style='color:#4F6EF7'>+</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("font-size:14px;color:#5F5E5A;font-weight:500;letter-spacing:1px;border:none;")
        cl.addWidget(logo)

        title = QLabel("Hapus Pembelian?")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)

        subtitle = QLabel(
            f"Kamu akan menghapus pembelian <b>#{p.id:04d}</b>.<br>"
            "Semua detail item akan ikut terhapus. Tindakan ini tidak dapat dibatalkan."
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

        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{ background:{C_WHITE}; border:1px solid #E4E6EE; border-radius:10px; }}
            QLabel {{ background:transparent; border:none; }}
        """)
        info_lay = QHBoxLayout(info_card)
        info_lay.setContentsMargins(14, 12, 14, 12)
        info_lay.setSpacing(12)

        icon_lbl = QLabel("🛒")
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size:18px;background:#EEF1FE;border-radius:8px;")

        detail = QVBoxLayout()
        detail.setSpacing(2)
        id_lbl   = QLabel(f"Pembelian #{p.id:04d}")
        id_lbl.setStyleSheet(f"font-size:13px;font-weight:600;color:{C_TEXT_PRI};")
        meta_lbl = QLabel(f"Supplier #{p.supplier_id}  ·  {_fmt_date(p.time)}  ·  {_fmt_currency(p.total_amount)}")
        meta_lbl.setStyleSheet(f"font-size:11px;color:{C_TEXT_SEC};")
        detail.addWidget(id_lbl)
        detail.addWidget(meta_lbl)

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

        delete_btn = QPushButton("Ya, Hapus Pembelian")
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
# View Toggle (reused pattern)
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
        self.setStyleSheet(f"QWidget {{ background: {C_WHITE}; border: 1px solid {C_BORDER}; border-radius: 10px; }}")
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
# Purchase Page
# ═══════════════════════════════════════════════════════════════════════════════
class PurchasePage(QWidget):
    def __init__(self, user: dict = None, parent=None):
        super().__init__(parent)
        self._user             = user or {}
        self._purchases        = self._load_purchases()
        self._search_query     = ""
        self._view_mode        = ViewToggle.VIEW_TABLE
        self._grid_initialized = False
        self._pending_refresh  = False
        self._render_token     = 0
        self._stat_value_labels: dict[str, tuple] = {}

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C_BG};")
        self._build_ui()

    def _load_purchases(self) -> list:
        return PurchaseController.fetch()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 17, 32, 28)
        layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Manajemen Pembelian")
        page_title.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 27px; font-weight: 700;
            color: {C_TEXT_PRI}; background: transparent;
        """)
        page_sub = QLabel("Kelola semua transaksi pembelian dari supplier di sini")
        page_sub.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 13px;
            color: {C_TEXT_SEC}; background: transparent;
        """)
        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        add_btn = QPushButton("+ Tambah Pembelian")
        add_btn.setFixedHeight(42)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 600;
                border-radius: 10px; padding: 0 20px; border: none;
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

        # ── Filter bar + view toggle ──────────────────────────────────────────
        filter_and_toggle = QHBoxLayout()
        filter_and_toggle.setSpacing(10)

        filter_widget = QWidget()
        filter_widget.setStyleSheet("background: transparent;")
        fw_layout = QHBoxLayout(filter_widget)
        fw_layout.setContentsMargins(0, 0, 0, 0)
        fw_layout.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("🔍  Cari supplier, user, atau tanggal...")
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
        fw_layout.addWidget(search, stretch=1)
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
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; background: none; }}
            QScrollBar:horizontal {{
                background: transparent; height: 8px;
                margin: 0 0 2px 0; border-radius: 3px;
            }}
            QScrollBar::handle:horizontal {{
                background: {C_BORDER}; border-radius: 3px; min-width: 28px;
            }}
            QScrollBar::handle:horizontal:hover {{ background: #B8BCCE; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; background: none; }}
        """)

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet("background: transparent;")
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setSpacing(14)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        for col in range(4):
            self._grid_layout.setColumnStretch(col, 1)
        self._grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._scroll.setWidget(self._grid_container)
        card_layout.addWidget(self._scroll)

        # Page 1: Table
        self._table_page = QWidget()
        self._table_page.setStyleSheet("background: transparent;")
        table_layout = QVBoxLayout(self._table_page)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self._table_view = PurchaseTableView()
        self._table_view.edit_clicked.connect(self._open_edit_dialog)
        self._table_view.delete_clicked.connect(self._delete_purchase)
        self._table_view.detail_clicked.connect(self._open_detail_dialog)
        table_layout.addWidget(self._table_view)

        self._content_stack.addWidget(self._card_page)   # index 0
        self._content_stack.addWidget(self._table_page)  # index 1
        self._content_stack.setCurrentIndex(1)

        layout.addWidget(self._content_stack, stretch=1)

    # ── Stats ──────────────────────────────────────────────────────────────────
    def _calc_stats(self) -> dict:
        total_amount = sum(p.total_amount or 0 for p in self._purchases)
        return {
            "total":    str(len(self._purchases)),
            "suppliers": str(len({p.supplier_id for p in self._purchases})),
            "amount":   _fmt_currency(total_amount),
        }

    def _build_stats_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(14)
        values = self._calc_stats()
        stats = [
            ("total",    "Total Pembelian",   values["total"],    "#4F6EF7", "#EEF1FE"),
            ("suppliers","Supplier Aktif",    values["suppliers"],"#F39C12", "#FFF8E8"),
            ("amount",   "Total Pengeluaran", values["amount"],   "#27AE60", "#E8F8F0"),
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

        dot = QLabel()
        if key == "amount":
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
                dot.setText(value)
                val_lbl.setText(value)

    # ── Data / filter ──────────────────────────────────────────────────────────
    def _filtered_purchases(self) -> list:
        result = self._purchases

        suppliers = SupplierController.fetch()
        users = UserController.fetch()

        supplier_map = {s.id: s.name.lower() for s in suppliers}
        user_map = {u[0]: u[1].lower() for u in users}

        if self._search_query:
            q = self._search_query.lower()

            result = [
                p for p in result
                if q in supplier_map.get(p.supplier_id, "")
                or q in user_map.get(p.user_id, "")
                or q in (p.time or "").lower()
                or q in str(p.id)
            ]

        return result

    # ── Refresh ────────────────────────────────────────────────────────────────
    def _refresh_view(self):
        if self._view_mode == ViewToggle.VIEW_CARD:
            self._refresh_grid()
        else:
            self._refresh_table()

    def _refresh_table(self):
        self._table_view.populate(self._filtered_purchases())

    def _refresh_grid(self):
        self._render_token += 1
        token = self._render_token

        if not self.isVisible():
            self._pending_refresh = True
            return

        self._pending_refresh = False
        self._clear_grid()
        purchases = self._filtered_purchases()

        if not purchases:
            empty_wrap = QWidget()
            empty_wrap.setStyleSheet("background: transparent; border: none;")
            outer = QVBoxLayout(empty_wrap)
            outer.setContentsMargins(0, 34, 0, 40)
            outer.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

            empty_card = QFrame()
            empty_card.setFixedHeight(260)
            empty_card.setMinimumWidth(420)
            empty_card.setMaximumWidth(560)
            empty_card.setStyleSheet(f"""
                QFrame {{ background:{C_WHITE}; border:1px solid {C_BORDER}; border-radius:18px; }}
                QLabel {{ background:transparent; border:none; }}
            """)
            card_layout = QVBoxLayout(empty_card)
            card_layout.setContentsMargins(40, 34, 40, 34)
            card_layout.setSpacing(8)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon = QLabel("🛒")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setStyleSheet("font-size: 46px;")
            title = QLabel("Tidak ada pembelian ditemukan")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet(f"font-family:'Segoe UI';font-size:16px;font-weight:700;color:{C_TEXT_PRI};")
            subtitle = QLabel("Coba ubah filter, kata kunci pencarian,\natau tambahkan pembelian baru.")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle.setStyleSheet(f"font-family:'Segoe UI';font-size:12px;color:{C_TEXT_SEC};")

            card_layout.addStretch()
            card_layout.addWidget(icon)
            card_layout.addWidget(title)
            card_layout.addWidget(subtitle)
            card_layout.addStretch()
            outer.addWidget(empty_card)
            self._grid_layout.addWidget(empty_wrap, 0, 0, 1, 4)
            self._grid_container.adjustSize()
            return

        for i, purchase in enumerate(purchases):
            if token != self._render_token:
                return
            card = PurchaseCard(purchase)
            card.edit_clicked.connect(self._open_edit_dialog)
            card.delete_clicked.connect(self._delete_purchase)
            card.detail_clicked.connect(self._open_detail_dialog)
            self._grid_layout.addWidget(card, i // 4, i % 4)

        self._grid_container.setMinimumWidth(5 * 180 + 4 * self._grid_layout.spacing())
        self._grid_container.adjustSize()
        self._grid_container.update()
        self._scroll.viewport().update()

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

    def _open_add_dialog(self):
        dlg = PurchaseDialog(parent=self, current_user=self._user)
        dlg.saved.connect(self._add_purchase)
        dlg.exec()

    def _open_edit_dialog(self, purchase):
        dlg = PurchaseDialog(parent=self, purchase=purchase, current_user=self._user)
        dlg.saved.connect(self._edit_purchase)
        dlg.exec()

    def _open_detail_dialog(self, purchase):
        dlg = PurchaseDetailDialog(purchase=purchase, parent=self)
        dlg.data_changed.connect(self._on_detail_changed)
        dlg.exec()
        
    def _on_detail_changed(self):
        self._purchases = self._load_purchases()
        self._refresh_stats()
        self._refresh_view()

    def _add_purchase(self, data: dict):
        try:
            PurchaseController.add(
                supplier_id=data["supplier_id"],
                user_id=data["user_id"],
                time=data["time"],
                total_amount=data["total_amount"],
            )
            self._purchases = self._load_purchases()
            self._refresh_stats()
            self._refresh_view()
            Toast.show_toast(f"Pembelian <b>#{data.get('id', '')}</b> berhasil ditambahkan.", "success", self)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _edit_purchase(self, data: dict):
        try:
            PurchaseController.edit(
                purchase_id=data["id"],
                supplier_id=data["supplier_id"],
                user_id=data["user_id"],
                time=data["time"],
                total_amount=data["total_amount"],
            )
            self._purchases = self._load_purchases()
            self._refresh_stats()
            self._refresh_view()
            Toast.show_toast(f"Pembelian <b>#{data['id']}</b> berhasil diperbarui.", "success", self)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _delete_purchase(self, purchase):
        def do_delete():
            try:
                PurchaseController.remove(purchase.id)
                self._purchases = self._load_purchases()
                self._refresh_stats()
                self._refresh_view()
                Toast.show_toast(f"Pembelian <b>#{purchase.id}</b> berhasil dihapus.", "success", self)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        dlg = DeletePurchaseDialog(purchase=purchase, parent=self)
        dlg.confirmed.connect(do_delete)
        dlg.exec()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._grid_initialized or self._pending_refresh:
            self._grid_initialized = True
            self._pending_refresh  = False
            QTimer.singleShot(0, self._refresh_view)