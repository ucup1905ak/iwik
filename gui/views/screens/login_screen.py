from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QSequentialAnimationGroup, QPropertyAnimation
from PyQt6.QtGui import QKeyEvent

from gui.views.components import (
    Avatar,
    PinDot,
    GhostButton,
)
from gui.models.user_model import verify_user_pin

PIN_LENGTH = 6

class LoginScreen(QWidget):
    def __init__(self, user: dict, on_back=None, on_success=None):  # ← tambah on_success
        super().__init__()
        self.user = user
        self.on_back = on_back
        self.on_success = on_success                                 # ← simpan callback
        self.pin_digits: list[str] = []
        self.locked = False

        self._reset_timer = QTimer(self)
        self._reset_timer.setSingleShot(True)
        self._reset_timer.timeout.connect(self._do_reset)

        self._verify_timer = QTimer(self)
        self._verify_timer.setSingleShot(True)
        self._verify_timer.timeout.connect(self._verify_pin)

        self._success_timer = QTimer(self)
        self._success_timer.setSingleShot(True)
        self._success_timer.timeout.connect(self._on_success)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setFixedWidth(360)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        card.setStyleSheet("""
            QFrame {
                background-color: #FAFAF8;
                border: 1px solid #DDD9D2;
                border-radius: 14px;
            }
        """)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(36, 28, 36, 32)
        cl.setSpacing(0)

        logo = QLabel("Warung<span style='color:#4F6EF7'>+</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("font-size:14px;color:#5F5E5A;font-weight:500;letter-spacing:1px;border:none;")
        cl.addWidget(logo)
        cl.addSpacing(24)

        avatar_row = QHBoxLayout()
        avatar_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av = Avatar(
            user["initials"],
            bg_color=user.get("avatar_bg", "#E6F1FB"),
            text_color=user.get("avatar_color", "#185FA5"),
        )
        avatar_row.addWidget(av)
        cl.addLayout(avatar_row)
        cl.addSpacing(12)

        name_lbl = QLabel(user["name"])
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet("font-size:16px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(name_lbl)

        role_lbl = QLabel(user.get("role", ""))
        role_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        role_lbl.setStyleSheet("font-size:12px;color:#888780;border:none;margin-bottom:0px;")
        cl.addWidget(role_lbl)
        cl.addSpacing(28)

        dots_row = QHBoxLayout()
        dots_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dots_row.setSpacing(16)
        self.dots: list[PinDot] = []
        accent = user.get("avatar_color", "#4F6EF7")
        for _ in range(PIN_LENGTH):
            d = PinDot(accent=accent)
            self.dots.append(d)
            dots_row.addWidget(d)
        cl.addLayout(dots_row)
        cl.addSpacing(8)

        self.status_lbl = QLabel("Ketik PIN 6 digit")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("font-size:12px;color:#888780;border:none;")
        cl.addWidget(self.status_lbl)
        cl.addSpacing(32)

        hint = QLabel("Gunakan keyboard untuk memasukkan PIN")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setWordWrap(True)
        hint.setStyleSheet("font-size:11px;color:#B4B2A9;border:none;")
        cl.addWidget(hint)
        cl.addSpacing(24)

        back_btn = GhostButton("Ganti akun", on_click=self._go_back)
        cl.addWidget(back_btn)

        root.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self.setFocus)

    def keyPressEvent(self, event: QKeyEvent):
        if self.locked:
            return
        key = event.text()
        if key.isdigit():
            self._add_digit(key)
        elif event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            self._remove_digit()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if len(self.pin_digits) == PIN_LENGTH:
                self._verify_pin()
        else:
            super().keyPressEvent(event)

    def _add_digit(self, d: str):
        if len(self.pin_digits) < PIN_LENGTH:
            self.pin_digits.append(d)
            self._refresh_dots()
            self._set_status("Ketik PIN 6 digit", "#888780")
            if len(self.pin_digits) == PIN_LENGTH:
                self._verify_timer.start(160)

    def _remove_digit(self):
        if self.pin_digits:
            self.pin_digits.pop()
            self._refresh_dots()
            self._set_status("Ketik PIN 6 digit", "#888780")

    def _refresh_dots(self, error=False):
        for i, dot in enumerate(self.dots):
            dot.set_error(error)
            dot.set_filled(i < len(self.pin_digits))

    def _set_status(self, text: str, color: str):
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet(f"font-size:12px;color:{color};border:none;")

    def _verify_pin(self):
        if self.locked:
            return

        entered_pin = "".join(self.pin_digits)
        user = verify_user_pin(self.user["name"], entered_pin)

        if user:
            self._set_status("Autentikasi berhasil — menyiapkan dashboard...", "#3B8A3E")
            self.locked = True
            self._success_timer.start(700)
        else:
            self._shake_and_reset()

    def _shake_and_reset(self):
        self.locked = True
        self._set_status("PIN salah. Coba lagi.", "#E0443A")
        self._refresh_dots(error=True)

        for dot in self.dots:
            grp = QSequentialAnimationGroup(dot)
            for offset in [9, -9, 6, -6, 3, -3, 0]:
                anim = QPropertyAnimation(dot, b"shake")
                anim.setDuration(38)
                anim.setStartValue(dot._shake_offset)
                anim.setEndValue(offset)
                grp.addAnimation(anim)
            grp.start()

        self._reset_timer.start(650)

    def _do_reset(self):
        self.pin_digits.clear()
        self._refresh_dots(error=False)
        self.locked = False
        self.setFocus()

    def _on_success(self):
        # Panggil callback on_success dengan data user, bukan QMessageBox lagi
        if self.on_success:
            self.on_success(self.user)

    def _go_back(self):
        if self.on_back:
            self.on_back()