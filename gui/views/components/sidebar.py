# views/widgets/sidebar_widget.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal, QByteArray
from PyQt6.QtGui import QColor, QPainter, QPixmap, QPalette, QImage
from PyQt6.QtSvg import QSvgRenderer

# ── Nav items ─────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    {"key": "dashboard",  "label": "Dashboard",  "icon": "grid"},
    {"key": "products",   "label": "Produk",      "icon": "box"},
    {"key": "categories", "label": "Kategori",    "icon": "tag"},
    {"key": "cashier",    "label": "Kasir",       "icon": "shopping-cart"},
    {"key": "reports",    "label": "Laporan",     "icon": "bar-chart-2"},
    {"key": "users",      "label": "Pengguna",    "icon": "users"},
]

# ── SVG icons ─────────────────────────────────────────────────────────────────
ICONS = {
    "grid":          """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>""",
    "box":           """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>""",
    "tag":           """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>""",
    "shopping-cart": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>""",
    "bar-chart-2":   """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>""",
    "users":         """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",
    "log-out":       """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>""",
}

# ── Palette ───────────────────────────────────────────────────────────────────
COLOR_BG         = "#FAFAF8"
COLOR_ACTIVE_BG  = "#EEF0FD"
COLOR_HOVER_BG   = "#F1EFE8"
COLOR_ACCENT     = "#4F6EF7"
COLOR_TEXT       = "#888780"
COLOR_TEXT_ACT   = "#4F6EF7"   # biru sama dengan accent — sesuai screenshot
COLOR_TEXT_HOVER = "#5F5E5A"
COLOR_DIVIDER    = "#DDD9D2"
COLOR_AVATAR_BG  = "#F1EFE8"
COLOR_LOGOUT     = "#C0392B"
COLOR_LOGOUT_HOV = "#962d22"


# ── Helper ────────────────────────────────────────────────────────────────────
def _make_pixmap(key: str, color: str, size: int = 18) -> QPixmap:
    """Render SVG to pixmap."""
    svg = ICONS.get(key, "").replace('stroke="currentColor"', f'stroke="{color}"')
    
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(px)
    try:
        r = QSvgRenderer(QByteArray(svg.encode()))
        r.render(painter)
    finally:
        if painter.isActive():
            painter.end()
    
    return px


# ── NavItem ───────────────────────────────────────────────────────────────────
class NavItem(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, key: str, label: str, icon: str, active: bool = False):
        super().__init__()
        self.key       = key
        self._active   = active
        self._hovered  = False
        self._icon_key = icon
        self._pixmap_cache: dict[str, QPixmap] = {}  # Cache pixmaps by color

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        lay = QHBoxLayout(self)
        # ── Margin kiri 8px untuk indicator bar 3px + gap 8px = total 19px ke icon
        lay.setContentsMargins(8, 0, 12, 0)
        lay.setSpacing(0)

        # Indicator bar 3px di kiri (hanya active)
        self._bar = QFrame()
        self._bar.setFixedSize(3, 20)
        lay.addWidget(self._bar)
        lay.addSpacing(10)

        # Icon
        self._icon_lbl = QLabel()
        self._icon_lbl.setFixedSize(18, 18)
        self._icon_lbl.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(self._icon_lbl)
        lay.addSpacing(10)

        # Label
        self._lbl = QLabel(label)
        self._lbl.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(self._lbl)
        lay.addStretch()

        self._refresh()

    def _get_pixmap(self, color: str) -> QPixmap:
        """Get cached pixmap or create new one"""
        if color not in self._pixmap_cache:
            self._pixmap_cache[color] = _make_pixmap(self._icon_key, color)
        return self._pixmap_cache[color]

    def _refresh(self):
        if self._active:
            self.setStyleSheet(f"background: {COLOR_ACTIVE_BG}; border-radius: 8px;")
            self._bar.setStyleSheet(f"background: {COLOR_ACCENT}; border-radius: 2px;")
            self._icon_lbl.setPixmap(self._get_pixmap(COLOR_ACCENT))
            self._lbl.setStyleSheet(f"""
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 600;
                color: {COLOR_TEXT_ACT}; background: transparent; border: none;
            """)
        elif self._hovered:
            self.setStyleSheet(f"background: {COLOR_HOVER_BG}; border-radius: 8px;")
            self._bar.setStyleSheet("background: transparent;")
            self._icon_lbl.setPixmap(self._get_pixmap(COLOR_TEXT_HOVER))
            self._lbl.setStyleSheet(f"""
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 500;
                color: {COLOR_TEXT_HOVER}; background: transparent; border: none;
            """)
        else:
            self.setStyleSheet("background: transparent; border-radius: 8px;")
            self._bar.setStyleSheet("background: transparent;")
            self._icon_lbl.setPixmap(self._get_pixmap(COLOR_TEXT))
            self._lbl.setStyleSheet(f"""
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 400;
                color: {COLOR_TEXT}; background: transparent; border: none;
            """)

    def set_active(self, v: bool):
        self._active = v
        self._refresh()

    def enterEvent(self, e):
        if not self._active:
            self._hovered = True
            self._refresh()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hovered = False
        self._refresh()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        self.clicked.emit(self.key)


