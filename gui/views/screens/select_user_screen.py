# views/screens/select_user_screen.py
"""
Select User Screen
==================
Layar awal untuk memilih akun dari database
atau menambahkan admin baru.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt

from gui.views.components import (
    Divider,
    AccountOption,
)


class SelectUserScreen(QWidget):
    def __init__(self, users: list[dict], on_select=None, on_add=None):
        super().__init__()

        self.users = users
        self.on_select = on_select
        self.on_add = on_add

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setFixedWidth(440)
        card.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Minimum,
        )
        card.setStyleSheet("""
            QFrame {
                background-color: #FAFAF8;
                border: 1px solid #DDD9D2;
                border-radius: 14px;
            }
        """)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(36, 30, 36, 30)
        cl.setSpacing(0)

        logo = QLabel("Warung<span style='color:#4F6EF7'>+</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("""
            font-size:14px;
            color:#5F5E5A;
            font-weight:500;
            letter-spacing:1px;
            border:none;
        """)
        cl.addWidget(logo)
        cl.addSpacing(10)

        title = QLabel("Pilih akun")
        title.setStyleSheet("""
            font-size:20px;
            font-weight:600;
            color:#1B1B1B;
            border:none;
        """)
        cl.addWidget(title)

        subtitle = QLabel("Masuk sebagai siapa hari ini?")
        subtitle.setStyleSheet("""
            font-size:12px;
            color:#888780;
            border:none;
        """)
        cl.addWidget(subtitle)
        cl.addSpacing(16)

        cl.addWidget(Divider())
        cl.addSpacing(10)

        for user in self.users:
            acc = AccountOption(
                user["initials"],
                user["name"],
                badge_text=user["role"],
                badge_bg=user["badge_bg"],
                badge_color=user["badge_color"],
                avatar_bg=user["avatar_bg"],
                avatar_color=user["avatar_color"],
                on_click=lambda u=user: self.on_select(u) if self.on_select else None,
            )
            cl.addWidget(acc)
            cl.addSpacing(4)

        cl.addSpacing(8)
        cl.addWidget(Divider())
        cl.addSpacing(10)

        root.addWidget(
            card,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
