from __future__ import annotations

from controllers.receivables import ReceivablesController, Receivables
from controllers.customer import CustomerController
from gui.views.components import Avatar

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
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QSizePolicy,
    QDateEdit,
    QDoubleSpinBox,
    QScrollArea,
    QStackedWidget,
    QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDate
from PyQt6.QtGui import QColor, QPainterPath, QRegion, QFont

from gui.views.components.toast import Toast

# ── Color palette ──────────────────────────────────────────────────────────────
C_BG        = "#F4F5F9"
C_WHITE     = "#FFFFFF"
C_ACCENT    = "#4F6EF7"
C_ACCENT_H  = "#3A57E8"
C_TEXT_PRI  = "#1A1D2E"
C_TEXT_SEC  = "#6B6F80"
C_BORDER    = "#E4E6EE"
C_DANGER    = "#E05252"
C_TAG_BG    = "#EEF1FE"
C_SUCCESS   = "#27AE60"
C_WARNING   = "#F39C12"

RADIUS = 14

# ── Status config ──────────────────────────────────────────────────────────────
STATUS_CONFIG = {
    "unpaid":  {"label": "🔴 Belum Lunas", "bg": "#FDEAEA", "text": "#C0392B", "dot": "#E05252"},
    "partial": {"label": "🟡 Sebagian",    "bg": "#FEF3E2", "text": "#A04000", "dot": "#F39C12"},
    "paid":    {"label": "🟢 Lunas",       "bg": "#E8F8F0", "text": "#1D6A40", "dot": "#27AE60"},
}

FILTER_STATUS = ["Semua", "🔴 Belum Lunas", "🟡 Sebagian", "🟢 Lunas"]

C_ROW_ALT    = "#FAFBFF"
C_HEADER_BG  = "#FFFFFF"
C_HEADER_TEXT = "#9EA3B8"
C_DIVIDER    = "#F0F1F7"


# ── Helpers ────────────────────────────────────────────────────────────────────
def _fmt_currency(amount: float) -> str:
    return f"Rp {amount:,.0f}".replace(",", ".")

def _status_cfg(status: str) -> dict:
    return STATUS_CONFIG.get(status, STATUS_CONFIG["unpaid"])

def _resolve_status(amount_paid: float, total_amount: float) -> str:
    if amount_paid <= 0:
        return "unpaid"
    if amount_paid >= total_amount:
        return "paid"
    return "partial"

def _customer_name(customer_id: int | None, customer_map: dict) -> str:
    if customer_id is None:
        return "—"
    return customer_map.get(customer_id, f"ID #{customer_id}")

def _due_date_display(due_date: str | None) -> str:
    if not due_date:
        return "—"
    return due_date


