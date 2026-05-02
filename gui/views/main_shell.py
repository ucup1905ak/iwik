# views/main_shell.py

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QStackedWidget, QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal

from gui.views.components.sidebar import SidebarWidget
from gui.views.screens.product_page import ProductPage

ANIM_DURATION = 160

# ── Placeholder page untuk menu lain ─────────────────────────────────────────
class PlaceholderPage(QWidget):
    def __init__(self, title: str, emoji: str = "🚧"):
        super().__init__()
        self.setStyleSheet("background: #F4F5F9;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        emoji_lbl = QLabel(emoji)
        emoji_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emoji_lbl.setStyleSheet("font-size: 52px; background: transparent;")

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet("""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: 700;
            color: #1A1D2E;
            background: transparent;
        """)

        sub_lbl = QLabel("Halaman ini sedang dalam pengembangan.")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setStyleSheet("""
            font-family: 'Segoe UI';
            font-size: 13px;
            color: #6B6F80;
            background: transparent;
        """)

        layout.addWidget(emoji_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(sub_lbl)


# ═════════════════════════════════════════════════════════════════════════════
# Main Shell
# ═════════════════════════════════════════════════════════════════════════════
class MainShell(QWidget):
    logout_requested = pyqtSignal()

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self._user = user
        self._animating = False

        self.setStyleSheet("background: #F4F5F9;")
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────────────
        self._sidebar = SidebarWidget(user=self._user)
        self._sidebar.nav_changed.connect(self._navigate_to)
        self._sidebar.logout_requested.connect(self.logout_requested.emit)
        root.addWidget(self._sidebar)

        # ── Content area ──────────────────────────────────────────────────────
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: #F4F5F9;")
        root.addWidget(self._stack, stretch=1)

        # ── Register pages ────────────────────────────────────────────────────
        self._pages: dict[str, QWidget] = {}

        self._add_page("dashboard",  PlaceholderPage("Dashboard", "📊"))
        self._add_page("products",   ProductPage(user=self._user))
        self._add_page("categories", PlaceholderPage("Kategori", "🏷️"))
        self._add_page("cashier",    PlaceholderPage("Kasir", "🛒"))
        self._add_page("reports",    PlaceholderPage("Laporan", "📈"))
        self._add_page("users",      PlaceholderPage("Pengguna", "👥"))

        # Default: produk
        self._current_key = "products"
        self._stack.setCurrentWidget(self._pages["products"])

    def _add_page(self, key: str, widget: QWidget):
        self._pages[key] = widget
        # Wrap with opacity effect
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(1.0)
        widget.setGraphicsEffect(effect)
        self._stack.addWidget(widget)

    # ── Navigation ────────────────────────────────────────────────────────────
    def _navigate_to(self, key: str):
        if key == self._current_key or self._animating:
            return
        if key not in self._pages:
            return

        self._animating = True
        old_widget = self._pages[self._current_key]
        new_widget = self._pages[key]

        self._stack.setCurrentWidget(new_widget)

        old_eff = old_widget.graphicsEffect()
        new_eff = new_widget.graphicsEffect()

        if new_eff:
            new_eff.setOpacity(0.0)

        anim_in = QPropertyAnimation(new_eff, b"opacity")
        anim_in.setDuration(ANIM_DURATION)
        anim_in.setStartValue(0.0)
        anim_in.setEndValue(1.0)
        anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_done():
            if old_eff:
                old_eff.setOpacity(1.0)
            self._animating = False

        anim_in.finished.connect(on_done)
        anim_in.start()
        self._anim_in = anim_in

        self._current_key = key