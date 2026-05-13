# gui/views/screens/reports_page.py

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from PyQt6.QtCore import Qt
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
    QFileDialog,
)

from controllers.product import ProductController, Product
from controllers.sales import SalesController, Sales
from controllers.sales_detail import SalesDetailController, SalesDetail
from controllers.purchase import PurchaseController, Purchase
from controllers.purchase_detail import PurchaseDetailController, PurchaseDetail
from controllers.receivables import ReceivablesController, Receivables
from gui.views.components.toast import Toast
from gui.signals import sales_signals


# ─────────────────────────────────────────────────────────────────────────────
# Theme
# ─────────────────────────────────────────────────────────────────────────────
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

CHART_COLORS = [
    "#4F6EF7",
    "#27AE60",
    "#E07D2A",
    "#E05252",
    "#8E44AD",
    "#16A085",
    "#F2C94C",
    "#3498DB",
    "#E84393",
    "#6C757D",
]

ENABLE_CARD_SHADOWS = False
RADIUS = 14
LOW_STOCK_THRESHOLD = 20

Period = Literal["daily", "weekly", "monthly"]
ChartType = Literal["bar", "line"]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _format_price(price: float | int | None) -> str:
    value = float(price or 0)
    return f"Rp {value:,.0f}".replace(",", ".")


def _format_number(value: int | float | None) -> str:
    return f"{int(value or 0):,}".replace(",", ".")


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    value = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _period_start(period: Period) -> datetime:
    now = datetime.now()

    if period == "daily":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == "weekly":
        return (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)

    return (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)


def _period_end() -> datetime:
    return datetime.now()


def _period_label(period: Period) -> str:
    if period == "daily":
        return "Hari Ini"
    if period == "weekly":
        return "7 Hari Terakhir"
    return "30 Hari Terakhir"


def _period_date_range(period: Period) -> tuple[datetime, datetime]:
    return _period_start(period), _period_end()


def _same_period(time_value: str | None, period: Period) -> bool:
    dt = _parse_datetime(time_value)
    if not dt:
        return False
    return dt >= _period_start(period)


def _apply_card_shadow(widget: QWidget):
    if ENABLE_CARD_SHADOWS:
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 18))
        widget.setGraphicsEffect(shadow)
    else:
        widget.setGraphicsEffect(None)


def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()


# ─────────────────────────────────────────────────────────────────────────────
# Chart Widgets
# ─────────────────────────────────────────────────────────────────────────────
class SimpleChartWidget(QWidget):
    def __init__(self, chart_type: ChartType = "bar", parent=None):
        super().__init__(parent)
        self._chart_type = chart_type
        self._data: list[tuple[str, float]] = []
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, data: list[tuple[str, float]]):
        self._data = data
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        left, right, top, bottom = 54, 18, 18, 42
        chart_w = max(1, w - left - right)
        chart_h = max(1, h - top - bottom)

        painter.setPen(QPen(QColor(C_BORDER), 1))
        for i in range(5):
            y = top + int(chart_h * i / 4)
            painter.drawLine(left, y, left + chart_w, y)

        has_non_zero = any(value > 0 for _, value in self._data)
        if not self._data or not has_non_zero:
            painter.setPen(QColor(C_TEXT_SEC))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Belum ada data")
            return

        max_value = max(value for _, value in self._data) or 1

        if self._chart_type == "line":
            self._draw_line(painter, left, top, chart_w, chart_h, max_value)
        else:
            self._draw_bar(painter, left, top, chart_w, chart_h, max_value)

        painter.setPen(QColor(C_TEXT_SEC))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(0, top - 2, left - 8, 16, Qt.AlignmentFlag.AlignRight, _format_price(max_value))
        painter.drawText(0, top + chart_h - 10, left - 8, 16, Qt.AlignmentFlag.AlignRight, "0")

        count = len(self._data)
        step = 1 if count <= 10 else 2 if count <= 18 else 4

        for idx, (label, _) in enumerate(self._data):
            if idx % step != 0 and idx != count - 1:
                continue

            if count == 1:
                x = left + chart_w // 2
            else:
                x = left + int(idx * chart_w / (count - 1))

            painter.drawText(
                x - 30,
                top + chart_h + 18,
                60,
                16,
                Qt.AlignmentFlag.AlignCenter,
                label,
            )

    def _draw_bar(self, painter: QPainter, left: int, top: int, chart_w: int, chart_h: int, max_value: float):
        count = len(self._data)
        gap = 10 if count <= 12 else 5
        bar_w = max(7, int((chart_w - gap * (count + 1)) / max(1, count)))

        for idx, (_, value) in enumerate(self._data):
            if value <= 0:
                continue

            x = left + gap + idx * (bar_w + gap)
            bar_h = int((value / max_value) * (chart_h - 10))
            y = top + chart_h - bar_h

            path = QPainterPath()
            path.addRoundedRect(x, y, bar_w, max(2, bar_h), 5, 5)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(CHART_COLORS[idx % len(CHART_COLORS)])))
            painter.drawPath(path)

    def _draw_line(self, painter: QPainter, left: int, top: int, chart_w: int, chart_h: int, max_value: float):
        count = len(self._data)
        points: list[tuple[int, int]] = []

        for idx, (_, value) in enumerate(self._data):
            if count == 1:
                x = left + chart_w // 2
            else:
                x = left + int(idx * chart_w / (count - 1))
            y = top + chart_h - int((value / max_value) * (chart_h - 10))
            points.append((x, y))

        painter.setPen(QPen(QColor(C_ACCENT), 3))
        for i in range(1, len(points)):
            painter.drawLine(points[i - 1][0], points[i - 1][1], points[i][0], points[i][1])

        painter.setPen(Qt.PenStyle.NoPen)
        for idx, (x, y) in enumerate(points):
            painter.setBrush(QBrush(QColor(CHART_COLORS[idx % len(CHART_COLORS)])))
            painter.drawEllipse(x - 4, y - 4, 8, 8)


class PieChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[tuple[str, float]] = []
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, data: list[tuple[str, float]]):
        self._data = [(label, value) for label, value in data if value > 0]
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        total = sum(value for _, value in self._data)
        if not self._data or total <= 0:
            painter.setPen(QColor(C_TEXT_SEC))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Belum ada data")
            return

        size = min(w * 0.42, h * 0.72)
        x = 28
        y = int((h - size) / 2)
        rect = int(x), int(y), int(size), int(size)

        start_angle = 0
        for idx, (_, value) in enumerate(self._data):
            span_angle = int((value / total) * 360 * 16)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(CHART_COLORS[idx % len(CHART_COLORS)])))
            painter.drawPie(*rect, start_angle, span_angle)
            start_angle += span_angle

        legend_x = int(x + size + 24)
        legend_y = max(12, y)
        painter.setPen(QColor(C_TEXT_PRI))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)

        for idx, (label, value) in enumerate(self._data[:6]):
            cy = legend_y + idx * 26
            color = QColor(CHART_COLORS[idx % len(CHART_COLORS)])
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(legend_x, cy + 3, 12, 12, 3, 3)

            painter.setPen(QColor(C_TEXT_PRI))
            pct = (value / total) * 100
            painter.drawText(
                legend_x + 20,
                cy,
                max(120, w - legend_x - 26),
                20,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                f"{label} - {pct:.0f}%",
            )