# ═══════════════════════════════════════════════════════════════════════════════
# Customer Detail Dialog — rincian semua transaksi piutang satu pelanggan
# ═══════════════════════════════════════════════════════════════════════════════
class CustomerDetailDialog(QDialog):
    """Menampilkan semua transaksi piutang milik satu pelanggan."""

    pay_clicked    = pyqtSignal(object)   # emits Receivables
    delete_clicked = pyqtSignal(object)   # emits Receivables

    def __init__(self, customer_name: str, records: list[Receivables], parent=None):
        super().__init__(parent)
        self._name    = customer_name
        self._records = records
        self.setWindowTitle(f"Detail Piutang — {customer_name}")
        self.setModal(True)
        self.setFixedWidth(640)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setSizeGripEnabled(False)
        self.setStyleSheet(f"QDialog {{ background: {C_WHITE}; font-family: 'Segoe UI'; }}")
        self._build_ui()
        self.adjustSize()
        self.setMaximumHeight(620)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──
        header = QFrame()
        header.setStyleSheet(f"QFrame {{ background: #FAFAF8; border-bottom: 1px solid #DDD9D2; }}")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(28, 18, 28, 18)
        hl.setSpacing(12)

        logo = QLabel("Warung<span style='color:#4F6EF7'>+</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("font-size:13px;color:#5F5E5A;font-weight:500;letter-spacing:1px;border:none;background:transparent;")

        title = QLabel(f"Rincian Piutang  ·  {self._name}")
        title.setStyleSheet(f"font-size:16px;font-weight:700;color:{C_TEXT_PRI};border:none;background:transparent;")

        total_remaining = sum(r.total_amount - r.amount_paid for r in self._records)
        total_lbl = QLabel(_fmt_currency(total_remaining))
        total_lbl.setStyleSheet(f"font-size:14px;font-weight:700;color:{C_DANGER};border:none;background:transparent;")

        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(logo)
        col.addWidget(title)

        hl.addLayout(col)
        hl.addStretch()

        right = QVBoxLayout()
        right.setSpacing(2)
        right.setAlignment(Qt.AlignmentFlag.AlignRight)
        sub = QLabel("Total Sisa")
        sub.setStyleSheet(f"font-size:10px;color:{C_TEXT_SEC};border:none;background:transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(sub)
        right.addWidget(total_lbl)
        hl.addLayout(right)
        root.addWidget(header)

        # ── Scroll area with transaction cards ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        container.setStyleSheet(f"background: {C_BG};")
        vlay = QVBoxLayout(container)
        vlay.setContentsMargins(20, 16, 20, 16)
        vlay.setSpacing(10)

        for i, rec in enumerate(self._records):
            card = self._make_transaction_card(i + 1, rec)
            vlay.addWidget(card)

        vlay.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll)

        # ── Footer ──
        footer = QFrame()
        footer.setStyleSheet("QFrame { background: #FAFAF8; border-top: 1px solid #DDD9D2; }")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(28, 14, 28, 14)

        close_btn = QPushButton("Tutup")
        close_btn.setFixedHeight(38)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #5F5E5A;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 500;
                border-radius: 10px; border: 1px solid #DDD9D2; padding: 0 20px;
            }
            QPushButton:hover { background: #F1EFE8; border: 1px solid #C8C6BF; }
        """)
        close_btn.clicked.connect(self.reject)
        fl.addStretch()
        fl.addWidget(close_btn)
        root.addWidget(footer)

    def _make_transaction_card(self, index: int, rec: Receivables) -> QFrame:
        status    = _resolve_status(rec.amount_paid, rec.total_amount)
        cfg       = _status_cfg(status)
        remaining = rec.total_amount - rec.amount_paid

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 10px;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        # ── Top row: nomor + status + tombol ──
        top = QHBoxLayout()
        top.setSpacing(8)

        num_lbl = QLabel(f"Transaksi #{index}")
        num_lbl.setStyleSheet(f"font-size:12px;font-weight:600;color:{C_TEXT_PRI};")

        badge = QLabel(cfg["label"])
        badge.setStyleSheet(f"""
            background: {cfg['bg']}; color: {cfg['text']};
            font-size: 10px; font-weight: 700;
            padding: 3px 8px; border-radius: 5px;
        """)

        top.addWidget(num_lbl)
        top.addWidget(badge)
        top.addStretch()

        if status != "paid":
            pay_btn = QPushButton("Bayar")
            pay_btn.setFixedSize(62, 26)
            pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            pay_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #E8F8F0; color: {C_SUCCESS};
                    font-size: 11px; font-weight: 600;
                    border-radius: 6px; border: none;
                }}
                QPushButton:hover {{ background: {C_SUCCESS}; color: #FFFFFF; }}
            """)
            pay_btn.clicked.connect(lambda _=False, r=rec: self.pay_clicked.emit(r))
            top.addWidget(pay_btn)

        del_btn = QPushButton("Hapus")
        del_btn.setFixedSize(62, 26)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: #FDEAEA; color: {C_DANGER};
                font-size: 11px; font-weight: 600;
                border-radius: 6px; border: none;
            }}
            QPushButton:hover {{ background: {C_DANGER}; color: #FFFFFF; }}
        """)
        del_btn.clicked.connect(lambda _=False, r=rec: self.delete_clicked.emit(r))
        top.addWidget(del_btn)
        lay.addLayout(top)

        # ── Divider ──
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
        lay.addWidget(div)

        # ── Amount grid ──
        grid = QHBoxLayout()
        grid.setSpacing(0)

        for label, value, color in [
            ("Total Piutang", _fmt_currency(rec.total_amount), C_TEXT_PRI),
            ("Terbayar",     _fmt_currency(rec.amount_paid),  C_TEXT_SEC),
            ("Sisa",         _fmt_currency(remaining),        C_DANGER if remaining > 0 and status != "paid" else C_SUCCESS),
        ]:
            col = QVBoxLayout()
            col.setSpacing(3)
            l = QLabel(label)
            l.setStyleSheet(f"font-size:10px;color:{C_TEXT_SEC};")
            v = QLabel(value)
            v.setStyleSheet(f"font-size:13px;font-weight:700;color:{color};")
            col.addWidget(l)
            col.addWidget(v)
            grid.addLayout(col)
            if label != "Sisa":
                grid.addStretch()

        lay.addLayout(grid)

        # ── Due date ──
        if rec.due_date:
            today = QDate.currentDate()
            try:
                d = QDate.fromString(rec.due_date, "yyyy-MM-dd")
                overdue = d.isValid() and d < today and status != "paid"
            except Exception:
                overdue = False
            color = C_DANGER if overdue else C_TEXT_SEC
            prefix = "⚠ Lewat jatuh tempo: " if overdue else "Jatuh tempo: "
            due_lbl = QLabel(f"{prefix}{rec.due_date}")
            due_lbl.setStyleSheet(f"font-size:11px;color:{color};")
            lay.addWidget(due_lbl)

        return card


# ═══════════════════════════════════════════════════════════════════════════════
# Delete All Receivables Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class DeleteAllReceivablesDialog(QDialog):
    confirmed = pyqtSignal()

    def __init__(self, records: list[Receivables], customer_name: str, parent=None):
        super().__init__(parent)
        self._records = records
        self._name    = customer_name
        self.setWindowTitle("Hapus Semua Piutang")
        self.setModal(True)
        self.setFixedWidth(400)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setSizeGripEnabled(False)
        self.setStyleSheet(f"QDialog {{ background: {C_WHITE}; font-family: 'Segoe UI'; }}")
        self._build_ui()
        self.adjustSize()
        self.setMaximumSize(400, self.height())

    def _build_ui(self):
        total = sum(r.total_amount for r in self._records)

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
        cl.addSpacing(14)

        title = QLabel("Hapus Semua Piutang?")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)
        cl.addSpacing(4)

        sub = QLabel(
            f"Semua <b>{len(self._records)} transaksi piutang</b> atas nama "
            f"<b>{self._name}</b> dengan total <b>{_fmt_currency(total)}</b> "
            f"akan dihapus permanen. Tindakan ini tidak dapat dibatalkan."
        )
        sub.setTextFormat(Qt.TextFormat.RichText)
        sub.setWordWrap(True)
        sub.setStyleSheet("font-size:12px;color:#888780;border:none;")
        cl.addWidget(sub)
        cl.addSpacing(20)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider)
        cl.addSpacing(18)

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

        del_btn = QPushButton("Ya, Hapus Semua")
        del_btn.setFixedHeight(40)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_DANGER}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 600;
                border-radius: 10px; border: none;
            }}
            QPushButton:hover {{ background: #C94040; }}
        """)
        del_btn.clicked.connect(lambda: (self.confirmed.emit(), self.accept()))

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(del_btn)
        cl.addLayout(btn_row)
        root.addWidget(card)


# ═══════════════════════════════════════════════════════════════════════════════
# Receivable Card (Card View)
# ═══════════════════════════════════════════════════════════════════════════════
class ReceivableCard(QFrame):
    """Satu kartu piutang pelanggan untuk tampilan grid/card view."""

    CARD_WIDTH = 290

    pay_clicked        = pyqtSignal(object)       # emits Receivables (agg)
    delete_clicked     = pyqtSignal(object)       # emits Receivables (agg)
    detail_clicked     = pyqtSignal(str, list)    # emits (customer_name, [Receivables])
    delete_all_clicked = pyqtSignal(str, list)    # emits (customer_name, [Receivables])

    def __init__(
        self,
        agg_rec: Receivables,
        cust_name: str,
        phone: str,
        all_for_cust: list[Receivables],
        parent=None,
    ):
        super().__init__(parent)
        self._agg_rec      = agg_rec
        self._cust_name    = cust_name
        self._phone        = phone
        self._all_for_cust = all_for_cust
        self._build()

    def _build(self):
        agg       = self._agg_rec
        status    = _resolve_status(agg.amount_paid, agg.total_amount)
        cfg       = _status_cfg(status)
        remaining = agg.total_amount - agg.amount_paid
        multi     = len(self._all_for_cust) > 1

        # Border warna sesuai status
        border_color = cfg["dot"]
        top_accent   = cfg["bg"]

        self.setObjectName("ReceivableCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame#ReceivableCard {{
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
                border-top-left-radius:  13px;
                border-top-right-radius: 13px;
                border-bottom: 1px solid {border_color};
                border-left: none; border-right: none; border-top: none;
            }}
        """)
        strip_lay = QHBoxLayout(top_strip)
        strip_lay.setContentsMargins(14, 0, 14, 0)
        strip_lay.setSpacing(6)

        # Avatar inisial
        parts = self._cust_name.strip().split()
        initials = (
            (parts[0][0] + parts[1][0]).upper()
            if len(parts) >= 2
            else self._cust_name[:2].upper() if self._cust_name else "?"
        )
        palettes = [
            ("#EEF0FD", "#3B52C4"),
            ("#FDF0EC", "#B04A28"),
            ("#E6F1FB", "#185FA5"),
            ("#EAF3DE", "#3B6D11"),
        ]
        idx = (ord(initials[0]) - ord("A")) % len(palettes)
        av_bg, av_fg = palettes[idx]

        avatar = Avatar(initials, bg_color=av_bg, text_color=av_fg, size=24)
        strip_lay.addWidget(avatar)

        name_lbl = QLabel(self._cust_name)
        name_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 12px; font-weight: 700;
            color: {C_TEXT_PRI}; background: transparent; border: none;
        """)
        strip_lay.addWidget(name_lbl)
        strip_lay.addStretch()

        # Status badge di kanan strip
        status_badge = QLabel(cfg["label"])
        status_badge.setStyleSheet(f"""
            background: transparent; color: {cfg['text']};
            font-family: 'Segoe UI'; font-size: 9px; font-weight: 700;
            border: none;
        """)
        strip_lay.addWidget(status_badge)

        root.addWidget(top_strip)

        # ── Body ──────────────────────────────────────────────────────────────
        body = QVBoxLayout()
        body.setContentsMargins(14, 10, 14, 10)
        body.setSpacing(8)

        # Nomor telepon + badge multi transaksi
        info_row = QHBoxLayout()
        info_row.setSpacing(6)
        phone_lbl = QLabel(f"📞  {self._phone}" if self._phone else "📞  —")
        phone_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 11px;
            color: {C_TEXT_SEC}; background: transparent; border: none;
        """)
        info_row.addWidget(phone_lbl)
        info_row.addStretch()

        if multi:
            multi_badge = QLabel(f"🔴 {len(self._all_for_cust)} Transaksi")
            multi_badge.setStyleSheet(f"""
                background: #FDEAEA; color: {C_DANGER};
                font-family: 'Segoe UI'; font-size: 10px; font-weight: 700;
                padding: 3px 8px; border-radius: 5px; border: none;
            """)
            info_row.addWidget(multi_badge)
        body.addLayout(info_row)

        # Divider
        div1 = QFrame()
        div1.setFixedHeight(1)
        div1.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
        body.addWidget(div1)

        # Amount columns: Total · Terbayar · Sisa
        amt_row = QHBoxLayout()
        amt_row.setSpacing(0)

        def _amt_col(label: str, value: str, color: str):
            col = QVBoxLayout()
            col.setSpacing(2)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:9px;color:{C_TEXT_SEC};background:transparent;border:none;")
            val = QLabel(value)
            val.setStyleSheet(f"font-family:'Segoe UI';font-size:12px;font-weight:700;color:{color};background:transparent;border:none;")
            col.addWidget(lbl)
            col.addWidget(val)
            return col

        remain_color = C_DANGER if remaining > 0 and status != "paid" else C_SUCCESS

        amt_row.addLayout(_amt_col("Total Piutang", _fmt_currency(agg.total_amount), C_TEXT_PRI))
        amt_row.addStretch()

        sep1 = QFrame()
        sep1.setFixedWidth(1)
        sep1.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
        amt_row.addWidget(sep1)
        amt_row.addSpacing(10)

        amt_row.addLayout(_amt_col("Terbayar", _fmt_currency(agg.amount_paid), C_TEXT_SEC))
        amt_row.addStretch()

        sep2 = QFrame()
        sep2.setFixedWidth(1)
        sep2.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
        amt_row.addWidget(sep2)
        amt_row.addSpacing(10)

        amt_row.addLayout(_amt_col("Sisa", _fmt_currency(remaining), remain_color))

        body.addLayout(amt_row)

        # Due date (jika ada)
        if agg.due_date:
            today = QDate.currentDate()
            try:
                d = QDate.fromString(agg.due_date, "yyyy-MM-dd")
                overdue = d.isValid() and d < today and status != "paid"
            except Exception:
                overdue = False
            due_color  = C_DANGER if overdue else C_TEXT_SEC
            due_prefix = "⚠  " if overdue else "📅  "
            due_lbl = QLabel(f"{due_prefix}Jatuh tempo: {agg.due_date}")
            due_lbl.setStyleSheet(f"""
                font-family: 'Segoe UI'; font-size: 10px;
                color: {due_color}; background: transparent; border: none;
            """)
            body.addWidget(due_lbl)

        root.addLayout(body)

        # ── Footer: action buttons ────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background: #F7F8FC;
                border-bottom-left-radius:  13px;
                border-bottom-right-radius: 13px;
                border-top: 1px solid {C_DIVIDER};
                border-left: none; border-right: none; border-bottom: none;
            }}
        """)
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(14, 7, 14, 7)
        footer_lay.setSpacing(6)
        footer_lay.addStretch()

        if multi:
            detail_btn = QPushButton("Detail")
            detail_btn.setFixedSize(68, 26)
            detail_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            detail_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C_TAG_BG}; color: {C_ACCENT};
                    font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                    border-radius: 7px; border: none;
                }}
                QPushButton:hover {{ background: {C_ACCENT}; color: #FFFFFF; }}
            """)
            detail_btn.clicked.connect(
                lambda _=False, n=self._cust_name, rs=self._all_for_cust:
                    self.detail_clicked.emit(n, rs)
            )
            footer_lay.addWidget(detail_btn)

            del_all_btn = QPushButton("Hapus")
            del_all_btn.setFixedSize(68, 26)
            del_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_all_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #FDEAEA; color: {C_DANGER};
                    font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                    border-radius: 7px; border: none;
                }}
                QPushButton:hover {{ background: {C_DANGER}; color: #FFFFFF; }}
            """)
            del_all_btn.clicked.connect(
                lambda _=False, n=self._cust_name, rs=self._all_for_cust:
                    self.delete_all_clicked.emit(n, rs)
            )
            footer_lay.addWidget(del_all_btn)

        else:
            actual_rec = self._all_for_cust[0] if self._all_for_cust else self._agg_rec

            if status != "paid":
                pay_btn = QPushButton("Bayar")
                pay_btn.setFixedSize(68, 26)
                pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                pay_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: #E8F8F0; color: {C_SUCCESS};
                        font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                        border-radius: 7px; border: none;
                    }}
                    QPushButton:hover {{ background: {C_SUCCESS}; color: #FFFFFF; }}
                """)
                pay_btn.clicked.connect(lambda _=False, r=actual_rec: self.pay_clicked.emit(r))
                footer_lay.addWidget(pay_btn)

            del_btn = QPushButton("Hapus")
            del_btn.setFixedSize(68, 26)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #FDEAEA; color: {C_DANGER};
                    font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                    border-radius: 7px; border: none;
                }}
                QPushButton:hover {{ background: {C_DANGER}; color: #FFFFFF; }}
            """)
            del_btn.clicked.connect(lambda _=False, r=actual_rec: self.delete_clicked.emit(r))
            footer_lay.addWidget(del_btn)

        root.addWidget(footer)

        # Tinggi dinamis
        base_h = 36 + 10 + 22 + 1 + 10 + 38 + 1 + 10 + 40
        extra  = 20 if agg.due_date else 0
        self.setFixedHeight(base_h + extra)


# ═══════════════════════════════════════════════════════════════════════════════
# View Toggle
# ═══════════════════════════════════════════════════════════════════════════════
class ReceivablesViewToggle(QWidget):
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
# Receivables Table View
# ═══════════════════════════════════════════════════════════════════════════════
class ReceivablesTableView(QTableWidget):
    pay_clicked        = pyqtSignal(object)       # emits Receivables
    delete_clicked     = pyqtSignal(object)       # emits Receivables
    detail_clicked     = pyqtSignal(str, list)    # emits (customer_name, [Receivables])
    delete_all_clicked = pyqtSignal(str, list)    # emits (customer_name, [Receivables])

    COLUMNS    = ["      #", "Pelanggan", "Total Piutang", "Terbayar", "Sisa", "Status", "Aksi"]
    COL_NO     = 0
    COL_CUST   = 1
    COL_TOTAL  = 2
    COL_PAID   = 3
    COL_REMAIN = 4
    COL_STATUS = 5
    COL_ACTION = 6
    ROW_H = 52

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
        self._adjust_columns()
        QTimer.singleShot(0, self._apply_viewport_clip)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._apply_viewport_clip)

    MIN_NAME_WIDTH = 300
   
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

        header.setSectionResizeMode(self.COL_NO,     QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_CUST,   QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COL_TOTAL,  QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_PAID,   QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_REMAIN, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_STATUS, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(self.COL_ACTION, QHeaderView.ResizeMode.Fixed)

        self.setColumnWidth(self.COL_NO,     44)
        self.setColumnWidth(self.COL_TOTAL,  130)
        self.setColumnWidth(self.COL_PAID,   130)
        self.setColumnWidth(self.COL_REMAIN, 130)
        self.setColumnWidth(self.COL_STATUS, 170)
        self.setColumnWidth(self.COL_ACTION, 210)
        
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

    def _adjust_columns(self):
        header = self.horizontalHeader()

        fixed_widths = (
            self.columnWidth(self.COL_NO) +
            self.columnWidth(self.COL_TOTAL) +
            self.columnWidth(self.COL_PAID) +
            self.columnWidth(self.COL_REMAIN) +
            self.columnWidth(self.COL_STATUS) +
            self.columnWidth(self.COL_ACTION)
        )

        available = self.viewport().width()
        name_width = available - fixed_widths

        if name_width >= self.MIN_NAME_WIDTH:
            header.setSectionResizeMode(self.COL_CUST, QHeaderView.ResizeMode.Stretch)
        else:
            header.setSectionResizeMode(self.COL_CUST, QHeaderView.ResizeMode.Fixed)
            self.setColumnWidth(self.COL_CUST, self.MIN_NAME_WIDTH)

    def _show_empty_state(self):
        self.clearContents()
        self.setRowCount(1)
        self.setSpan(0, 0, 1, self.columnCount())
        self.setRowHeight(0, 260)
        self.setShowGrid(False)

        for col in range(self.columnCount()):
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setBackground(QColor(C_WHITE))
            item.setData(Qt.ItemDataRole.DisplayRole, "")
            self.setItem(0, col, item)

        empty = QWidget()
        empty.setObjectName("EmptyState")
        empty.setStyleSheet(f"QWidget#EmptyState {{ background: {C_WHITE}; border: none; }} QLabel {{ background: transparent; border: none; }}")
        lay = QVBoxLayout(empty)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(8)
        lay.addStretch()

        icon = QLabel("💳")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 46px;")
        title = QLabel("Tidak ada data piutang")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-family:'Segoe UI';font-size:16px;font-weight:700;color:{C_TEXT_PRI};")
        sub = QLabel("Coba ubah filter atau kata kunci pencarian.")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"font-family:'Segoe UI';font-size:12px;color:{C_TEXT_SEC};")

        lay.addWidget(icon)
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addStretch()
        self.setCellWidget(0, 0, empty)

    def populate(self, rows: list[tuple], customer_map: dict, all_receivables: list[Receivables]):
        self._all_receivables = all_receivables
        self.clearContents()
        self.setRowCount(0)

        if not rows:
            self._show_empty_state()
            return

        self.setShowGrid(True)

        for i, (agg_rec, cust_name, all_for_cust) in enumerate(rows):
            row = self.rowCount()
            self.insertRow(row)
            self.setRowHeight(row, self.ROW_H)

            row_bg = C_ROW_ALT if row % 2 == 1 else C_WHITE
            for col in range(len(self.COLUMNS)):
                ph = QTableWidgetItem()
                ph.setBackground(QColor(row_bg))
                ph.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.setItem(row, col, ph)

            remaining = agg_rec.total_amount - agg_rec.amount_paid
            status    = _resolve_status(agg_rec.amount_paid, agg_rec.total_amount)
            multi     = len(all_for_cust) > 1

            self.setCellWidget(row, self.COL_NO,     self._make_no_cell(i + 1))
            customer = customer_map.get(agg_rec.customer_id)

            cust_name = customer.name if customer else "Unknown"
            phone = customer.phone if customer else ""

            self.setCellWidget(
                row,
                self.COL_CUST,
                self._make_customer_cell(
                    cust_name,
                    phone,
                    len(all_for_cust) if multi else 0
                )
            )
            self.setCellWidget(row, self.COL_TOTAL,  self._make_currency_cell(_fmt_currency(agg_rec.total_amount)))
            self.setCellWidget(row, self.COL_PAID,   self._make_currency_cell(_fmt_currency(agg_rec.amount_paid), muted=True))
            self.setCellWidget(row, self.COL_REMAIN, self._make_currency_cell(
                _fmt_currency(remaining), bold=True,
                danger=remaining > 0 and status != "paid"
            ))
            self.setCellWidget(row, self.COL_STATUS, self._make_status_badge(status))
            self.setCellWidget(row, self.COL_ACTION, self._make_action_buttons(
                agg_rec, status, cust_name, all_for_cust if multi else []
            ))

        QTimer.singleShot(0, self._apply_viewport_clip)

    # ── Cell builders ──────────────────────────────────────────────────────────
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

    def _make_customer_cell(self, text: str, phone: str = "", has_multiple: int = 0) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")

        lay = QHBoxLayout(w)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        parts = text.strip().split()
        if len(parts) >= 2:
            initials = parts[0][0].upper() + parts[1][0].upper()
        else:
            initials = text[:2].upper() if text else "?"

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

        text_wrap = QWidget()
        text_wrap.setStyleSheet("background: transparent; border: none;")

        text_lay = QVBoxLayout(text_wrap)
        text_lay.setContentsMargins(0, 0, 0, 0)
        text_lay.setSpacing(1)

        name_lbl = QLabel(text)
        name_lbl.setStyleSheet(f"""
            font-family:'Segoe UI';
            font-size:13px;
            color:{C_TEXT_PRI};
            background:transparent;
            font-weight:600;
        """)

        phone_lbl = QLabel(phone if phone else "-")
        phone_lbl.setStyleSheet(f"""
            font-family:'Segoe UI';
            font-size:11px;
            color:{C_TEXT_SEC};
            background:transparent;
        """)

        text_lay.addWidget(name_lbl)
        text_lay.addWidget(phone_lbl)

        lay.addWidget(text_wrap)

        if has_multiple:
            badge_wrap = QWidget()
            badge_wrap.setStyleSheet("background: transparent; border: none;")

            badge_lay = QHBoxLayout(badge_wrap)
            badge_lay.setContentsMargins(0, 0, 0, 0)
            badge_lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            badge = QLabel(f"🔴 {has_multiple} Transaksi")
            badge.setStyleSheet(f"""
                background: #FDEAEA;
                color: {C_DANGER};

                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: 700;

                padding: 4px 10px;
                border-radius: 6px;
                border: none;
            """)

            badge_lay.addWidget(badge)
            lay.addWidget(badge_wrap)

        lay.addStretch()

        return w

    def _make_text_cell(self, text: str, muted: bool = False) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        color = C_TEXT_SEC if muted else C_TEXT_PRI
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:13px;color:{color};background:transparent;font-weight:{'400' if muted else '500'};")
        lay.addWidget(lbl)
        return w

    def _make_currency_cell(self, text: str, muted: bool = False, bold: bool = False, danger: bool = False) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        if danger:
            color = C_DANGER
        elif muted:
            color = C_TEXT_SEC
        else:
            color = C_TEXT_PRI
        weight = "700" if bold else "400"
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:13px;color:{color};background:transparent;font-weight:{weight};")
        lay.addWidget(lbl)
        return w

    def _make_status_badge(self, status: str) -> QWidget:
        cfg = _status_cfg(status)
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        badge = QLabel(cfg["label"])
        badge.setStyleSheet(f"""
            background: {cfg['bg']}; color: {cfg['text']};
            font-family: 'Segoe UI'; font-size: 11px; font-weight: 700;
            padding: 4px 10px; border-radius: 6px; border: none;
        """)
        lay.addWidget(badge)
        return w

    def _make_action_buttons(
        self,
        rec: Receivables,
        status: str,
        cust_name: str,
        all_for_cust: list[Receivables],
    ) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(8, 0, 8, 0)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        multi = len(all_for_cust) > 1

        if multi:
            detail_btn = QPushButton("Detail")
            detail_btn.setFixedSize(62, 28)
            detail_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            detail_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C_TAG_BG}; color: {C_ACCENT};
                    font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                    border-radius: 7px; border: none;
                }}
                QPushButton:hover {{ background: {C_ACCENT}; color: #FFFFFF; }}
            """)
            detail_btn.clicked.connect(
                lambda _=False, n=cust_name, rs=all_for_cust: self.detail_clicked.emit(n, rs)
            )
            lay.addWidget(detail_btn)

            del_all_btn = QPushButton("Hapus")
            del_all_btn.setFixedSize(62, 28)
            del_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_all_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #FDEAEA; color: {C_DANGER};
                    font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                    border-radius: 7px; border: none;
                }}
                QPushButton:hover {{ background: {C_DANGER}; color: #FFFFFF; }}
            """)
            del_all_btn.clicked.connect(
                lambda _=False, n=cust_name, rs=all_for_cust: self.delete_all_clicked.emit(n, rs)
            )
            lay.addWidget(del_all_btn)

        else:
            if status != "paid":
                pay_btn = QPushButton("Bayar")
                pay_btn.setFixedSize(62, 28)
                pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                pay_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: #E8F8F0; color: {C_SUCCESS};
                        font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                        border-radius: 7px; border: none;
                    }}
                    QPushButton:hover {{ background: {C_SUCCESS}; color: #FFFFFF; }}
                """)
                actual_rec = all_for_cust[0] if all_for_cust else rec
                pay_btn.clicked.connect(lambda _=False, r=actual_rec: self.pay_clicked.emit(r))
                lay.addWidget(pay_btn)

            del_btn = QPushButton("Hapus")
            del_btn.setFixedSize(62, 28)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #FDEAEA; color: {C_DANGER};
                    font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                    border-radius: 7px; border: none;
                }}
                QPushButton:hover {{ background: {C_DANGER}; color: #FFFFFF; }}
            """)
            actual_rec = all_for_cust[0] if all_for_cust else rec
            del_btn.clicked.connect(lambda _=False, r=actual_rec: self.delete_clicked.emit(r))
            lay.addWidget(del_btn)

        return w


# ═══════════════════════════════════════════════════════════════════════════════
# Pay Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class PayDialog(QDialog):
    paid = pyqtSignal(dict)   # {"id": int, "amount": float}

    def __init__(self, rec: Receivables, customer_name: str, parent=None):
        super().__init__(parent)
        self._rec  = rec
        self._name = customer_name
        self.setWindowTitle("Catat Pembayaran")
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
        rec       = self._rec
        remaining = rec.total_amount - rec.amount_paid

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
        cl.addSpacing(14)

        title = QLabel("Catat Pembayaran Piutang")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)
        cl.addSpacing(4)

        sub = QLabel(f"Pelanggan: <b>{self._name}</b>")
        sub.setTextFormat(Qt.TextFormat.RichText)
        sub.setStyleSheet("font-size:12px;color:#888780;border:none;")
        cl.addWidget(sub)
        cl.addSpacing(16)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider)
        cl.addSpacing(16)

        info = QFrame()
        info.setStyleSheet("QFrame { background:#F7F9FC; border: 1px solid #E4E6EE; border-radius: 10px; } QLabel { border:none; background:transparent; }")
        info_lay = QHBoxLayout(info)
        info_lay.setContentsMargins(16, 12, 16, 12)
        info_lay.setSpacing(0)

        for label, value in [("Total Piutang", _fmt_currency(rec.total_amount)),
                              ("Terbayar",     _fmt_currency(rec.amount_paid)),
                              ("Sisa",         _fmt_currency(remaining))]:
            col = QVBoxLayout()
            col.setSpacing(3)
            lbl = QLabel(label)
            lbl.setStyleSheet(f"font-size:11px;color:{C_TEXT_SEC};")
            val = QLabel(value)
            val.setStyleSheet(f"font-size:14px;font-weight:700;color:{'#E05252' if label == 'Sisa' else C_TEXT_PRI};")
            col.addWidget(lbl)
            col.addWidget(val)
            info_lay.addLayout(col)
            if label != "Sisa":
                info_lay.addStretch()

        cl.addWidget(info)
        cl.addSpacing(18)

        lbl_bayar = QLabel("Jumlah Pembayaran")
        lbl_bayar.setStyleSheet("font-size:12px;font-weight:500;color:#5F5E5A;border:none;")
        cl.addWidget(lbl_bayar)
        cl.addSpacing(5)

        self._amount_input = QDoubleSpinBox()
        self._amount_input.setRange(0.01, remaining)
        self._amount_input.setValue(remaining)
        self._amount_input.setDecimals(0)
        self._amount_input.setSingleStep(1000)
        self._amount_input.setFixedHeight(40)
        self._amount_input.setPrefix("Rp ")
        self._amount_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }
            QDoubleSpinBox:focus { border: 1px solid #4F6EF7; }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 0; }
        """)
        cl.addWidget(self._amount_input)
        cl.addSpacing(6)

        lunas_btn = QPushButton("Lunasi semua  (" + _fmt_currency(remaining) + ")")
        lunas_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        lunas_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C_ACCENT};
                font-family: 'Segoe UI'; font-size: 11px; font-weight: 600;
                border: none; text-align: left; padding: 0;
            }}
            QPushButton:hover {{ color: {C_ACCENT_H}; }}
        """)
        lunas_btn.clicked.connect(lambda: self._amount_input.setValue(remaining))
        cl.addWidget(lunas_btn)

        self._err_lbl = QLabel("")
        self._err_lbl.setStyleSheet(f"font-size:11px;color:{C_DANGER};font-family:'Segoe UI';border:none;")
        self._err_lbl.setVisible(False)
        cl.addWidget(self._err_lbl)
        cl.addSpacing(18)

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

        save_btn = QPushButton("Simpan Pembayaran")
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_SUCCESS}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 600;
                border-radius: 10px; border: none;
            }}
            QPushButton:hover {{ background: #1D9055; }}
        """)
        save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        cl.addLayout(btn_row)
        root.addWidget(card)

    def _on_save(self):
        amount    = self._amount_input.value()
        remaining = self._rec.total_amount - self._rec.amount_paid
        if amount <= 0:
            self._err_lbl.setText("Jumlah pembayaran harus lebih dari 0.")
            self._err_lbl.setVisible(True)
            return
        if amount > remaining + 0.01:
            self._err_lbl.setText("Jumlah melebihi sisa piutang.")
            self._err_lbl.setVisible(True)
            return
        self._err_lbl.setVisible(False)
        self.paid.emit({"id": self._rec.id, "amount": amount})
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
# Add Receivable Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class AddReceivableDialog(QDialog):
    saved = pyqtSignal(dict)

    def __init__(self, customers: list, parent=None):
        super().__init__(parent)
        self._customers = customers
        self.setWindowTitle("Tambah Piutang")
        self.setModal(True)
        self.setFixedWidth(440)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setSizeGripEnabled(False)
        self.setStyleSheet(f"QDialog {{ background: {C_WHITE}; font-family: 'Segoe UI'; }}")
        self._build_ui()
        self.adjustSize()
        self.setMaximumSize(440, self.height())

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size:12px;font-weight:500;color:#5F5E5A;border:none;")
        return lbl

    def _build_ui(self):
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
        cl.addSpacing(14)

        title = QLabel("Tambah Piutang Baru")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)
        cl.addSpacing(4)

        sub = QLabel("Isi detail piutang pelanggan.")
        sub.setStyleSheet("font-size:12px;color:#888780;border:none;")
        cl.addWidget(sub)
        cl.addSpacing(16)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider)
        cl.addSpacing(18)

        cl.addWidget(self._label("Pelanggan"))
        cl.addSpacing(5)
        self._customer_combo = QComboBox()
        self._customer_combo.setFixedHeight(40)
        self._customer_combo.addItem("— Tanpa Pelanggan —", None)
        for c in self._customers:
            self._customer_combo.addItem(c.name, c.id)
        self._customer_combo.setStyleSheet(f"""
            QComboBox {{
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }}
            QComboBox:focus {{ border: 1px solid #4F6EF7; }}
            QComboBox::drop-down {{ border: none; width: 0; }}
            QComboBox QAbstractItemView {{
                background: #FFFFFF; border: 1px solid #DDD9D2;
                color: #1b1b1b; font-size: 13px;
                selection-background-color: #EEF1FE; selection-color: #4F6EF7;
            }}
        """)
        cl.addWidget(self._customer_combo)
        cl.addSpacing(12)

        cl.addWidget(self._label("Total Piutang (Rp)"))
        cl.addSpacing(5)
        self._total_input = QDoubleSpinBox()
        self._total_input.setRange(1, 999_999_999)
        self._total_input.setValue(0)
        self._total_input.setDecimals(0)
        self._total_input.setSingleStep(1000)
        self._total_input.setFixedHeight(40)
        self._total_input.setPrefix("Rp ")
        self._total_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }
            QDoubleSpinBox:focus { border: 1px solid #4F6EF7; }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 0; }
        """)
        cl.addWidget(self._total_input)
        cl.addSpacing(12)

        cl.addWidget(self._label("Jatuh Tempo (opsional)"))
        cl.addSpacing(5)
        self._due_date = QDateEdit()
        self._due_date.setCalendarPopup(True)
        self._due_date.setDate(QDate.currentDate().addDays(7))
        self._due_date.setFixedHeight(40)
        self._due_date.setDisplayFormat("dd MMMM yyyy")
        self._due_date.setStyleSheet("""
            QDateEdit {
                background: #FFFFFF; border: 1px solid #DDD9D2;
                border-radius: 8px; padding: 0 12px;
                font-size: 13px; color: #1b1b1b; font-family: 'Segoe UI';
            }
            QDateEdit:focus { border: 1px solid #4F6EF7; }
            QDateEdit::drop-down { border: none; width: 0; }
        """)
        self._has_due = QPushButton("✓  Gunakan tanggal jatuh tempo")
        self._has_due.setCheckable(True)
        self._has_due.setChecked(True)
        self._has_due.setCursor(Qt.CursorShape.PointingHandCursor)
        self._has_due.setFixedHeight(28)
        self._has_due.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {C_ACCENT}; font-size:11px;
                font-weight:600; border: none; text-align: left; padding: 0; }}
            QPushButton:hover {{ color: {C_ACCENT_H}; }}
        """)
        self._has_due.toggled.connect(self._due_date.setEnabled)
        cl.addWidget(self._due_date)
        cl.addSpacing(4)
        cl.addWidget(self._has_due)

        self._err_lbl = QLabel("")
        self._err_lbl.setStyleSheet(f"font-size:11px;color:{C_DANGER};font-family:'Segoe UI';border:none;")
        self._err_lbl.setVisible(False)
        cl.addWidget(self._err_lbl)
        cl.addSpacing(18)

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

        save_btn = QPushButton("Tambah Piutang")
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
        total = self._total_input.value()
        if total <= 0:
            self._err_lbl.setText("Total piutang harus lebih dari 0.")
            self._err_lbl.setVisible(True)
            return
        self._err_lbl.setVisible(False)
        customer_id = self._customer_combo.currentData()
        due_date    = (
            self._due_date.date().toString("yyyy-MM-dd")
            if self._has_due.isChecked()
            else None
        )
        self.saved.emit({
            "customer_id": customer_id,
            "total_amount": total,
            "due_date": due_date,
        })
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════════
# Delete Confirm Dialog
# ═══════════════════════════════════════════════════════════════════════════════
class DeleteReceivableDialog(QDialog):
    confirmed = pyqtSignal()

    def __init__(self, rec: Receivables, customer_name: str, parent=None):
        super().__init__(parent)
        self._rec  = rec
        self._name = customer_name
        self.setWindowTitle("Hapus Data Piutang")
        self.setModal(True)
        self.setFixedWidth(400)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setSizeGripEnabled(False)
        self.setStyleSheet(f"QDialog {{ background: {C_WHITE}; font-family: 'Segoe UI'; }}")
        self._build_ui()
        self.adjustSize()
        self.setMaximumSize(400, self.height())

    def _build_ui(self):
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
        cl.addSpacing(14)

        title = QLabel("Hapus Data Piutang?")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)
        cl.addSpacing(4)

        sub = QLabel(
            f"Piutang atas nama <b>{self._name}</b> sebesar "
            f"<b>{_fmt_currency(self._rec.total_amount)}</b> akan dihapus permanen."
        )
        sub.setTextFormat(Qt.TextFormat.RichText)
        sub.setWordWrap(True)
        sub.setStyleSheet("font-size:12px;color:#888780;border:none;")
        cl.addWidget(sub)
        cl.addSpacing(20)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider)
        cl.addSpacing(18)

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

        del_btn = QPushButton("Ya, Hapus")
        del_btn.setFixedHeight(40)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_DANGER}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 600;
                border-radius: 10px; border: none;
            }}
            QPushButton:hover {{ background: #C94040; }}
        """)
        del_btn.clicked.connect(lambda: (self.confirmed.emit(), self.accept()))

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(del_btn)
        cl.addLayout(btn_row)
        root.addWidget(card)


