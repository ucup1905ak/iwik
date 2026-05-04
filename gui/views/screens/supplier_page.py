from controllers.supplier import SupplierController, Supplier
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFrame,
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
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRegularExpression 
from PyQt6.QtGui import QColor, QPainterPath, QRegion, QFont,  QRegularExpressionValidator
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


# ── Helpers ────────────────────────────────────────────────────────────────────
_PALETTES = [
    ("#EEF0FD", "#3B52C4"),
    ("#FDF0EC", "#B04A28"),
    ("#E6F1FB", "#185FA5"),
    ("#EAF3DE", "#3B6D11"),
    ("#FDF6EC", "#B07A28"),
    ("#F3ECFD", "#7B28B0"),
]

def _supplier_palette(name: str):
    parts = name.strip().split()
    initials = (parts[0][0] + parts[1][0]).upper() if len(parts) >= 2 else (name[:2].upper())
    idx = (ord(initials[0]) - ord("A")) % len(_PALETTES)
    return _PALETTES[idx], initials


# ═══════════════════════════════════════════════════════════════════════════════
# Supplier Card
# ═══════════════════════════════════════════════════════════════════════════════
class SupplierCard(QFrame):
    edit_clicked   = pyqtSignal(object)
    delete_clicked = pyqtSignal(object)

    def __init__(self, supplier: Supplier, parent=None):
        super().__init__(parent)
        self._supplier = supplier
        self._build()

    def _build(self):
        self.setObjectName("SupplierCard")
        self.setFixedHeight(148)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame#SupplierCard {{
                background:    {C_WHITE};
                border-radius: 14px;
                border:        1.5px solid {C_BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # ── Top row: Avatar + Nama ────────────────────────────────────────────
        top = QHBoxLayout()
        top.setSpacing(12)

        (bg, fg), initials = _supplier_palette(self._supplier.name)
        avatar = Avatar(initials, bg_color=bg, text_color=fg, size=38)
        top.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(4)
        info.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(self._supplier.name)
        name_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 14px; font-weight: 700;
            color: {C_TEXT_PRI}; background: transparent; border: none;
        """)
        info.addWidget(name_lbl)

        phone_text = self._supplier.phone or "—"
        phone_lbl = QLabel(f"📞  {phone_text}")
        phone_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 11px;
            color: {C_TEXT_SEC}; background: transparent; border: none;
        """)
        info.addWidget(phone_lbl)

        top.addLayout(info)
        top.addStretch()
        layout.addLayout(top)

        # ── Address ───────────────────────────────────────────────────────────
        addr_text = self._supplier.address or "Alamat belum diisi"
        addr_lbl = QLabel(f"📍  {addr_text}")
        addr_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 11px;
            color: {C_TEXT_SEC}; background: transparent; border: none;
        """)
        addr_lbl.setWordWrap(True)
        layout.addWidget(addr_lbl)

        layout.addStretch()

        # ── Bottom row: action buttons ────────────────────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(8)
        bottom.addStretch()

        edit_btn = QPushButton("Edit")
        edit_btn.setFixedSize(72, 28)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_TAG_BG}; color: {C_ACCENT};
                font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                border-radius: 7px; border: none;
            }}
            QPushButton:hover {{ background: {C_ACCENT}; color: #FFFFFF; }}
        """)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self._supplier))
        bottom.addWidget(edit_btn)

        del_btn = QPushButton("Hapus")
        del_btn.setFixedSize(82, 28)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FDEAEA; color: {C_DANGER};
                font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                border-radius: 7px; border: none;
            }}
            QPushButton:hover {{ background: {C_DANGER}; color: #FFFFFF; }}
        """)
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(self._supplier))
        bottom.addWidget(del_btn)

        layout.addLayout(bottom)


# ═══════════════════════════════════════════════════════════════════════════════
# Supplier Table View
# ═══════════════════════════════════════════════════════════════════════════════
class SupplierTableView(QTableWidget):
    edit_clicked   = pyqtSignal(object)
    delete_clicked = pyqtSignal(object)

    COLUMNS    = ["      #", "Nama", "Telepon", "Alamat", "Aksi"]
    COL_NO      = 0
    COL_NAME    = 1
    COL_PHONE   = 2
    COL_ADDRESS = 3
    COL_ACTION  = 4
    ROW_H       = 52

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

        header.setSectionResizeMode(self.COL_NO,      QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_NAME,    QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COL_PHONE,   QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_ADDRESS, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COL_ACTION,  QHeaderView.ResizeMode.Fixed)

        self.setColumnWidth(self.COL_NO,     44)
        self.setColumnWidth(self.COL_PHONE,  140)
        self.setColumnWidth(self.COL_ACTION, 160)

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

        icon = QLabel("🏭")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 46px;")
        title = QLabel("Tidak ada supplier ditemukan")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-family:'Segoe UI';font-size:16px;font-weight:700;color:{C_TEXT_PRI};")
        sub = QLabel("Coba ubah kata kunci pencarian,\natau tambahkan supplier baru.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"font-family:'Segoe UI';font-size:12px;color:{C_TEXT_SEC};")

        lay.addWidget(icon)
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addStretch()
        self.setCellWidget(0, 0, empty)

    def populate(self, suppliers: list[Supplier]):
        self.clearContents()
        self.setRowCount(0)

        if not suppliers:
            self._show_empty_state()
            return

        self.setShowGrid(True)
        for i, supplier in enumerate(suppliers):
            row = self.rowCount()
            self.insertRow(row)
            self.setRowHeight(row, self.ROW_H)

            row_bg = C_ROW_ALT if row % 2 == 1 else C_WHITE
            for col in range(len(self.COLUMNS)):
                ph = QTableWidgetItem()
                ph.setBackground(QColor(row_bg))
                ph.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.setItem(row, col, ph)

            self.setCellWidget(row, self.COL_NO,      self._make_no_cell(i + 1))
            self.setCellWidget(row, self.COL_NAME,    self._make_name_cell(supplier.name))
            self.setCellWidget(row, self.COL_PHONE,   self._make_text_cell(supplier.phone or "—"))
            self.setCellWidget(row, self.COL_ADDRESS, self._make_text_cell(supplier.address or "—"))
            self.setCellWidget(row, self.COL_ACTION,  self._make_action_buttons(supplier))

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

    def _make_name_cell(self, name: str) -> QWidget:
        w, lay = self._wrap()

        (bg, fg), initials = _supplier_palette(name)
        avatar = Avatar(initials, bg_color=bg, text_color=fg, size=30)
        lay.addWidget(avatar)
        lay.setSpacing(8)

        lbl = QLabel(name)
        lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:13px;font-weight:600;color:{C_TEXT_PRI};background:transparent;")
        lay.addWidget(lbl)
        return w

    def _make_text_cell(self, text: str) -> QWidget:
        w, lay = self._wrap()
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:12px;color:{C_TEXT_PRI};background:transparent;")
        lay.addWidget(lbl)
        return w

    def _make_action_buttons(self, supplier: Supplier) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(5, 0, 0, 0)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

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
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(supplier))
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
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(supplier))
        lay.addWidget(del_btn)

        return w


# ═══════════════════════════════════════════════════════════════════════════════
# Supplier Dialog (Add / Edit)
# ═══════════════════════════════════════════════════════════════════════════════
class SupplierDialog(QDialog):
    saved = pyqtSignal(dict)

    def __init__(self, parent=None, supplier: Supplier = None):
        super().__init__(parent)
        self._supplier = supplier
        self._is_edit  = supplier is not None
        self.setWindowTitle("Edit Supplier" if self._is_edit else "Tambah Supplier")
        self.setModal(True)
        self.setFixedWidth(440)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setSizeGripEnabled(False)
        self.setStyleSheet(f"QDialog {{ background: {C_WHITE}; font-family: 'Segoe UI'; }}")
        self._build_ui()
        self.adjustSize()
        self.setMaximumSize(440, self.height())

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

    def _make_multiline_field(self, parent_layout, label_text: str, placeholder: str = ""):
        from PyQt6.QtWidgets import QTextEdit
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent; border: none;")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(5)

        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size:12px;font-weight:500;color:#5F5E5A;border:none;")
        wl.addWidget(lbl)

        field = QTextEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(80)
        field.setStyleSheet("""
            QTextEdit {
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 8px 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }
            QTextEdit:focus { border: 1px solid #4F6EF7; }
            QTextEdit:hover { border: 1px solid #B4B0AA; }
        """)
        wl.addWidget(field)

        err = QLabel("")
        err.setStyleSheet("font-size:11px;color:#E05252;font-family:'Segoe UI';border:none;")
        err.setVisible(False)
        wl.addWidget(err)

        parent_layout.addWidget(wrap)
        parent_layout.addSpacing(10)
        return field, err

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

        title = QLabel("Edit Supplier" if self._is_edit else "Tambah Supplier Baru")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)
        cl.addSpacing(5)

        subtitle = QLabel(
            f"Ubah informasi untuk supplier <b>{self._supplier.name}</b>."
            if self._is_edit else
            "Isi informasi supplier baru untuk warungmu."
        )
        subtitle.setTextFormat(Qt.TextFormat.RichText)
        subtitle.setStyleSheet("font-size:12px;color:#888780;border:none;")
        cl.addWidget(subtitle)
        cl.addSpacing(16)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider)
        cl.addSpacing(18)

        self._name_field,    self._name_err    = self._make_field(cl, "Nama", "Contoh: PT Maju Bersama")
        self._phone_field,   self._phone_err   = self._make_field(cl, "Telepon (opsional)", "Contoh: 08123456789")
        regex = QRegularExpression("^[0-9]*$")
        self._phone_field.setValidator(QRegularExpressionValidator(regex))
        self._phone_field.setMaxLength(15)
        self._address_field, self._address_err = self._make_multiline_field(cl, "Alamat (opsional)", "Contoh: Jl. Pahlawan No. 10, Yogyakarta")

        if self._is_edit:
            self._name_field.setText(self._supplier.name)
            self._phone_field.setText(self._supplier.phone or "")
            self._address_field.setPlainText(self._supplier.address or "")

        cl.addSpacing(12)

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

        save_btn = QPushButton("Simpan Perubahan" if self._is_edit else "Tambah Supplier")
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

    @staticmethod
    def _show_error(field, err: QLabel, msg: str):
        field.setStyleSheet("""
            QLineEdit, QTextEdit {
                background: #FFF8F8; border: 1px solid #E05252;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }
        """)
        err.setText(msg)
        err.setVisible(True)

    @staticmethod
    def _clear_error(field, err: QLabel):
        field.setStyleSheet("""
            QLineEdit, QTextEdit {
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }
            QLineEdit:focus, QTextEdit:focus { border: 1px solid #4F6EF7; }
            QLineEdit:hover, QTextEdit:hover { border: 1px solid #B4B0AA; }
        """)
        err.setVisible(False)

    def _on_save(self):
        self._clear_error(self._name_field, self._name_err)
        self._clear_error(self._phone_field, self._phone_err)
        self._clear_error(self._address_field, self._address_err)

        valid = True
        name = self._name_field.text().strip()
        if not name:
            self._show_error(self._name_field, self._name_err, "Nama supplier tidak boleh kosong.")
            valid = False

        if not valid:
            return

        phone   = self._phone_field.text().strip() or None
        address = self._address_field.toPlainText().strip() or None

        payload = {"name": name, "phone": phone, "address": address}
        if self._is_edit:
            payload["id"] = self._supplier.id
        self.saved.emit(payload)
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
# Delete Supplier Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class DeleteSupplierDialog(QDialog):
    confirmed = pyqtSignal()

    def __init__(self, supplier: Supplier, parent=None):
        super().__init__(parent)
        self._supplier = supplier
        self.setWindowTitle("Hapus Supplier")
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
        cl.addSpacing(10)

        title = QLabel("Hapus Supplier?")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)
        cl.addSpacing(6)

        subtitle = QLabel(
            f"Kamu akan menghapus supplier <b>{self._supplier.name}</b>.<br>"
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

        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{ background: {C_WHITE}; border: 1px solid #E4E6EE; border-radius: 10px; }}
            QLabel {{ background: transparent; border: none; }}
        """)
        info_lay = QHBoxLayout(info_card)
        info_lay.setContentsMargins(14, 12, 14, 12)
        info_lay.setSpacing(12)

        icon_lbl = QLabel("🏭")
        icon_lbl.setFixedSize(36, 36)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size:18px;background:#EEF1FE;border-radius:8px;")

        detail = QVBoxLayout()
        detail.setSpacing(2)
        name_lbl = QLabel(self._supplier.name)
        name_lbl.setStyleSheet(f"font-size:13px;font-weight:600;color:{C_TEXT_PRI};")
        phone_lbl = QLabel(self._supplier.phone or "Telepon tidak tersedia")
        phone_lbl.setStyleSheet(f"font-size:11px;color:{C_TEXT_SEC};")
        detail.addWidget(name_lbl)
        detail.addWidget(phone_lbl)

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

        delete_btn = QPushButton("Ya, Hapus Supplier")
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
# Supplier Page
# ═══════════════════════════════════════════════════════════════════════════════
class SupplierPage(QWidget):
    def __init__(self, user: dict = None, parent=None):
        super().__init__(parent)
        self._user             = user or {}
        self._suppliers        = self._load_suppliers()
        self._search_query     = ""
        self._view_mode        = ViewToggle.VIEW_TABLE
        self._grid_initialized = False
        self._pending_refresh  = False
        self._render_token     = 0
        self._stat_value_labels: dict[str, tuple] = {}

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C_BG};")
        self._build_ui()

    def _load_suppliers(self) -> list[Supplier]:
        return SupplierController.fetch()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 17, 32, 28)
        layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Manajemen Supplier")
        page_title.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 27px; font-weight: 700;
            color: {C_TEXT_PRI}; background: transparent;
        """)

        page_sub = QLabel("Kelola semua supplier warungmu di sini")
        page_sub.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 13px;
            color: {C_TEXT_SEC}; background: transparent;
        """)

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        add_btn = QPushButton("+ Tambah Supplier")
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

        # ── Search bar + view toggle ──────────────────────────────────────────
        filter_and_toggle = QHBoxLayout()
        filter_and_toggle.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("🔍  Cari supplier...")
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

        self._view_toggle = ViewToggle(initial=ViewToggle.VIEW_TABLE)
        self._view_toggle.toggled.connect(self._on_view_mode_changed)

        filter_and_toggle.addWidget(search, stretch=1)
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
        self._grid_layout.setColumnStretch(0, 1)
        self._grid_layout.setColumnStretch(1, 1)
        self._grid_layout.setColumnStretch(2, 1)
        self._grid_layout.setColumnStretch(3, 1)
        self._grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self._scroll.setWidget(self._grid_container)
        card_layout.addWidget(self._scroll)

        # Page 1: Table
        self._table_page = QWidget()
        self._table_page.setStyleSheet("background: transparent;")
        table_layout = QVBoxLayout(self._table_page)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self._table_view = SupplierTableView()
        self._table_view.edit_clicked.connect(self._open_edit_dialog)
        self._table_view.delete_clicked.connect(self._delete_supplier)
        table_layout.addWidget(self._table_view)

        self._content_stack.addWidget(self._card_page)   # index 0
        self._content_stack.addWidget(self._table_page)  # index 1
        self._content_stack.setCurrentIndex(1)

        layout.addWidget(self._content_stack, stretch=1)

    # ── Stats ──────────────────────────────────────────────────────────────────
    def _calc_stats(self) -> dict:
        total = len(self._suppliers)
        with_phone   = sum(1 for s in self._suppliers if s.phone)
        with_address = sum(1 for s in self._suppliers if s.address)
        return {
            "total":        str(total),
            "with_phone":   str(with_phone),
            "with_address": str(with_address),
        }

    def _build_stats_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(14)
        values = self._calc_stats()
        stats = [
            ("total",        "Total Supplier",    values["total"],        "#4F6EF7", "#EEF1FE"),
            ("with_phone",   "Ada Telepon",        values["with_phone"],   "#27AE60", "#E8F8F0"),
            ("with_address", "Ada Alamat",         values["with_address"], "#E08C52", "#FEF3EA"),
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
    def _filtered_suppliers(self) -> list[Supplier]:
        result = self._suppliers
        if self._search_query:
            q = self._search_query.lower()
            result = [s for s in result if q in s.name.lower()
                      or (s.phone and q in s.phone.lower())
                      or (s.address and q in s.address.lower())]
        return result

    # ── Refresh ────────────────────────────────────────────────────────────────
    def _refresh_view(self):
        if self._view_mode == ViewToggle.VIEW_CARD:
            self._refresh_grid()
        else:
            self._refresh_table()

    def _refresh_table(self):
        self._table_view.populate(self._filtered_suppliers())

    def _refresh_grid(self):
        self._render_token += 1
        token = self._render_token

        if not self.isVisible():
            self._pending_refresh = True
            return

        self._pending_refresh = False
        self._clear_grid()
        suppliers = self._filtered_suppliers()

        if not suppliers:
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

            icon = QLabel("🏭")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setStyleSheet("font-size: 46px;")

            title = QLabel("Tidak ada supplier ditemukan")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet(f"""
                font-family: 'Segoe UI'; font-size: 16px;
                font-weight: 700; color: {C_TEXT_PRI};
            """)

            subtitle = QLabel("Coba ubah kata kunci pencarian,\natau tambahkan supplier baru.")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle.setStyleSheet(f"""
                font-family: 'Segoe UI'; font-size: 12px; color: {C_TEXT_SEC};
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

        for i, supplier in enumerate(suppliers):
            if token != self._render_token:
                return
            card = SupplierCard(supplier)
            card.edit_clicked.connect(self._open_edit_dialog)
            card.delete_clicked.connect(self._delete_supplier)
            self._grid_layout.addWidget(card, i // 4, i % 4)

        MIN_CARD_W = 180
        self._grid_container.setMinimumWidth(5 * MIN_CARD_W + 4 * self._grid_layout.spacing())
        self._grid_container.adjustSize()
        self._grid_container.update()
        self._scroll.viewport().update()

    def _get_column_count(self) -> int:
        return 4

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
        dlg = SupplierDialog(parent=self)
        dlg.saved.connect(self._add_supplier)
        dlg.exec()

    def _open_edit_dialog(self, supplier: Supplier):
        dlg = SupplierDialog(parent=self, supplier=supplier)
        dlg.saved.connect(self._edit_supplier)
        dlg.exec()

    def _edit_supplier(self, data: dict):
        try:
            SupplierController.edit(
                supplier_id=data["id"],
                name=data["name"],
                phone=data["phone"],
                address=data["address"],
            )
            self._suppliers = self._load_suppliers()
            self._refresh_stats()
            self._refresh_view()
            Toast.show_toast(f"Supplier <b>{data['name']}</b> berhasil diperbarui.", "success", self)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _add_supplier(self, data: dict):
        try:
            SupplierController.add(
                name=data["name"],
                phone=data["phone"],
                address=data["address"],
            )
            self._suppliers = self._load_suppliers()
            self._refresh_stats()
            self._refresh_view()
            Toast.show_toast(f"Supplier <b>{data['name']}</b> berhasil ditambahkan.", "success", self)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _delete_supplier(self, supplier: Supplier):
        def do_delete():
            try:
                SupplierController.remove(supplier.id)
                self._suppliers = self._load_suppliers()
                self._refresh_stats()
                self._refresh_view()
                Toast.show_toast(f"Supplier <b>{supplier.name}</b> berhasil dihapus.", "success", self)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

        dlg = DeleteSupplierDialog(supplier=supplier, parent=self)
        dlg.confirmed.connect(do_delete)
        dlg.exec()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._grid_initialized or self._pending_refresh:
            self._grid_initialized = True
            self._pending_refresh  = False
            QTimer.singleShot(0, self._refresh_view)