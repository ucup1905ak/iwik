# views/main_shell.py

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QStackedWidget,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer

from gui.views.components.sidebar import SidebarWidget
from gui.views.screens.product_page import ProductPage


ANIM_DURATION = 160
INITIAL_PAGE_KEY = "products"


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
        self._pending_key: str | None = None
        self._current_key = INITIAL_PAGE_KEY

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: #F4F5F9;")

        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────────────
        # Active key sidebar harus sama dengan page awal stack.
        self._sidebar = SidebarWidget(
            user=self._user,
            active_key=self._current_key,
        )
        self._sidebar.nav_changed.connect(self._navigate_to)
        self._sidebar.logout_requested.connect(self.logout_requested.emit)
        root.addWidget(self._sidebar)

        # ── Content area ──────────────────────────────────────────────────────
        self._stack = QStackedWidget()
        self._stack.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._stack.setStyleSheet("background: #F4F5F9;")
        root.addWidget(self._stack, stretch=1)

        # ── Lazy-loaded pages ─────────────────────────────────────────────────
        self._pages: dict[str, QWidget] = {}
        self._page_config = {
            "dashboard":  ("Dashboard", "📊", None),
            "products":   (None, None, "products"),
            "categories": ("Kategori", "🏷️", None),
            "cashier":    ("Kasir", "🛒", None),
            "reports":    ("Laporan", "📈", None),
            "users":      ("Pengguna", "👥", None),
        }

        initial_page = self._get_or_create_page(self._current_key)
        if initial_page is not None:
            self._stack.setCurrentWidget(initial_page)
            self._sidebar.set_active(self._current_key)

    def _add_page(self, key: str, widget: QWidget):
        self._pages[key] = widget
        widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Jangan pasang QGraphicsOpacityEffect permanen di page.
        # Effect hanya dibuat sementara saat transisi di _navigate_to().
        self._stack.addWidget(widget)

    def _get_or_create_page(self, key: str) -> QWidget | None:
        """Lazy-load: create page on first access."""
        if key in self._pages:
            return self._pages[key]

        if key not in self._page_config:
            return None

        title, emoji, page_type = self._page_config[key]

        if page_type == "products":
            widget = ProductPage(user=self._user)
        else:
            widget = PlaceholderPage(title, emoji)

        self._add_page(key, widget)
        return widget

    def _navigate_to(self, key: str):
        if key == self._current_key:
            self._sidebar.set_active(key)
            return

        if self._animating:
            self._pending_key = key
            return

        new_widget = self._get_or_create_page(key)
        if new_widget is None:
            self._sidebar.set_active(self._current_key)
            return

        self._animating = True

        effect = QGraphicsOpacityEffect(new_widget)
        effect.setOpacity(0.0)
        new_widget.setGraphicsEffect(effect)

        self._stack.setCurrentWidget(new_widget)
        self._current_key = key
        self._sidebar.set_active(key)

        # Force repaint setelah page benar-benar masuk ke QStackedWidget.
        new_widget.update()
        self._stack.update()

        anim_in = QPropertyAnimation(effect, b"opacity")
        anim_in.setDuration(ANIM_DURATION)
        anim_in.setStartValue(0.0)
        anim_in.setEndValue(1.0)
        anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_done():
            # Penting: lepas effect setelah animasi.
            # Effect permanen di container/page besar sering membuat child repaint terlambat.
            new_widget.setGraphicsEffect(None)
            new_widget.update()
            self._stack.update()

            self._animating = False
            self._flush_pending_nav()

        anim_in.finished.connect(on_done)
        anim_in.start()
        self._anim_in = anim_in

    def _flush_pending_nav(self):
        if not self._pending_key:
            return

        if self._pending_key == self._current_key:
            self._pending_key = None
            self._sidebar.set_active(self._current_key)
            return

        next_key = self._pending_key
        self._pending_key = None
        QTimer.singleShot(0, lambda key=next_key: self._navigate_to(key))
