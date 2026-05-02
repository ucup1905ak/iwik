# views/app_shell.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    Qt,
)
from PyQt6.QtGui import QPainter, QPixmap

# Screens
from gui.views.screens.select_user_screen import SelectUserScreen
from gui.views.screens.login_screen import LoginScreen
from gui.views.screens.add_admin_screen import AddAdminScreen
from gui.views.screens.splash_screen import SplashScreen
from gui.views.main_shell import MainShell

# Database
from gui.models.user_model import (
    get_all_users,
    create_user,
)

ANIM_DURATION = 180


class AppShell(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Warung+")
        self.setMinimumSize(1024, 720)
        self.setStyleSheet("AppShell { font-family: 'Segoe UI'; }")

        self._bg_pixmap = QPixmap("assets/bg_auth.png")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent;")
        root.addWidget(self._stack)

        self._animating = False
        self._in_main_shell = False  # track apakah sudah di main shell

        self._show_splash()

    # ────────────────────────────────────────────────────────────────────────
    # Background — hanya tampil saat di auth screens
    # ────────────────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        if self._in_main_shell:
            return  # main shell punya background sendiri
        painter = QPainter(self)
        if not self._bg_pixmap.isNull():
            scaled = self._bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            painter.drawPixmap(-x, -y, scaled)
        painter.end()

    # ────────────────────────────────────────────────────────────────────────
    # Splash
    # ────────────────────────────────────────────────────────────────────────
    def _show_splash(self):
        self._splash = SplashScreen()
        self._splash.finished.connect(self._on_splash_finished)
        self._stack.addWidget(self._splash)
        self._stack.setCurrentWidget(self._splash)

    def _on_splash_finished(self):
        self.users = self._load_users_from_db()
        if len(self.users) == 0:
            self._go_add_admin(initial=True)
        else:
            self._go_select(initial=True)

    # ────────────────────────────────────────────────────────────────────────
    # Database
    # ────────────────────────────────────────────────────────────────────────
    def _load_users_from_db(self) -> list[dict]:
        db_users = get_all_users()
        users = []
        for user in db_users:
            user_id, name, role = user
            is_admin = role == 1
            users.append({
                "id":          user_id,
                "initials":    self._generate_initials(name),
                "name":        name,
                "role":        "Admin" if is_admin else "Cashier",
                "badge_bg":    "#EEF0FD" if is_admin else "#FDF0EC",
                "badge_color": "#3B52C4" if is_admin else "#B04A28",
                "avatar_bg":   "#EEF0FD" if is_admin else "#FDF0EC",
                "avatar_color":"#3B52C4" if is_admin else "#B04A28",
            })
        return users

    # ────────────────────────────────────────────────────────────────────────
    # Auth Navigation
    # ────────────────────────────────────────────────────────────────────────
    def _go_select(self, initial: bool = False):
        self._in_main_shell = False
        screen = SelectUserScreen(
            users=self.users,
            on_select=self._go_login,
            on_add=self._go_add_admin,
        )
        wrapper = self._make_wrapper(screen)
        if initial:
            self._stack.addWidget(wrapper)
            self._transition(wrapper, remove_old=True)
        else:
            self._transition(wrapper)

    def _go_login(self, user: dict):
        screen = LoginScreen(
            user=user,
            on_back=self._go_select,
            on_success=lambda u: self._go_main(u),   # ← callback baru
        )
        self._transition(self._make_wrapper(screen))

    def _go_add_admin(self, initial: bool = False):
        screen = AddAdminScreen(
            on_back=None if len(self.users) == 0 else self._go_select,
            on_success=self._handle_admin_saved,
        )
        wrapper = self._make_wrapper(screen)
        if initial:
            self._stack.addWidget(wrapper)
            self._transition(wrapper, remove_old=True)
        else:
            self._transition(wrapper)

    # ────────────────────────────────────────────────────────────────────────
    # Main Shell (post-login)
    # ────────────────────────────────────────────────────────────────────────
    def _go_main(self, user: dict):
        """
        Masuk ke main app (sidebar + konten) setelah login berhasil.
        Main shell tidak dibungkus wrapper transparan karena punya BG sendiri.
        """
        self._in_main_shell = True

        main = MainShell(user=user)
        main.logout_requested.connect(self._handle_logout)

        # Beri opacity effect manual supaya transisi bisa jalan
        effect = QGraphicsOpacityEffect(main)
        effect.setOpacity(1.0)
        main.setGraphicsEffect(effect)

        self._stack.addWidget(main)

        old = self._stack.currentWidget()
        self._stack.setCurrentWidget(main)

        old_eff = old.graphicsEffect() if old else None
        new_eff = effect
        new_eff.setOpacity(0.0)

        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

        anim = QPropertyAnimation(new_eff, b"opacity")
        anim.setDuration(ANIM_DURATION)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def done():
            self._stack.removeWidget(old)
            if old:
                old.deleteLater()
            self.update()  # force repaint agar BG hilang

        anim.finished.connect(done)
        anim.start()
        self._anim_to_main = anim

    def _handle_logout(self):
        """Kembali ke select user screen setelah logout."""
        self._in_main_shell = False
        self.users = self._load_users_from_db()
        self._go_select()
        self.update()

    # ────────────────────────────────────────────────────────────────────────
    # State handling
    # ────────────────────────────────────────────────────────────────────────
    def _handle_admin_saved(self, data: dict):
        create_user(name=data["name"], pin=data["pin"], role=1)
        self.users = self._load_users_from_db()
        print(f"[AppShell] Admin baru: {data['name']}")
        self._go_select()

    # ────────────────────────────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────────────────────────────
    def _generate_initials(self, name: str) -> str:
        parts = name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        if len(parts) == 1:
            return parts[0][:2].upper()
        return "??"

    def _make_wrapper(self, screen: QWidget) -> QWidget:
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(screen)
        effect = QGraphicsOpacityEffect(wrapper)
        effect.setOpacity(1.0)
        wrapper.setGraphicsEffect(effect)
        return wrapper

    def _transition(self, new_wrapper: QWidget, remove_old: bool = False):
        if self._animating:
            return
        self._animating = True

        old_wrapper = self._stack.currentWidget()
        self._stack.addWidget(new_wrapper)
        self._stack.setCurrentWidget(new_wrapper)

        old_effect = old_wrapper.graphicsEffect() if old_wrapper else None
        new_effect = new_wrapper.graphicsEffect()

        if old_effect is None:
            if new_effect:
                new_effect.setOpacity(0.0)
                anim_in = QPropertyAnimation(new_effect, b"opacity")
                anim_in.setDuration(ANIM_DURATION)
                anim_in.setStartValue(0.0)
                anim_in.setEndValue(1.0)
                anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

                def on_finished_simple():
                    if old_wrapper:
                        self._stack.removeWidget(old_wrapper)
                        old_wrapper.deleteLater()
                    self._animating = False

                anim_in.finished.connect(on_finished_simple)
                anim_in.start()
                self._anim_in = anim_in
            else:
                if old_wrapper:
                    self._stack.removeWidget(old_wrapper)
                    old_wrapper.deleteLater()
                self._animating = False
            return

        new_effect.setOpacity(0.0)

        anim_out = QPropertyAnimation(old_effect, b"opacity")
        anim_out.setDuration(ANIM_DURATION)
        anim_out.setStartValue(1.0)
        anim_out.setEndValue(0.0)
        anim_out.setEasingCurve(QEasingCurve.Type.OutCubic)

        anim_in = QPropertyAnimation(new_effect, b"opacity")
        anim_in.setDuration(ANIM_DURATION)
        anim_in.setStartValue(0.0)
        anim_in.setEndValue(1.0)
        anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup()
        group.addAnimation(anim_out)
        group.addAnimation(anim_in)

        def on_finished():
            self._stack.removeWidget(old_wrapper)
            old_wrapper.deleteLater()
            self._animating = False

        group.finished.connect(on_finished)
        group.start()
        self._anim_group = group