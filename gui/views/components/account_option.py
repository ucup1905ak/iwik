from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QFont

from .avatar import Avatar
from .badge import Badge


class AccountOption(QWidget):
    def __init__(
        self,
        initials,
        name,
        badge_text="",
        badge_bg="#EAF3DE",
        badge_color="#3B6D11",
        avatar_bg="#E6F1FB",
        avatar_color="#185FA5",
        is_add=False,
        on_click=None,
    ):
        super().__init__()

        self.is_add = is_add
        self.on_click = on_click
        self._bg_alpha = 0
        self._chevron_alpha = 0

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(64)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: 0px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 14, 10)
        layout.setSpacing(14)

        if is_add:
            avatar = Avatar(
                "+",
                bg_color="#F1EFE8",
                text_color="#5F5E5A",
                dashed=True
            )
            avatar.setFont(QFont("Segoe UI", 20))
        else:
            avatar = Avatar(
                initials,
                bg_color=avatar_bg,
                text_color=avatar_color
            )

        layout.addWidget(avatar)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        name_label = QLabel(name)

        if is_add:
            name_label.setStyleSheet("""
                font-size: 14px;
                color: #888780;
                font-weight: 400;
                font-family: 'Segoe UI';
            """)
        else:
            name_label.setStyleSheet("""
                font-size: 14px;
                color: #1B1B1B;
                font-weight: 500;
                font-family: 'Segoe UI';
            """)

        text_layout.addWidget(name_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        if badge_text:
            badge = Badge(
                badge_text,
                bg=badge_bg,
                color=badge_color
            )
            layout.addWidget(badge)

        self.chevron = QLabel("›")
        self.chevron.setStyleSheet("""
            font-size: 18px;
            color: transparent;
            font-family: 'Segoe UI';
            padding-right: 2px;
        """)

        layout.addWidget(self.chevron)

        self._anim_bg = QPropertyAnimation(self, b"bgAlpha")
        self._anim_bg.setDuration(140)
        self._anim_bg.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim_chevron = QPropertyAnimation(self, b"chevronAlpha")
        self._anim_chevron.setDuration(140)
        self._anim_chevron.setEasingCurve(QEasingCurve.Type.OutCubic)

    def getBgAlpha(self):
        return self._bg_alpha

    def setBgAlpha(self, value):
        self._bg_alpha = value
        self.update()

    bgAlpha = pyqtProperty(int, getBgAlpha, setBgAlpha)

    def getChevronAlpha(self):
        return self._chevron_alpha

    def setChevronAlpha(self, value: int):
        self._chevron_alpha = value

        r = int(0xB4 * value / 255)
        g = int(0xB2 * value / 255)
        b = int(0xA9 * value / 255)

        self.chevron.setStyleSheet(
            f"""
            font-size:18px;
            color: rgba({r},{g},{b},{value});
            font-family:'Segoe UI';
            padding-right:2px;
            """
        )

    chevronAlpha = pyqtProperty(int, getChevronAlpha, setChevronAlpha)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(
            0,
            0,
            self.width(),
            self.height(),
            8,
            8
        )

        if self._bg_alpha > 0:
            bg = QColor("#ECEAE6")
            bg.setAlpha(self._bg_alpha)

            painter.fillPath(path, bg)

            if self._bg_alpha > 50:
                border = QColor("#C8C4BC")
                border.setAlpha(min(self._bg_alpha, 160))

                painter.setPen(border)
                painter.drawPath(path)

        painter.end()

    def _anim_to(self, bg_val: int, ch_val: int):
        self._anim_bg.stop()
        self._anim_bg.setStartValue(self._bg_alpha)
        self._anim_bg.setEndValue(bg_val)
        self._anim_bg.start()

        self._anim_chevron.stop()
        self._anim_chevron.setStartValue(self._chevron_alpha)
        self._anim_chevron.setEndValue(ch_val)
        self._anim_chevron.start()

    def enterEvent(self, e):
        self._anim_to(220, 255)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._anim_to(0, 0)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        self._anim_to(255, 255)
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._anim_to(220, 255)

        if self.on_click:
            self.on_click()

        super().mouseReleaseEvent(e)