# ═══════════════════════════════════════════════════════════════════════════════
# Receivables Page
# ═══════════════════════════════════════════════════════════════════════════════
class ReceivablesPage(QWidget):
    def __init__(self, user: dict = None, parent=None):
        super().__init__(parent)
        self._user              = user or {}
        self._receivables       = []
        self._customer_map      = {}
        self._customers         = []
        self._active_filter     = "Semua"
        self._search_query      = ""
        self._view_mode         = ReceivablesViewToggle.VIEW_TABLE
        self._grid_initialized  = False
        self._pending_refresh   = False
        self._render_token      = 0
        self._stat_labels: dict[str, QLabel] = {}
        self._stat_dots:   dict[str, QLabel] = {}

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C_BG};")
        self._load_data()
        self._build_ui()

    def _update_due_date(self, data: dict):
        try:
            rec = ReceivablesController.get(data["id"])
            if rec is None:
                raise ValueError("Data piutang tidak ditemukan.")

            ReceivablesController.edit(
                receivable_id=rec.id,
                sales_id=rec.sales_id,
                customer_id=rec.customer_id,
                amount_paid=rec.amount_paid,
                total_amount=rec.total_amount,
                due_date=data["due_date"],
                status=rec.status,
            )
            self._load_data()
            self._refresh_stats()
            self._refresh_view()
            cust = self._customer_map.get(rec.customer_id, "—")
            msg = (
                f"Jatuh tempo <b>{cust}</b> dihapus."
                if data["due_date"] is None
                else f"Jatuh tempo <b>{cust}</b> diperbarui ke {data['due_date']}."
            )
            Toast.show_toast(msg, "success", self)
        except Exception as e:
            Toast.show_toast(str(e), "error", self)

    # ── Data ──────────────────────────────────────────────────────────────────
    def _load_data(self):
        self._receivables = ReceivablesController.fetch()
        self._customers = CustomerController.fetch()

        self._customer_map = {
            c.id: c for c in self._customers
        }

    def _calc_stats(self) -> dict:
        total_debt   = sum(r.total_amount - r.amount_paid for r in self._receivables if r.status != "paid")
        count_unpaid = sum(1 for r in self._receivables if _resolve_status(r.amount_paid, r.total_amount) in ("unpaid", "partial"))
        count_paid   = sum(1 for r in self._receivables if _resolve_status(r.amount_paid, r.total_amount) == "paid")
        return {
            "total_debt":   _fmt_currency(total_debt),
            "count_unpaid": str(count_unpaid),
            "count_paid":   str(count_paid),
        }

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 17, 32, 28)
        layout.setSpacing(0)

        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        page_title = QLabel("Piutang Pelanggan")
        page_title.setStyleSheet(f"font-family:'Segoe UI';font-size:27px;font-weight:700;color:{C_TEXT_PRI};background:transparent;")
        page_sub = QLabel("Pantau dan kelola piutang pelanggan warungmu")
        page_sub.setStyleSheet(f"font-family:'Segoe UI';font-size:13px;color:{C_TEXT_SEC};background:transparent;")
        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        

        header.addLayout(title_col)
        header.addStretch()
        layout.addLayout(header)
        layout.addSpacing(20)

        layout.addLayout(self._build_stats_row())
        layout.addSpacing(20)

        # ── Filter bar + view toggle ───────────────────────────────────────────
        bar_and_toggle = QHBoxLayout()
        bar_and_toggle.setSpacing(10)

        filter_widget = QWidget()
        filter_widget.setStyleSheet("background: transparent;")
        fw_layout = QHBoxLayout(filter_widget)
        fw_layout.setContentsMargins(0, 0, 0, 0)
        fw_layout.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("🔍  Cari nama pelanggan...")
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
        for f in FILTER_STATUS:
            btn = self._make_filter_btn(f)
            self._filter_buttons[f] = btn
            fw_layout.addWidget(btn)
        fw_layout.addStretch()

        self._view_toggle = ReceivablesViewToggle(initial=ReceivablesViewToggle.VIEW_TABLE)
        self._view_toggle.toggled.connect(self._on_view_mode_changed)

        bar_and_toggle.addWidget(filter_widget, stretch=1)
        bar_and_toggle.addWidget(self._view_toggle)
        layout.addLayout(bar_and_toggle)
        layout.addSpacing(16)

        # ── Content stack ──────────────────────────────────────────────────────
        self._content_stack = QStackedWidget()
        self._content_stack.setStyleSheet("background: transparent;")

        # ── Page 0: Card grid ──────────────────────────────────────────────────
        self._card_page = QWidget()
        self._card_page.setStyleSheet("background: transparent;")
        card_page_layout = QVBoxLayout(self._card_page)
        card_page_layout.setContentsMargins(0, 0, 0, 0)
        card_page_layout.setSpacing(0)

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
        card_page_layout.addWidget(self._scroll)

        # ── Page 1: Table ──────────────────────────────────────────────────────
        self._table_page = QWidget()
        self._table_page.setStyleSheet("background: transparent;")
        table_page_layout = QVBoxLayout(self._table_page)
        table_page_layout.setContentsMargins(0, 0, 0, 0)
        table_page_layout.setSpacing(0)

        self._table = ReceivablesTableView()
        self._table.pay_clicked.connect(self._open_pay_dialog)
        self._table.delete_clicked.connect(self._open_delete_dialog)
        self._table.detail_clicked.connect(self._open_detail_dialog)
        self._table.delete_all_clicked.connect(self._open_delete_all_dialog)
        table_page_layout.addWidget(self._table)

        self._content_stack.addWidget(self._card_page)   # index 0
        self._content_stack.addWidget(self._table_page)  # index 1
        self._content_stack.setCurrentIndex(1)

        layout.addWidget(self._content_stack, stretch=1)

        self._refresh_table()

    # ── Stats ─────────────────────────────────────────────────────────────────
    def _build_stats_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(14)
        stats_def = [
            ("count_unpaid", "Belum / Sebagian Lunas",  "#E05252", "#FDEAEA", False),
            ("count_paid",   "Sudah Lunas",             "#27AE60", "#E8F8F0", False),
            ("total_debt",   "Total Sisa Piutang",      "#4F6EF7", "#EEF1FE", True),
        ]
        vals = self._calc_stats()
        for key, label, color, bg, is_currency in stats_def:
            card, lbl, dot = self._stat_card(key, label, vals[key], color, bg, is_currency)
            self._stat_labels[key] = lbl
            self._stat_dots[key]   = dot
            row.addWidget(card)
        return row

    def _stat_card(self, key, label, value, color, bg, is_currency):
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background: {C_WHITE}; border-radius: 12px; border: 1px solid {C_BORDER}; }}")
        card.setFixedHeight(76)

        lay = QHBoxLayout(card)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        indicator = QFrame()
        indicator.setFixedSize(40, 40)
        indicator.setStyleSheet(f"background: {bg}; border-radius: 10px; border: none;")

        ind_lay = QHBoxLayout(indicator)
        ind_lay.setContentsMargins(0, 0, 0, 0)
        ind_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dot = QLabel()
        if is_currency:
            dot.setText("🪙")
            dot.setStyleSheet("font-size: 18px; background: transparent; border: none;")
        else:
            dot.setText(value)
            dot.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {color}; background: transparent; border: none;")
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ind_lay.addWidget(dot)

        val_lbl = QLabel(value)
        val_lbl.setFixedHeight(26)
        val_lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:22px;font-weight:700;color:{C_TEXT_PRI};background:transparent;border:none;")

        lbl_lbl = QLabel(label)
        lbl_lbl.setStyleSheet(f"font-family:'Segoe UI';font-size:11px;color:{C_TEXT_SEC};background:transparent;border:none;")

        text_w = QWidget()
        text_w.setStyleSheet("background: transparent; border: none;")
        tw = QVBoxLayout(text_w)
        tw.setSpacing(3)
        tw.setContentsMargins(0, 0, 0, 0)
        tw.addStretch()
        tw.addWidget(val_lbl)
        tw.addWidget(lbl_lbl)
        tw.addStretch()

        lay.addWidget(indicator)
        lay.addWidget(text_w)
        lay.addStretch()
        return card, val_lbl, dot

    def _refresh_stats(self):
        vals = self._calc_stats()
        for key, val in vals.items():
            lbl = self._stat_labels.get(key)
            if lbl:
                lbl.setText(val)
            dot = self._stat_dots.get(key)
            if dot and key != "total_debt":
                dot.setText(val)

    # ── Filter buttons ────────────────────────────────────────────────────────
    def _make_filter_btn(self, label: str) -> QPushButton:
        active = label == self._active_filter
        btn = QPushButton(label)
        btn.setFixedHeight(38)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_filter_btn(btn, active)
        btn.clicked.connect(lambda _=False, s=label: self._on_filter_changed(s))
        return btn

    def _style_filter_btn(self, btn: QPushButton, active: bool):
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

    # ── Filtering & refresh ───────────────────────────────────────────────────
    def _filtered_rows(self) -> list[tuple]:
        from collections import OrderedDict

        filtered = self._receivables

        if self._search_query:
            q = self._search_query.lower()
            filtered = [
                r for r in filtered
                if (lambda c: (
                    q in (c.name or "").lower() or
                    q in (c.phone or "").lower()
                ) if c else False)(self._customer_map.get(r.customer_id))
            ]

        groups: dict[int | None, list[Receivables]] = OrderedDict()
        for r in filtered:
            groups.setdefault(r.customer_id, []).append(r)

        rows = []
        for cid, recs in groups.items():
            customer     = self._customer_map.get(cid)
            cust_name    = customer.name if customer else "—"
            total_amount = sum(r.total_amount for r in recs)
            amount_paid  = sum(r.amount_paid  for r in recs)
            agg_status   = _resolve_status(amount_paid, total_amount)

            if self._active_filter == "🔴 Belum Lunas" and agg_status != "unpaid":
                continue
            elif self._active_filter == "🟡 Sebagian" and agg_status != "partial":
                continue
            elif self._active_filter == "🟢 Lunas" and agg_status != "paid":
                continue

            rep = recs[0]
            unpaid_dues = [
                r.due_date for r in recs
                if r.due_date and _resolve_status(r.amount_paid, r.total_amount) != "paid"
            ]
            nearest_due = min(unpaid_dues) if unpaid_dues else rep.due_date

            agg_rec = Receivables(
                id           = rep.id,
                sales_id     = rep.sales_id,
                customer_id  = cid,
                total_amount = total_amount,
                amount_paid  = amount_paid,
                due_date     = nearest_due,
                status       = agg_status,
            )
            rows.append((agg_rec, cust_name, recs))

        return rows

    def _refresh_view(self):
        if self._view_mode == ReceivablesViewToggle.VIEW_CARD:
            self._refresh_grid()
        else:
            self._refresh_table()

    def _refresh_table(self):
        self._table.populate(self._filtered_rows(), self._customer_map, self._receivables)

    # ── Card grid ─────────────────────────────────────────────────────────────
    def _get_column_count(self) -> int:
        available = self._scroll.viewport().width()
        cols = available // (ReceivableCard.CARD_WIDTH + self._grid_layout.spacing())
        return max(2, min(4, int(cols)))

    def _refresh_grid(self):
        self._render_token += 1
        token = self._render_token

        if not self.isVisible():
            self._pending_refresh = True
            return

        self._pending_refresh = False
        self._clear_grid()

        rows = self._filtered_rows()

        if not rows:
            self._grid_layout.setAlignment(
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
            )

            empty_wrap = QWidget()
            empty_wrap.setStyleSheet("background: transparent; border: none;")
            empty_wrap.setMinimumWidth(self._scroll.viewport().width())

            outer = QVBoxLayout(empty_wrap)
            outer.setContentsMargins(0, 43, 2, 0)
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
                QLabel {{ background: transparent; border: none; }}
            """)

            ec_layout = QVBoxLayout(empty_card)
            ec_layout.setContentsMargins(40, 34, 40, 34)
            ec_layout.setSpacing(8)
            ec_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon = QLabel("💳")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setStyleSheet("font-size: 46px;")

            etitle = QLabel("Tidak ada data piutang")
            etitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            etitle.setStyleSheet(f"font-family:'Segoe UI';font-size:16px;font-weight:700;color:{C_TEXT_PRI};")

            esub = QLabel("Coba ubah filter atau kata kunci pencarian.")
            esub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            esub.setStyleSheet(f"font-family:'Segoe UI';font-size:12px;color:{C_TEXT_SEC};")

            ec_layout.addStretch()
            ec_layout.addWidget(icon)
            ec_layout.addWidget(etitle)
            ec_layout.addWidget(esub)
            ec_layout.addStretch()

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

        for c in range(10):
            self._grid_layout.setColumnStretch(c, 0)
        for c in range(cols):
            self._grid_layout.setColumnStretch(c, 1)

        if len(rows) <= 60:
            self._render_all_cards(rows, token)
        else:
            self._render_batch_cards(rows, start=0, batch_size=12, token=token)

        self._grid_container.adjustSize()
        self._grid_container.update()
        self._scroll.viewport().update()

    def _render_all_cards(self, rows: list[tuple], token: int):
        cols = self._get_column_count()
        for i, (agg_rec, cust_name, all_for_cust) in enumerate(rows):
            if token != self._render_token:
                return
            customer  = self._customer_map.get(agg_rec.customer_id)
            phone     = customer.phone if customer else ""
            card = ReceivableCard(agg_rec, cust_name, phone, all_for_cust)
            card.pay_clicked.connect(self._open_pay_dialog)
            card.delete_clicked.connect(self._open_delete_dialog)
            card.detail_clicked.connect(self._open_detail_dialog)
            card.delete_all_clicked.connect(self._open_delete_all_dialog)
            self._grid_layout.addWidget(card, i // cols, i % cols)

    def _render_batch_cards(
        self,
        rows: list[tuple],
        start: int,
        batch_size: int,
        token: int,
    ):
        if token != self._render_token:
            return
        cols = self._get_column_count()
        end  = min(start + batch_size, len(rows))

        for i in range(start, end):
            agg_rec, cust_name, all_for_cust = rows[i]
            customer = self._customer_map.get(agg_rec.customer_id)
            phone    = customer.phone if customer else ""
            card = ReceivableCard(agg_rec, cust_name, phone, all_for_cust)
            card.pay_clicked.connect(self._open_pay_dialog)
            card.delete_clicked.connect(self._open_delete_dialog)
            card.detail_clicked.connect(self._open_detail_dialog)
            card.delete_all_clicked.connect(self._open_delete_all_dialog)
            self._grid_layout.addWidget(card, i // cols, i % cols)

        if end < len(rows):
            QTimer.singleShot(
                0,
                lambda: self._render_batch_cards(rows, end, batch_size, token),
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
        if self._view_mode == ReceivablesViewToggle.VIEW_CARD:
            QTimer.singleShot(0, self._refresh_grid)

    # ── Event handlers ────────────────────────────────────────────────────────
    def _on_view_mode_changed(self, mode: str):
        self._view_mode = mode
        if mode == ReceivablesViewToggle.VIEW_TABLE:
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
            self._style_filter_btn(btn, False)
        self._active_filter = label
        if btn := self._filter_buttons.get(label):
            self._style_filter_btn(btn, True)
        self._refresh_view()

    def _open_add_dialog(self):
        dlg = AddReceivableDialog(customers=self._customers, parent=self)
        dlg.saved.connect(self._add_receivable)
        dlg.exec()

    def _open_pay_dialog(self, rec: Receivables):
        customer = self._customer_map.get(rec.customer_id)
        cust_name = customer.name if customer else "—"

        dlg = PayDialog(rec=rec, customer_name=cust_name, parent=self)
        dlg.paid.connect(self._record_payment)
        dlg.exec()

    def _open_delete_dialog(self, rec: Receivables):
        customer = self._customer_map.get(rec.customer_id)
        cust_name = customer.name if customer else "—"

        dlg = DeleteReceivableDialog(rec=rec, customer_name=cust_name, parent=self)
        dlg.confirmed.connect(lambda: self._delete_receivable(rec))
        dlg.exec()

    def _open_detail_dialog(self, customer_name: str, records: list[Receivables]):
        dlg = CustomerDetailDialog(customer_name=customer_name, records=records, parent=self)
        dlg.pay_clicked.connect(lambda rec: (dlg.accept(), self._open_pay_dialog(rec)))
        dlg.delete_clicked.connect(lambda rec: (dlg.accept(), self._open_delete_dialog(rec)))
        dlg.exec()

    def _open_delete_all_dialog(self, customer_name: str, records: list[Receivables]):
        dlg = DeleteAllReceivablesDialog(records=records, customer_name=customer_name, parent=self)
        dlg.confirmed.connect(lambda: self._delete_all_receivables(records))
        dlg.exec()

    # ── CRUD handlers ─────────────────────────────────────────────────────────
    def _add_receivable(self, data: dict):
        try:
            ReceivablesController.add(
                sales_id=0,
                customer_id=data["customer_id"],
                total_amount=data["total_amount"],
                due_date=data["due_date"],
                amount_paid=0.0,
                status="unpaid",
            )
            self._load_data()
            self._refresh_stats()
            self._refresh_view()
            cust = self._customer_map.get(data["customer_id"], "Pelanggan")
            Toast.show_toast(f"Piutang <b>{cust}</b> berhasil ditambahkan.", "success", self)
        except Exception as e:
            Toast.show_toast(str(e), "error", self)

    def _record_payment(self, data: dict):
        try:
            rec = ReceivablesController.get(data["id"])
            if rec is None:
                raise ValueError("Data piutang tidak ditemukan.")

            new_paid   = rec.amount_paid + data["amount"]
            new_status = _resolve_status(new_paid, rec.total_amount)

            ReceivablesController.edit(
                receivable_id=rec.id,
                sales_id=rec.sales_id,
                customer_id=rec.customer_id,
                amount_paid=new_paid,
                total_amount=rec.total_amount,
                due_date=rec.due_date,
                status=new_status,
            )

            # ── Update paid_amount di Sales ──
            if rec.sales_id:
                from controllers.sales import SalesController
                sale = SalesController.get(rec.sales_id)
                if sale:
                    SalesController.edit(
                        sale_id=sale.id,
                        customer_id=sale.customer_id,
                        cashier_id=sale.cashier_id,
                        time=sale.time,
                        payment=sale.payment,
                        paid_amount=new_paid,
                        total_price=sale.total_price,
                    )

            # ── Trigger refresh transactions_page ──
            from gui.signals import sales_signals
            sales_signals.sales_completed.emit(rec.sales_id or 0)

            self._load_data()
            self._refresh_stats()
            self._refresh_view()
            customer = self._customer_map.get(rec.customer_id)
            cust_name = customer.name if customer else "Pelanggan"

            msg = (
                f"Piutang <b>{cust_name}</b> lunas!"
                if new_status == "paid"
                else f"Pembayaran <b>{cust_name}</b> tercatat."
            )

            Toast.show_toast(msg, "success", self)
        except Exception as e:
            Toast.show_toast(str(e), "error", self)

    def _delete_receivable(self, rec: Receivables):
        try:
            ReceivablesController.remove(rec.id)
            self._load_data()
            self._refresh_stats()
            self._refresh_view()
            from gui.signals import sales_signals
            sales_signals.sales_completed.emit(rec.sales_id or 0)
            customer = self._customer_map.get(rec.customer_id)
            cust_name = customer.name if customer else "Pelanggan"
            Toast.show_toast(
                f"Piutang <b>{cust_name}</b> berhasil dihapus.",
                "success",
                self
            )
        except Exception as e:
            Toast.show_toast(str(e), "error", self)

    def _delete_all_receivables(self, records: list[Receivables]):
        try:
            customer = self._customer_map.get(records[0].customer_id)
            cust_name = customer.name if customer else "Pelanggan"

            for rec in records:
                ReceivablesController.remove(rec.id)

            self._load_data()
            self._refresh_stats()
            self._refresh_view()

            from gui.signals import sales_signals
            for rec in records:
                if rec.sales_id:
                    sales_signals.sales_completed.emit(rec.sales_id)

            Toast.show_toast(
                f"Semua piutang <b>{cust_name}</b> berhasil dihapus.",
                "success",
                self
            )

        except Exception as e:
            Toast.show_toast(str(e), "error", self)

    def showEvent(self, event):
        super().showEvent(event)
        self._load_data()
        self._refresh_stats()
        if not self._grid_initialized or self._pending_refresh:
            self._grid_initialized = True
            self._pending_refresh  = False
            QTimer.singleShot(0, self._refresh_view)
        else:
            self._refresh_view()