class ChartCard(QFrame):
    def __init__(self, title: str, subtitle: str, chart_type: ChartType = "bar", parent=None):
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._chart = SimpleChartWidget(chart_type)
        self._subtitle_lbl: QLabel | None = None
        self._build()

    def _build(self):
        self.setObjectName("ChartCard")
        self.setMinimumHeight(310)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame#ChartCard {{
                background: {C_WHITE};
                border-radius: {RADIUS}px;
                border: 1.5px solid {C_BORDER};
            }}
        """)
        _apply_card_shadow(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        title = QLabel(self._title)
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 16px;
            font-weight: 800;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        root.addWidget(title)

        self._subtitle_lbl = QLabel(self._subtitle)
        self._subtitle_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        root.addWidget(self._subtitle_lbl)

        root.addWidget(self._chart)

    def set_data(self, data: list[tuple[str, float]], subtitle: str | None = None):
        self._chart.set_data(data)
        if subtitle and self._subtitle_lbl:
            self._subtitle_lbl.setText(subtitle)


class PieChartCard(QFrame):
    def __init__(self, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        self._chart = PieChartWidget()
        self._subtitle_lbl: QLabel | None = None
        self._title = title
        self._subtitle = subtitle
        self._build()

    def _build(self):
        self.setObjectName("PieChartCard")
        self.setMinimumHeight(310)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame#PieChartCard {{
                background: {C_WHITE};
                border-radius: {RADIUS}px;
                border: 1.5px solid {C_BORDER};
            }}
        """)
        _apply_card_shadow(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        title = QLabel(self._title)
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 16px;
            font-weight: 800;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        root.addWidget(title)

        self._subtitle_lbl = QLabel(self._subtitle)
        self._subtitle_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 12px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        root.addWidget(self._subtitle_lbl)

        root.addWidget(self._chart)

    def set_data(self, data: list[tuple[str, float]], subtitle: str | None = None):
        self._chart.set_data(data)
        if subtitle and self._subtitle_lbl:
            self._subtitle_lbl.setText(subtitle)


# ─────────────────────────────────────────────────────────────────────────────
# Cards / Lists
# ─────────────────────────────────────────────────────────────────────────────
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
        self.setMinimumHeight(116)
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
        top.addWidget(title)
        top.addStretch()

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


class ReportListItem(QFrame):
    def __init__(self, title: str, subtitle: str, value: str, color: str = C_ACCENT, parent=None):
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._value = value
        self._color = color
        self._build()

    def _build(self):
        self.setObjectName("ReportListItem")
        self.setFixedHeight(56)
        self.setStyleSheet(f"""
            QFrame#ReportListItem {{
                background: {C_ROW_ALT};
                border-radius: 10px;
                border: 1px solid {C_BORDER};
            }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 7, 12, 7)
        root.setSpacing(10)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(1)

        title = QLabel(self._title)
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
        subtitle.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 10px;
            color: {C_TEXT_SEC};
            background: transparent;
            border: none;
        """)
        text_col.addWidget(subtitle)

        root.addLayout(text_col, stretch=1)

        value = QLabel(self._value)
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value.setMinimumWidth(78)
        value.setFixedHeight(26)
        value.setStyleSheet(f"""
            background: {C_WHITE};
            color: {self._color};
            border: 1px solid {self._color};
            border-radius: 7px;
            font-family: 'Segoe UI';
            font-size: 10px;
            font-weight: 700;
            padding: 0 8px;
        """)
        root.addWidget(value)


class ReportListCard(QFrame):
    def __init__(self, title: str, icon: str, empty_text: str, parent=None):
        super().__init__(parent)
        self._title = title
        self._icon = icon
        self._empty_text = empty_text
        self._items_layout: QVBoxLayout | None = None
        self._build()

    def _build(self):
        self.setObjectName("ReportListCard")
        self.setMinimumHeight(258)
        self.setMaximumHeight(258)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame#ReportListCard {{
                background: {C_WHITE};
                border-radius: {RADIUS}px;
                border: 1.5px solid {C_BORDER};
            }}
        """)
        _apply_card_shadow(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

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
        self._items_layout.setSpacing(6)
        root.addLayout(self._items_layout)

        self.set_items([])

    def set_items(self, items: list[tuple[str, str, str, str]], max_items: int = 3):
        if self._items_layout is None:
            return

        _clear_layout(self._items_layout)
        items = items[:max_items]

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
        else:
            for title, subtitle, value, color in items:
                self._items_layout.addWidget(ReportListItem(title, subtitle, value, color))

        self._items_layout.addStretch()
        self.update()


# ─────────────────────────────────────────────────────────────────────────────
# Reports Page
# ─────────────────────────────────────────────────────────────────────────────
class ReportsPage(QWidget):
    def __init__(self, user: dict | None = None, parent=None):
        super().__init__(parent)
        self._user = user or {}
        self._active_period: Period = "daily"

        self._products: list[Product] = []
        self._sales: list[Sales] = []
        self._sales_details: list[SalesDetail] = []
        self._purchases: list[Purchase] = []
        self._purchase_details: list[PurchaseDetail] = []
        self._receivables: list[Receivables] = []

        self._period_buttons: dict[Period, QPushButton] = {}

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"background: {C_BG};")

        self._build_ui()
        self._load_data()

        # Auto-refresh saat ada transaksi baru dari halaman Kasir
        sales_signals.sales_completed.connect(self._on_sales_completed)

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
        self._build_main_charts(self._content_layout)
        self._build_secondary_charts(self._content_layout)
        self._build_list_section(self._content_layout)

        scroll.setWidget(content)
        root.addWidget(scroll)

    def _build_header(self, parent_layout: QVBoxLayout):
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title_col.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Laporan")
        title.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size: 24px;
            font-weight: 800;
            color: {C_TEXT_PRI};
            background: transparent;
            border: none;
        """)
        title_col.addWidget(title)

        subtitle = QLabel("Ringkasan performa penjualan, produk, pembayaran, stok, dan pembelian")
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

        pdf_btn = QPushButton("Generate PDF")
        pdf_btn.setFixedHeight(40)
        pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pdf_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_SUCCESS};
                color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 700;
                border-radius: 10px;
                border: none;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: #219653;
            }}
        """)
        pdf_btn.clicked.connect(self._export_pdf_report)
        header.addWidget(pdf_btn)

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

        self._revenue_card = MetricCard("Omset", "Rp 0", "Total penjualan", "💰", C_ACCENT)
        self._order_card = MetricCard("Transaksi", "0", "Total order", "🧾", C_SUCCESS)
        self._items_sold_card = MetricCard("Item Terjual", "0", "Total quantity", "📦", C_ACCENT)
        self._avg_order_card = MetricCard("Rata-rata Order", "Rp 0", "Omset / transaksi", "📊", C_WARNING)

        cards = [self._revenue_card, self._order_card, self._items_sold_card, self._avg_order_card]
        for i, card in enumerate(cards):
            grid.addWidget(card, 0, i)
            grid.setColumnStretch(i, 1)

        parent_layout.addLayout(grid)

    def _build_main_charts(self, parent_layout: QVBoxLayout):
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        self._revenue_chart = ChartCard("Tren Omset", "Omset berdasarkan periode aktif", "line")
        self._payment_pie_chart = PieChartCard("Komposisi Pembayaran", "Distribusi metode pembayaran")

        grid.addWidget(self._revenue_chart, 0, 0)
        grid.addWidget(self._payment_pie_chart, 0, 1)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 2)

        parent_layout.addLayout(grid)

    def _build_secondary_charts(self, parent_layout: QVBoxLayout):
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        self._transaction_chart = ChartCard("Jumlah Transaksi", "Jumlah order berdasarkan periode aktif", "bar")
        self._product_chart = ChartCard("Produk Terjual", "Top produk berdasarkan quantity terjual", "bar")
        self._category_chart = ChartCard("Penjualan per Kategori", "Quantity terjual berdasarkan kategori produk", "bar")
        self._purchase_chart = ChartCard("Pembelian Stok", "Total pembelian stok berdasarkan periode aktif", "line")

        grid.addWidget(self._transaction_chart, 0, 0)
        grid.addWidget(self._product_chart, 0, 1)
        grid.addWidget(self._category_chart, 1, 0)
        grid.addWidget(self._purchase_chart, 1, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        parent_layout.addLayout(grid)

    def _build_list_section(self, parent_layout: QVBoxLayout):
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        self._top_products_card = ReportListCard("Barang Terjual Terbanyak", "🔥", "Belum ada produk terjual")
        self._low_stock_card = ReportListCard("Stok Perlu Dicek", "⚠️", "Stok produk masih aman")
        self._receivables_card = ReportListCard("Piutang Customer", "💳", "Belum ada piutang")
        self._summary_card = ReportListCard("Insight Ringkas", "💡", "Belum ada insight")

        grid.addWidget(self._top_products_card, 0, 0)
        grid.addWidget(self._low_stock_card, 0, 1)
        grid.addWidget(self._receivables_card, 1, 0)
        grid.addWidget(self._summary_card, 1, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        parent_layout.addLayout(grid)

    # ── Data / Refresh ────────────────────────────────────────────────────────
    def _load_data(self):
        try:
            self._products = ProductController.fetch()
            self._sales = SalesController.fetch()
            self._sales_details = SalesDetailController.fetch()
            self._purchases = PurchaseController.fetch()
            self._purchase_details = PurchaseDetailController.fetch()
            self._receivables = ReceivablesController.fetch()
            self._refresh_report()
        except Exception as e:
            Toast.show_toast(f"Gagal memuat laporan: {str(e)}", "error", self)

    def _on_sales_completed(self, sales_id: int):
        """Dipanggil otomatis saat transaksi selesai dari halaman Kasir."""
        self._load_data()

    def _set_period(self, period: Period):
        self._active_period = period
        self._refresh_period_button_styles()
        self._refresh_report()

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

    def _refresh_report(self):
        period_sales = self._filtered_sales()
        period_details = self._filtered_sales_details(period_sales)
        period_purchases = self._filtered_purchases()
        period_purchase_details = self._filtered_purchase_details(period_purchases)

        self._refresh_metrics(period_sales, period_details)
        self._refresh_charts(period_sales, period_details, period_purchases)
        self._refresh_lists(period_sales, period_details, period_purchases)

    def _filtered_sales(self) -> list[Sales]:
        return [sale for sale in self._sales if _same_period(sale.time, self._active_period)]

    def _filtered_sales_details(self, sales: list[Sales]) -> list[SalesDetail]:
        sales_ids = {int(sale.id) for sale in sales}
        return [detail for detail in self._sales_details if int(detail.sales_id) in sales_ids]

    def _filtered_purchases(self) -> list[Purchase]:
        return [purchase for purchase in self._purchases if _same_period(purchase.time, self._active_period)]

    def _filtered_purchase_details(self, purchases: list[Purchase]) -> list[PurchaseDetail]:
        purchase_ids = {int(purchase.id) for purchase in purchases}
        return [detail for detail in self._purchase_details if int(detail.purchase_id) in purchase_ids]

    def _refresh_metrics(self, period_sales: list[Sales], period_details: list[SalesDetail]):
        revenue = sum(float(sale.total_price or 0) for sale in period_sales)
        tx_count = len(period_sales)
        items_sold = sum(int(detail.quantity or 0) for detail in period_details)
        avg_order = revenue / tx_count if tx_count else 0

        label = _period_label(self._active_period)
        self._revenue_card.set_values(_format_price(revenue), label)
        self._order_card.set_values(_format_number(tx_count), f"Order {label.lower()}")
        self._items_sold_card.set_values(_format_number(items_sold), "Total barang keluar")
        self._avg_order_card.set_values(_format_price(avg_order), "Rata-rata nilai transaksi")

    def _refresh_charts(self, period_sales: list[Sales], period_details: list[SalesDetail], period_purchases: list[Purchase]):
        label = _period_label(self._active_period)
        payment_data = self._payment_series(period_sales)

        self._revenue_chart.set_data(self._revenue_series(period_sales), f"Omset {label.lower()}")
        self._payment_pie_chart.set_data(payment_data, "Distribusi metode pembayaran")
        self._transaction_chart.set_data(self._transaction_series(period_sales), f"Jumlah order {label.lower()}")
        self._product_chart.set_data(self._top_product_series(period_details), "Top 8 produk berdasarkan quantity terjual")
        self._category_chart.set_data(self._category_series(period_details), "Quantity terjual per kategori")
        self._purchase_chart.set_data(self._purchase_series(period_purchases), f"Pembelian stok {label.lower()}")

    # ── Series builders ───────────────────────────────────────────────────────
    def _time_labels(self) -> tuple[list[str], dict]:
        now = datetime.now()

        if self._active_period == "daily":
            labels = [f"{hour:02d}" for hour in range(24)]
            return labels, {hour: f"{hour:02d}" for hour in range(24)}

        days_back = 6 if self._active_period == "weekly" else 29
        days = [
            (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            for i in range(days_back, -1, -1)
        ]
        labels = [day.strftime("%d/%m") for day in days]
        return labels, {day.date(): label for day, label in zip(days, labels)}

    def _label_for_dt(self, dt: datetime, mapper: dict) -> str | None:
        if self._active_period == "daily":
            return mapper.get(dt.hour)
        return mapper.get(dt.date())

    def _revenue_series(self, period_sales: list[Sales]) -> list[tuple[str, float]]:
        labels, mapper = self._time_labels()
        buckets = {label: 0.0 for label in labels}

        for sale in period_sales:
            dt = _parse_datetime(sale.time)
            label = self._label_for_dt(dt, mapper) if dt else None
            if label:
                buckets[label] += float(sale.total_price or 0)

        return [(label, buckets[label]) for label in labels]

    def _transaction_series(self, period_sales: list[Sales]) -> list[tuple[str, float]]:
        labels, mapper = self._time_labels()
        buckets = {label: 0.0 for label in labels}

        for sale in period_sales:
            dt = _parse_datetime(sale.time)
            label = self._label_for_dt(dt, mapper) if dt else None
            if label:
                buckets[label] += 1

        return [(label, buckets[label]) for label in labels]

    def _purchase_series(self, period_purchases: list[Purchase]) -> list[tuple[str, float]]:
        labels, mapper = self._time_labels()
        buckets = {label: 0.0 for label in labels}

        for purchase in period_purchases:
            dt = _parse_datetime(purchase.time)
            label = self._label_for_dt(dt, mapper) if dt else None
            if label:
                buckets[label] += float(purchase.total_amount or 0)

        return [(label, buckets[label]) for label in labels]

    def _top_product_series(self, period_details: list[SalesDetail]) -> list[tuple[str, float]]:
        product_map = {int(product.id): product for product in self._products}
        qty_by_product: dict[int, int] = defaultdict(int)

        for detail in period_details:
            qty_by_product[int(detail.product_id)] += int(detail.quantity or 0)

        data: list[tuple[str, float]] = []
        for product_id, qty in sorted(qty_by_product.items(), key=lambda item: item[1], reverse=True)[:8]:
            product = product_map.get(product_id)
            if product:
                name = product.name if len(product.name) <= 12 else product.name[:11] + "..."
                data.append((name, float(qty)))

        return data

    def _category_series(self, period_details: list[SalesDetail]) -> list[tuple[str, float]]:
        product_map = {int(product.id): product for product in self._products}
        qty_by_category: dict[str, int] = defaultdict(int)

        for detail in period_details:
            product = product_map.get(int(detail.product_id))
            if product:
                category = product.category or "Lainnya"
                qty_by_category[category] += int(detail.quantity or 0)

        order = ["Makanan", "Minuman", "Snack", "Sembako", "Lainnya"]
        return [(category, float(qty_by_category.get(category, 0))) for category in order]

    def _payment_series(self, period_sales: list[Sales]) -> list[tuple[str, float]]:
        counts: dict[str, int] = defaultdict(int)
        
        # Payment label mapping - hanya Tunai dan QRIS
        payment_labels = {
            "tunai": "Tunai",
            "qris": "QRIS",
            None: "—",
        }

        for sale in period_sales:
            payment = (sale.payment or "").strip().lower() if sale.payment else None
            counts[payment] += 1

        order = ["tunai", "qris"]
        result: list[tuple[str, float]] = []
        
        for payment_key in order:
            label = payment_labels.get(payment_key, payment_key.upper() if payment_key else "—")
            count = counts.get(payment_key, 0)
            if count > 0:  # Hanya tampilkan jika ada transaksi
                result.append((label, float(count)))
        
        return result

    # ── List builders ─────────────────────────────────────────────────────────
    def _refresh_lists(self, period_sales: list[Sales], period_details: list[SalesDetail], period_purchases: list[Purchase]):
        self._top_products_card.set_items(self._top_product_items(period_details))
        self._low_stock_card.set_items(self._low_stock_items())
        self._receivables_card.set_items(self._receivable_items())
        self._summary_card.set_items(self._summary_items(period_sales, period_details, period_purchases))

    def _top_product_items(self, period_details: list[SalesDetail]) -> list[tuple[str, str, str, str]]:
        product_map = {int(product.id): product for product in self._products}
        qty_by_product: dict[int, int] = defaultdict(int)

        for detail in period_details:
            qty_by_product[int(detail.product_id)] += int(detail.quantity or 0)

        items: list[tuple[str, str, str, str]] = []
        for product_id, qty in sorted(qty_by_product.items(), key=lambda item: item[1], reverse=True)[:5]:
            product = product_map.get(product_id)
            if not product:
                continue

            estimate = float(product.price or 0) * qty
            items.append((
                product.name,
                f"{product.category or 'Tanpa kategori'} - Est. omset {_format_price(estimate)}",
                f"{_format_number(qty)} item",
                C_SUCCESS,
            ))

        return items

    def _low_stock_items(self) -> list[tuple[str, str, str, str]]:
        products = sorted(
            [product for product in self._products if int(product.stock or 0) < LOW_STOCK_THRESHOLD],
            key=lambda product: (int(product.stock or 0), str(product.name).lower()),
        )[:5]

        items: list[tuple[str, str, str, str]] = []
        for product in products:
            stock = int(product.stock or 0)
            badge = "Habis" if stock == 0 else f"Sisa {stock}"
            color = C_DANGER if stock == 0 else C_WARNING

            items.append((
                product.name,
                f"{product.category or 'Tanpa kategori'} - SKU {product.sku or '-'}",
                badge,
                color,
            ))

        return items

    def _receivable_items(self) -> list[tuple[str, str, str, str]]:
        unpaid = [
            receivable
            for receivable in self._receivables
            if str(receivable.status).lower() != "paid"
            and float(receivable.total_amount or 0) > float(receivable.amount_paid or 0)
        ]

        ranked = sorted(
            unpaid,
            key=lambda item: float(item.total_amount or 0) - float(item.amount_paid or 0),
            reverse=True,
        )[:5]

        items: list[tuple[str, str, str, str]] = []
        for receivable in ranked:
            remaining = float(receivable.total_amount or 0) - float(receivable.amount_paid or 0)
            items.append((
                f"Sales #{receivable.sales_id}",
                f"Due {receivable.due_date or '-'} - Status {receivable.status}",
                _format_price(remaining),
                C_DANGER,
            ))

        return items

    def _summary_items(self, period_sales: list[Sales], period_details: list[SalesDetail], period_purchases: list[Purchase]) -> list[tuple[str, str, str, str]]:
        revenue = sum(float(sale.total_price or 0) for sale in period_sales)
        purchases = sum(float(purchase.total_amount or 0) for purchase in period_purchases)
        tx_count = len(period_sales)
        items_sold = sum(int(detail.quantity or 0) for detail in period_details)
        avg_order = revenue / tx_count if tx_count else 0

        items: list[tuple[str, str, str, str]] = [
            ("Periode laporan", "Filter aktif yang sedang digunakan", _period_label(self._active_period), C_ACCENT),
            ("Estimasi margin kasar", "Omset dikurangi pembelian stok periode ini", _format_price(revenue - purchases), C_SUCCESS if revenue >= purchases else C_DANGER),
            ("Rata-rata transaksi", f"{_format_number(tx_count)} transaksi - {_format_number(items_sold)} item", _format_price(avg_order), C_ACCENT),
        ]

        return items

    # ── PDF Export ────────────────────────────────────────────────────────────
    def _export_pdf_report(self):
        try:
            default_name = f"laporan_transaksi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                "Simpan Laporan PDF",
                default_name,
                "PDF Files (*.pdf)",
            )

            if not output_path:
                return

            if not output_path.lower().endswith(".pdf"):
                output_path += ".pdf"

            self._generate_pdf(output_path)
            Toast.show_toast(f"Laporan berhasil dibuat: {output_path}", "success", self)
        except Exception as e:
            Toast.show_toast(f"Gagal membuat PDF: {str(e)}", "error", self)

    def _generate_pdf(self, output_path: str):
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
                PageBreak,
            )
        except ImportError as exc:
            raise RuntimeError("Library reportlab belum terinstall. Jalankan: pip install reportlab") from exc

        period_sales = self._filtered_sales()
        period_details = self._filtered_sales_details(period_sales)

        start, end = _period_date_range(self._active_period)
        revenue = sum(float(sale.total_price or 0) for sale in period_sales)
        tx_count = len(period_sales)
        items_sold = sum(int(detail.quantity or 0) for detail in period_details)
        avg_order = revenue / tx_count if tx_count else 0

        payment_breakdown = self._payment_series(period_sales)
        top_products = self._top_product_items(period_details)[:10]

        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(A4),
            rightMargin=1.2 * cm,
            leftMargin=1.2 * cm,
            topMargin=1.1 * cm,
            bottomMargin=1.1 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1A1D2E"),
            spaceAfter=10,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#6B6F80"),
            spaceAfter=10,
        )
        section_style = ParagraphStyle(
            "SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=14,
            textColor=colors.HexColor("#1A1D2E"),
            spaceBefore=8,
            spaceAfter=6,
        )

        elements = []

        elements.append(Paragraph("Laporan Transaksi Warung+", title_style))
        elements.append(Paragraph(
            f"Periode: {start.strftime('%d/%m/%Y %H:%M')} sampai {end.strftime('%d/%m/%Y %H:%M')} "
            f"({ _period_label(self._active_period) })",
            subtitle_style,
        ))

        summary_data = [
            ["Ringkasan", "Nilai"],
            ["Total Omset", _format_price(revenue)],
            ["Total Transaksi", _format_number(tx_count)],
            ["Total Item Terjual", _format_number(items_sold)],
            ["Rata-rata Nilai Transaksi", _format_price(avg_order)],
        ]

        summary_table = Table(summary_data, colWidths=[7 * cm, 6 * cm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F6EF7")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E4E6EE")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FC")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("Rincian Metode Pembayaran", section_style))
        payment_data = [["Metode", "Jumlah Transaksi"]]
        payment_data.extend([[label, _format_number(value)] for label, value in payment_breakdown if value > 0])

        if len(payment_data) == 1:
            payment_data.append(["-", "0"])

        payment_table = Table(payment_data, colWidths=[7 * cm, 6 * cm])
        payment_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF1FE")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1A1D2E")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E4E6EE")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FC")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(payment_table)
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("Barang Terjual Terbanyak", section_style))
        top_product_data = [["Produk", "Keterangan", "Terjual"]]
        for title, subtitle, value, _color in top_products:
            top_product_data.append([title, subtitle, value])

        if len(top_product_data) == 1:
            top_product_data.append(["-", "Belum ada data produk terjual", "0"])

        top_product_table = Table(top_product_data, colWidths=[6 * cm, 11 * cm, 4 * cm])
        top_product_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF1FE")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E4E6EE")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FC")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(top_product_table)
        elements.append(PageBreak())

        elements.append(Paragraph("Daftar Transaksi", section_style))

        product_count_by_sale: dict[int, int] = defaultdict(int)
        discount_by_sale: dict[int, float] = defaultdict(float)

        for detail in self._sales_details:
            product_count_by_sale[int(detail.sales_id)] += int(detail.quantity or 0)
            discount_by_sale[int(detail.sales_id)] += float(detail.discount or 0)

        # Payment label mapping - hanya Tunai dan QRIS
        payment_labels = {
            "tunai": "Tunai",
            "qris": "QRIS",
            None: "—",
        }

        tx_data = [["No", "Tanggal", "Sales ID", "Payment", "Item", "Diskon", "Dibayar", "Total"]]

        sorted_sales = sorted(
            period_sales,
            key=lambda sale: _parse_datetime(sale.time) or datetime.min,
            reverse=True,
        )

        for idx, sale in enumerate(sorted_sales, start=1):
            dt = _parse_datetime(sale.time)
            date_text = dt.strftime("%d/%m/%Y %H:%M") if dt else str(sale.time)
            
            payment_key = (sale.payment or "").strip().lower() if sale.payment else None
            payment_label = payment_labels.get(payment_key, str(payment_key).upper() if payment_key else "—")

            tx_data.append([
                str(idx),
                date_text,
                f"#{sale.id}",
                payment_label,
                _format_number(product_count_by_sale.get(int(sale.id), 0)),
                _format_price(discount_by_sale.get(int(sale.id), 0)),
                _format_price(sale.paid_amount or 0),
                _format_price(sale.total_price or 0),
            ])

        if len(tx_data) == 1:
            tx_data.append(["-", "-", "-", "-", "-", "-", "-", "-"])

        tx_table = Table(
            tx_data,
            repeatRows=1,
            colWidths=[1.1 * cm, 3.7 * cm, 2.0 * cm, 2.3 * cm, 1.5 * cm, 2.6 * cm, 2.8 * cm, 2.8 * cm],
        )
        tx_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F6EF7")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.3),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E4E6EE")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FC")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (4, 1), (-1, -1), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(tx_table)
        elements.append(Spacer(1, 12))

        total_paid = sum(float(sale.paid_amount or 0) for sale in period_sales)
        total_discount = sum(discount_by_sale.values())
        total_items = sum(product_count_by_sale.values())

        elements.append(Paragraph("Perhitungan Omset", section_style))
        calc_data = [
            ["Keterangan", "Nilai"],
            ["Total transaksi", _format_number(tx_count)],
            ["Total item terjual", _format_number(total_items)],
            ["Total diskon item", _format_price(total_discount)],
            ["Total dibayar", _format_price(total_paid)],
            ["Total omset", _format_price(revenue)],
            ["Rata-rata transaksi", _format_price(avg_order)],
        ]

        calc_table = Table(calc_data, colWidths=[8 * cm, 6 * cm])
        calc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#27AE60")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E4E6EE")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FC")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(calc_table)

        doc.build(elements)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ReportsPage(user={"id": 1, "name": "Admin"})
    window.resize(1280, 820)
    window.show()
    sys.exit(app.exec())