# gui/views/screens/dashboard_page.py

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Literal

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
    QScrollArea,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)

from controllers.product import ProductController, Product
from controllers.sales import SalesController, Sales
from controllers.sales_detail import SalesDetailController, SalesDetail
from controllers.receivables import ReceivablesController
from gui.views.components.toast import Toast


# ── Color palette: disamakan dengan product_page.py / sales_page.py ───────────
C_BG = "#F4F5F9"
C_WHITE = "#FFFFFF"
C_ACCENT = "#4F6EF7"
C_ACCENT_H = "#3A57E8"
C_TEXT_PRI = "#1A1D2E"
C_TEXT_SEC = "#6B6F80"
C_BORDER = "#E4E6EE"
C_DANGER = "#E05252"
C_SUCCESS = "#27AE60"
C_WARNING = "#E07D2A"
C_TAG_BG = "#EEF1FE"
C_ROW_ALT = "#FAFBFF"

ENABLE_CARD_SHADOWS = False
RADIUS = 14
LOW_STOCK_THRESHOLD = 20

SAMPLE_CATEGORIES = ["Makanan", "Minuman", "Snack", "Sembako", "Lainnya"]

CAT_THEME = {
    "Makanan": {"emoji": "🍽️", "bg": "#FFF4E8", "text": "#E67E22"},
    "Minuman": {"emoji": "🥤", "bg": "#EAF7FF", "text": "#3498DB"},
    "Snack": {"emoji": "🍿", "bg": "#FFF0F6", "text": "#E84393"},
    "Sembako": {"emoji": "🛒", "bg": "#EEFCEF", "text": "#27AE60"},
    "Lainnya": {"emoji": "📦", "bg": "#F1F3F8", "text": "#6C757D"},
}

Period = Literal["daily", "weekly", "monthly"]


def _cat_theme(category: str | None) -> dict:
    return CAT_THEME.get(category or "Lainnya", {"emoji": "📦", "bg": "#F1F3F8", "text": "#6C757D"})


def _format_price(price: float | int | None) -> str:
    value = float(price or 0)
    return f"Rp {value:,.0f}".replace(",", ".")


def _format_number(value: int | float | None) -> str:
    return f"{int(value or 0):,}".replace(",", ".")


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


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _period_start(period: Period) -> datetime:
    now = datetime.now()

    if period == "daily":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == "weekly":
        start = now - timedelta(days=now.weekday())
        return start.replace(hour=0, minute=0, second=0, microsecond=0)

    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _period_label(period: Period) -> str:
    if period == "daily":
        return "Hari Ini"
    if period == "weekly":
        return "Minggu Ini"
    return "Bulan Ini"


def _same_period(time_value: str | None, period: Period) -> bool:
    dt = _parse_datetime(time_value)
    if not dt:
        return False
    return dt >= _period_start(period)


# ═══════════════════════════════════════════════════════════════════════════════
# Simple Bar Chart Widget
# ═══════════════════════════════════════════════════════════════════════════════
class SalesChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[tuple[str, float]] = []
        self.setMinimumHeight(260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, data: list[tuple[str, float]]):
        self._data = data
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        if w <= 0 or h <= 0:
            return

        left = 44
        right = 18
        top = 18
        bottom = 42

        chart_w = max(1, w - left - right)
        chart_h = max(1, h - top - bottom)

        # Background grid
        grid_pen = QPen(QColor(C_BORDER))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)

        for i in range(5):
            y = top + int(chart_h * i / 4)
            painter.drawLine(left, y, left + chart_w, y)

        if not self._data:
            painter.setPen(QColor(C_TEXT_SEC))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Belum ada data penjualan")
            return

        max_value = max(value for _, value in self._data) or 1
        count = len(self._data)
        gap = 10 if count <= 12 else 5
        bar_w = max(8, int((chart_w - gap * (count + 1)) / count))

        for idx, (label, value) in enumerate(self._data):
            x = left + gap + idx * (bar_w + gap)
            bar_h = int((value / max_value) * (chart_h - 10)) if max_value else 0
            y = top + chart_h - bar_h

            rect_path = QPainterPath()
            rect_path.addRoundedRect(x, y, bar_w, bar_h, 5, 5)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(C_ACCENT)))
            painter.drawPath(rect_path)

            painter.setPen(QColor(C_TEXT_SEC))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)

            if count <= 12 or idx % 2 == 0:
                painter.drawText(
                    x - 8,
                    top + chart_h + 18,
                    bar_w + 16,
                    16,
                    Qt.AlignmentFlag.AlignCenter,
                    label,
                )

        # Y-axis max label
        painter.setPen(QColor(C_TEXT_SEC))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(0, top - 2, left - 8, 16, Qt.AlignmentFlag.AlignRight, _format_price(max_value))
        painter.drawText(0, top + chart_h - 10, left - 8, 16, Qt.AlignmentFlag.AlignRight, "Rp 0")