# ── LogoutButton ──────────────────────────────────────────────────────────────
class LogoutButton(QWidget):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self._hovered = False
        self._pixmap_cache: dict[str, QPixmap] = {}  # Cache pixmaps by color

        lay = QHBoxLayout(self)
        lay.setContentsMargins(21, 0, 12, 0)   # sejajar dengan icon nav (8+3+10=21)
        lay.setSpacing(10)

        self._icon_lbl = QLabel()
        self._icon_lbl.setFixedSize(18, 18)
        self._icon_lbl.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(self._icon_lbl)

        self._lbl = QLabel("Keluar")
        lay.addWidget(self._lbl)
        lay.addStretch()

        self._refresh()

    def _get_pixmap(self, color: str) -> QPixmap:
        """Get cached pixmap or create new one"""
        if color not in self._pixmap_cache:
            self._pixmap_cache[color] = _make_pixmap("log-out", color)
        return self._pixmap_cache[color]

    def _refresh(self):
        c  = COLOR_LOGOUT_HOV if self._hovered else COLOR_LOGOUT
        bg = "#FDF0EC"        if self._hovered else "transparent"
        self.setStyleSheet(f"background: {bg}; border-radius: 8px;")
        self._icon_lbl.setPixmap(self._get_pixmap(c))
        self._lbl.setStyleSheet(f"""
            font-family: 'Segoe UI'; font-size: 13px; font-weight: 500;
            color: {c}; background: transparent; border: none;
        """)

    def enterEvent(self, e):
        self._hovered = True;  self._refresh(); super().enterEvent(e)

    def leaveEvent(self, e):
        self._hovered = False; self._refresh(); super().leaveEvent(e)

    def mousePressEvent(self, e):
        self.clicked.emit()


# ── SidebarWidget ─────────────────────────────────────────────────────────────
class SidebarWidget(QWidget):
    nav_changed      = pyqtSignal(str)
    logout_requested = pyqtSignal()

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self._user       = user
        self._active_key = "dashboard"
        self._nav_items: dict[str, NavItem] = {}

        self.setFixedWidth(220)

        # Background reliable via QPalette
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(COLOR_BG))
        self.setPalette(pal)

        self._build_ui()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(COLOR_BG))
        p.setPen(QColor(COLOR_DIVIDER))
        p.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        p.end()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 0, 12, 16)
        root.setSpacing(0)

        # ── Logo ──────────────────────────────────────────────────────────────
        logo_wrap = QWidget()
        logo_wrap.setFixedHeight(64)
        logo_wrap.setStyleSheet("background: transparent;")
        ll = QHBoxLayout(logo_wrap)
        ll.setContentsMargins(8, 0, 0, 0)

        logo = QLabel()
        logo.setText("Warung<span style='color:#4F6EF7'>+</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("""
            font-family: 'Segoe UI'; font-size: 20px; font-weight: 700;
            letter-spacing: 1px; color: #1B1B1B;
            background: transparent; border: none;
        """)
        ll.addWidget(logo)
        ll.addStretch()
        root.addWidget(logo_wrap)

        # Divider bawah logo
        root.addWidget(self._divider())
        root.addSpacing(10)

        # ── Nav items ─────────────────────────────────────────────────────────
        for item in NAV_ITEMS:
            is_active = item["key"] == self._active_key
            nav = NavItem(item["key"], item["label"], item["icon"], active=is_active)
            nav.clicked.connect(self._on_nav_clicked)
            self._nav_items[item["key"]] = nav
            root.addWidget(nav)
            root.addSpacing(4)   # jarak antar item sesuai screenshot

        root.addStretch()

        # Divider atas user card
        root.addWidget(self._divider())
        root.addSpacing(12)

        # ── User card ─────────────────────────────────────────────────────────
        root.addWidget(self._build_user_card())
        root.addSpacing(6)

        # ── Logout ────────────────────────────────────────────────────────────
        logout = LogoutButton()
        logout.clicked.connect(self.logout_requested)
        root.addWidget(logout)

    def _divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {COLOR_DIVIDER}; border: none;")
        return line

    def _build_user_card(self) -> QWidget:
        card = QWidget()
        card.setFixedHeight(56)
        card.setStyleSheet(f"background: {COLOR_AVATAR_BG}; border-radius: 10px;")

        lay = QHBoxLayout(card)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(10)

        # Avatar circle
        initials = self._user.get("initials", "??")
        avatar   = QLabel(initials)
        avatar.setFixedSize(34, 34)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background: {COLOR_ACCENT}; color: #FFFFFF;
            font-family: 'Segoe UI'; font-size: 12px; font-weight: 700;
            border-radius: 17px; border: none;
        """)

        # Text info
        info = QVBoxLayout()
        info.setSpacing(0)
        info.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(self._user.get("name", "User"))
        name_lbl.setFixedHeight(16)
        name_lbl.setStyleSheet("""
            font-family: 'Segoe UI'; font-size: 12px; font-weight: 600;
            color: #1B1B1B; background: transparent; border: none;
            padding: 0px; margin: 0px;
        """)

        role_lbl = QLabel(self._user.get("role", "Admin"))
        role_lbl.setFixedHeight(14)
        role_lbl.setStyleSheet("""
            font-family: 'Segoe UI'; font-size: 10px; font-weight: 400;
            color: #888780; background: transparent; border: none;
            padding: 0px; margin: 0px;
        """)

        info.addWidget(name_lbl)
        info.addWidget(role_lbl)

        lay.addWidget(avatar)
        lay.addLayout(info)
        lay.addStretch()

        return card

    def _on_nav_clicked(self, key: str):
        if key == self._active_key:
            return
        if self._active_key in self._nav_items:
            self._nav_items[self._active_key].set_active(False)
        self._active_key = key
        self._nav_items[key].set_active(True)
        self.nav_changed.emit(key)

    def set_active(self, key: str):
        self._on_nav_clicked(key)