# ═══════════════════════════════════════════════════════════════════════════════
# Reusable UI Components
# ═══════════════════════════════════════════════════════════════════════════════
class MetricCard(QFrame):
    def __init__(self, title: str, value: str, subtitle: str, icon: str, color: str = C_ACCENT, parent=None):
        super().__init__(parent)
        self._title = title
        self._value = value
        self._subtitle = subtitle
        self._icon = icon
        self._color = color
        self._build()

    def _build(self):
        self.setObjectName("MetricCard")
        self.setMinimumHeight(122)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame#MetricCard {{
                background: {C_WHITE};
                border-radius: {RADIUS}px;
                border: 1.5px solid {C_BORDER};
            }}
        """)
        _apply_card_shadow(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(8)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)

        title = QLabel(self._title)
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            font-weight: 600;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)

        icon = QLabel(self._icon)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedSize(34, 34)
        icon.setStyleSheet(f"""
            background: {C_TAG_BG};
            color: {self._color};
            border-radius: 10px;
            border: none;
            font-size: 16px;
        """)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(icon)
        root.addLayout(top)

        self._value_lbl = QLabel(self._value)
        self._value_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 22px;
            font-weight: 800;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        root.addWidget(self._value_lbl)

        self._subtitle_lbl = QLabel(self._subtitle)
        self._subtitle_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 11px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        root.addWidget(self._subtitle_lbl)

    def set_values(self, value: str, subtitle: str):
        self._value_lbl.setText(value)
        self._subtitle_lbl.setText(subtitle)


class CategoryCard(QFrame):
    def __init__(self, category: str, product_count: int, stock_count: int, parent=None):
        super().__init__(parent)
        self._category = category
        self._product_count = product_count
        self._stock_count = stock_count
        self._build()

    def _build(self):
        theme = _cat_theme(self._category)
        self.setObjectName("CategoryCard")
        self.setFixedHeight(86)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame#CategoryCard {{
                background: {C_WHITE};
                border-radius: 12px;
                border: 1.5px solid {C_BORDER};
            }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(12)

        icon = QLabel(theme["emoji"])
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedSize(42, 42)
        icon.setStyleSheet(f"""
            background: {theme['bg']};
            color: {theme['text']};
            border-radius: 12px;
            border: none;
            font-size: 20px;
        """)
        root.addWidget(icon)

        info = QVBoxLayout()
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(2)

        name = QLabel(self._category)
        name.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 13px;
            font-weight: 700;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        info.addWidget(name)

        sub = QLabel(f"{_format_number(self._product_count)} produk • {_format_number(self._stock_count)} stok")
        sub.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 11px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        info.addWidget(sub)

        root.addLayout(info)


class InsightItem(QFrame):
    def __init__(self, title: str, subtitle: str, badge_text: str, badge_color: str = C_ACCENT, parent=None):
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._badge_text = badge_text
        self._badge_color = badge_color
        self._build()

    def _build(self):
        self.setObjectName("InsightItem")
        self.setFixedHeight(58)
        self.setStyleSheet(f"""
            QFrame#InsightItem {{
                background: {C_ROW_ALT};
                border-radius: 10px;
                border: 1px solid {C_BORDER};
            }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        root.setSpacing(10)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(1)

        title = QLabel(self._title)
        title.setWordWrap(False)
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            font-weight: 700;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        text_col.addWidget(title)

        subtitle = QLabel(self._subtitle)
        subtitle.setWordWrap(False)
        subtitle.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 10px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        text_col.addWidget(subtitle)

        root.addLayout(text_col, stretch=1)

        badge = QLabel(self._badge_text)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setMinimumWidth(58)
        badge.setFixedHeight(26)
        badge.setStyleSheet(f"""
            background: {C_WHITE};
            color: {self._badge_color};
            border: 1px solid {self._badge_color};
            border-radius: 7px;
            font-family: 'Segoe UI';
            font-size: 10px;
            font-weight: 700;
            padding: 0 8px;
        """)
        root.addWidget(badge)


class InsightCard(QFrame):
    def __init__(self, title: str, icon: str, empty_text: str, parent=None):
        super().__init__(parent)
        self._title = title
        self._icon = icon
        self._empty_text = empty_text
        self._items_layout: QVBoxLayout | None = None
        self._build()

    def _build(self):
        self.setObjectName("InsightCard")
        self.setMinimumHeight(254)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame#InsightCard {{
                background: {C_WHITE};
                border-radius: {RADIUS}px;
                border: 1.5px solid {C_BORDER};
            }}
        """)
        _apply_card_shadow(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        icon = QLabel(self._icon)
        icon.setFixedSize(30, 30)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"""
            background: {C_TAG_BG};
            color: {C_ACCENT};
            border-radius: 9px;
            font-size: 14px;
            border: none;
        """)
        header.addWidget(icon)

        title = QLabel(self._title)
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 14px;
            font-weight: 800;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        header.addWidget(title)
        header.addStretch()
        root.addLayout(header)

        self._items_layout = QVBoxLayout()
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSpacing(8)
        root.addLayout(self._items_layout)
        root.addStretch()

        self.set_items([])

    def set_items(self, items: list[tuple[str, str, str, str]]):
        if not self._items_layout:
            return

        while self._items_layout.count():
            item = self._items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not items:
            empty = QLabel(self._empty_text)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setMinimumHeight(160)
            empty.setStyleSheet(f"""
                font-family: 'Segoe UI';
                font-size: 12px;
                color: {C_TEXT_SEC};
                background: transparent;
                border: none;
            """)
            self._items_layout.addWidget(empty)
            return

        for title, subtitle, badge, color in items:
            self._items_layout.addWidget(InsightItem(title, subtitle, badge, color))


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard Page
# ═══════════════════════════════════════════════════════════════════════════════
class DashboardPage(QWidget):
    def __init__(self, user: dict | None = None, parent=None):
        super().__init__(parent)
        self._user = user or {}
        self._active_period: Period = "daily"

        self._products: list[Product] = []
        self._sales: list[Sales] = []
        self._sales_details: list[SalesDetail] = []

        self._period_buttons: dict[Period, QPushButton] = {}

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C_BG};")

        self._build_ui()
        self._load_data()

    # ── UI Build ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
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

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(18)

        self._build_header(self._content_layout)
        self._build_metric_cards(self._content_layout)
        self._build_category_section(self._content_layout)
        self._build_chart_section(self._content_layout)
        self._build_insight_section(self._content_layout)

        scroll.setWidget(content)
        root.addWidget(scroll)

    def _build_header(self, parent_layout: QVBoxLayout):
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title_col.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Dashboard")
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 24px;
            font-weight: 800;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        title_col.addWidget(title)

        subtitle = QLabel("Ringkasan penjualan, produk, dan stok toko")
        subtitle.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 13px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        title_col.addWidget(subtitle)

        header.addLayout(title_col)
        header.addStretch()

        period_wrap = QFrame()
        period_wrap.setFixedHeight(40)
        period_wrap.setStyleSheet(f"""
            QFrame {{
                background: {C_WHITE};
                border: 1.5px solid {C_BORDER};
                border-radius: 10px;
            }}
        """)
        period_layout = QHBoxLayout(period_wrap)
        period_layout.setContentsMargins(4, 4, 4, 4)
        period_layout.setSpacing(4)

        for key, label in [("daily", "Hari Ini"), ("weekly", "Minggu"), ("monthly", "Bulan")]:
            btn = QPushButton(label)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, p=key: self._set_period(p))
            period_layout.addWidget(btn)
            self._period_buttons[key] = btn

        header.addWidget(period_wrap)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT};
                color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 700;
                border-radius: 10px;
                border: none;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: {C_ACCENT_H};
            }}
        """)
        refresh_btn.clicked.connect(self._load_data)
        header.addWidget(refresh_btn)

        parent_layout.addLayout(header)
        self._refresh_period_button_styles()

    def _build_metric_cards(self, parent_layout: QVBoxLayout):
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        self._revenue_card = MetricCard("Pendapatan", "Rp 0", "Hari Ini", "💰", C_ACCENT)
        self._transaction_card = MetricCard("Transaksi", "0", "Total transaksi", "🧾", C_SUCCESS)
        self._product_card = MetricCard("Total Produk", "0", "0 kategori aktif", "📦", C_ACCENT)
        self._restock_card = MetricCard("Perlu Restock", "0", "Stok rendah / habis", "⚠️", C_WARNING)

        cards = [
            self._revenue_card,
            self._transaction_card,
            self._product_card,
            self._restock_card,
        ]

        for i, card in enumerate(cards):
            grid.addWidget(card, 0, i)
            grid.setColumnStretch(i, 1)

        parent_layout.addLayout(grid)

    def _build_category_section(self, parent_layout: QVBoxLayout):
        section = QVBoxLayout()
        section.setContentsMargins(0, 0, 0, 0)
        section.setSpacing(10)

        title = QLabel("Kategori Produk")
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 16px;
            font-weight: 800;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        section.addWidget(title)

        self._category_grid = QGridLayout()
        self._category_grid.setContentsMargins(0, 0, 0, 0)
        self._category_grid.setHorizontalSpacing(12)
        self._category_grid.setVerticalSpacing(12)
        section.addLayout(self._category_grid)

        parent_layout.addLayout(section)

    def _build_chart_section(self, parent_layout: QVBoxLayout):
        card = QFrame()
        card.setObjectName("ChartCard")
        card.setMinimumHeight(360)
        card.setStyleSheet(f"""
            QFrame#ChartCard {{
                background: {C_WHITE};
                border-radius: {RADIUS}px;
                border: 1.5px solid {C_BORDER};
            }}
        """)
        _apply_card_shadow(card)

        root = QVBoxLayout(card)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(14)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        title = QLabel("Chart Penjualan")
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 16px;
            font-weight: 800;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        text_col.addWidget(title)

        self._chart_subtitle = QLabel("Pendapatan berdasarkan periode")
        self._chart_subtitle.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        text_col.addWidget(self._chart_subtitle)

        header.addLayout(text_col)
        header.addStretch()
        root.addLayout(header)

        self._sales_chart = SalesChartWidget()
        root.addWidget(self._sales_chart, stretch=1)

        parent_layout.addWidget(card)

    def _build_insight_section(self, parent_layout: QVBoxLayout):
        section = QVBoxLayout()
        section.setContentsMargins(0, 0, 0, 0)
        section.setSpacing(10)

        title = QLabel("Insight Produk")
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 16px;
            font-weight: 800;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        section.addWidget(title)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        self._top_selling_card = InsightCard("Produk Paling Laku", "🔥", "Belum ada produk terjual")
        self._low_selling_card = InsightCard("Produk Kurang Laku", "📉", "Belum ada data pembanding")
        self._low_stock_card = InsightCard("Produk Perlu Restock", "⚠️", "Stok produk masih aman")

        grid.addWidget(self._top_selling_card, 0, 0)
        grid.addWidget(self._low_selling_card, 0, 1)
        grid.addWidget(self._low_stock_card, 0, 2)

        for i in range(3):
            grid.setColumnStretch(i, 1)

        section.addLayout(grid)
        parent_layout.addLayout(section)

    # ── Data Load / Refresh ───────────────────────────────────────────────────
    def _load_data(self):
        try:
            self._products = ProductController.fetch()
            self._sales = SalesController.fetch()
            self._sales_details = SalesDetailController.fetch()
            self._refresh_dashboard()
        except Exception as e:
            Toast.show_toast(f"Gagal memuat dashboard: {str(e)}", "error", self)

    def _set_period(self, period: Period):
        self._active_period = period
        self._refresh_period_button_styles()
        self._refresh_dashboard()

    def _refresh_period_button_styles(self):
        for period, btn in self._period_buttons.items():
            active = period == self._active_period
            if active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {C_ACCENT};
                        color: #FFFFFF;
                        font-family: 'Segoe UI';
                        font-size: 11px;
                        font-weight: 700;
                        border-radius: 8px;
                        border: none;
                        padding: 0 12px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {C_TEXT_SEC};
                        font-family: 'Segoe UI';
                        font-size: 11px;
                        font-weight: 600;
                        border-radius: 8px;
                        border: none;
                        padding: 0 12px;
                    }}
                    QPushButton:hover {{
                        background: {C_TAG_BG};
                        color: {C_ACCENT};
                    }}
                """)

    def _refresh_dashboard(self):
        period_sales = self._filtered_sales()
        period_sales_ids = {sale.id for sale in period_sales}
        period_details = [d for d in self._sales_details if d.sales_id in period_sales_ids]

        self._refresh_metrics(period_sales)
        self._refresh_categories()
        self._refresh_chart(period_sales)
        self._refresh_insights(period_details)

    # ── Data Helpers ──────────────────────────────────────────────────────────
    def _filtered_sales(self) -> list[Sales]:
        return [sale for sale in self._sales if _same_period(sale.time, self._active_period)]

    def _refresh_metrics(self, period_sales: list[Sales]):
        revenue = sum(float(sale.total_price or 0) for sale in period_sales)
        transaction_count = len(period_sales)
        product_count = len(self._products)
        active_categories = len({p.category for p in self._products if p.category})
        low_stock_count = len([p for p in self._products if int(p.stock or 0) < LOW_STOCK_THRESHOLD])
        empty_stock_count = len([p for p in self._products if int(p.stock or 0) == 0])

        label = _period_label(self._active_period)
        self._revenue_card.set_values(_format_price(revenue), label)
        self._transaction_card.set_values(_format_number(transaction_count), f"Transaksi {_period_label(self._active_period).lower()}")
        self._product_card.set_values(_format_number(product_count), f"{_format_number(active_categories)} kategori aktif")
        self._restock_card.set_values(_format_number(low_stock_count), f"{_format_number(empty_stock_count)} produk habis")

    def _refresh_categories(self):
        while self._category_grid.count():
            item = self._category_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        stats = {cat: {"count": 0, "stock": 0} for cat in SAMPLE_CATEGORIES}

        for product in self._products:
            cat = product.category if product.category in stats else "Lainnya"
            stats[cat]["count"] += 1
            stats[cat]["stock"] += int(product.stock or 0)

        for i, cat in enumerate(SAMPLE_CATEGORIES):
            card = CategoryCard(cat, stats[cat]["count"], stats[cat]["stock"])
            self._category_grid.addWidget(card, 0, i)
            self._category_grid.setColumnStretch(i, 1)

    def _refresh_chart(self, period_sales: list[Sales]):
        data = self._build_chart_data(period_sales)
        self._sales_chart.set_data(data)

        if self._active_period == "daily":
            self._chart_subtitle.setText("Pendapatan hari ini per jam")
        elif self._active_period == "weekly":
            self._chart_subtitle.setText("Pendapatan minggu ini per hari")
        else:
            self._chart_subtitle.setText("Pendapatan bulan ini per tanggal")

    def _build_chart_data(self, period_sales: list[Sales]) -> list[tuple[str, float]]:
        buckets: dict[str, float] = defaultdict(float)

        if self._active_period == "daily":
            labels = [f"{hour:02d}" for hour in range(24)]
            for label in labels:
                buckets[label] = 0

            for sale in period_sales:
                dt = _parse_datetime(sale.time)
                if dt:
                    buckets[f"{dt.hour:02d}"] += float(sale.total_price or 0)

            return [(label, buckets[label]) for label in labels]

        if self._active_period == "weekly":
            day_labels = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
            for label in day_labels:
                buckets[label] = 0

            for sale in period_sales:
                dt = _parse_datetime(sale.time)
                if dt:
                    buckets[day_labels[dt.weekday()]] += float(sale.total_price or 0)

            return [(label, buckets[label]) for label in day_labels]

        now = datetime.now()
        day_count = now.day
        labels = [str(day) for day in range(1, day_count + 1)]
        for label in labels:
            buckets[label] = 0

        for sale in period_sales:
            dt = _parse_datetime(sale.time)
            if dt:
                buckets[str(dt.day)] += float(sale.total_price or 0)

        return [(label, buckets[label]) for label in labels]

    def _refresh_insights(self, period_details: list[SalesDetail]):
        product_map = {p.id: p for p in self._products}
        sold_qty: dict[int, int] = defaultdict(int)

        for detail in period_details:
            sold_qty[detail.product_id] += int(detail.quantity or 0)

        top_items = self._build_top_selling_items(product_map, sold_qty)
        low_items = self._build_low_selling_items(product_map, sold_qty)
        stock_items = self._build_low_stock_items()

        self._top_selling_card.set_items(top_items)
        self._low_selling_card.set_items(low_items)
        self._low_stock_card.set_items(stock_items)

    def _build_top_selling_items(self, product_map: dict[int, Product], sold_qty: dict[int, int]) -> list[tuple[str, str, str, str]]:
        ranked = sorted(
            [(product_id, qty) for product_id, qty in sold_qty.items() if qty > 0 and product_id in product_map],
            key=lambda item: item[1],
            reverse=True,
        )[:3]

        items = []
        for product_id, qty in ranked:
            product = product_map[product_id]
            items.append((
                product.name,
                f"{product.category or 'Tanpa kategori'} • Stok {int(product.stock or 0)}",
                f"{_format_number(qty)} terjual",
                C_SUCCESS,
            ))
        return items

    def _build_low_selling_items(self, product_map: dict[int, Product], sold_qty: dict[int, int]) -> list[tuple[str, str, str, str]]:
        if not self._products:
            return []

        ranked = sorted(
            self._products,
            key=lambda product: (sold_qty.get(product.id, 0), product.name.lower()),
        )[:3]

        items = []
        for product in ranked:
            qty = sold_qty.get(product.id, 0)
            items.append((
                product.name,
                f"{product.category or 'Tanpa kategori'} • Stok {int(product.stock or 0)}",
                f"{_format_number(qty)} terjual",
                C_WARNING if qty > 0 else C_DANGER,
            ))
        return items

    def _build_low_stock_items(self) -> list[tuple[str, str, str, str]]:
        low_stock = sorted(
            [p for p in self._products if int(p.stock or 0) < LOW_STOCK_THRESHOLD],
            key=lambda product: int(product.stock or 0),
        )[:3]

        items = []
        for product in low_stock:
            stock = int(product.stock or 0)
            if stock == 0:
                badge = "Habis"
                color = C_DANGER
            else:
                badge = f"Sisa {stock}"
                color = C_WARNING

            items.append((
                product.name,
                f"{product.category or 'Tanpa kategori'} • SKU {product.sku or '-'}",
                badge,
                color,
            ))
        return items


# Optional local preview untuk testing langsung file ini.
# Jalankan hanya jika struktur project dan database sudah siap.
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = DashboardPage(user={"id": 1, "name": "Admin"})
    window.resize(1280, 820)
    window.show()
    sys.exit(app.exec())
