# views/components/buttons.py

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPainterPath


class PrimaryButton(QWidget):
    def __init__(self, text, on_click=None):
        super().__init__()
        self._on_click = on_click
        self._bg_anim_val = 0
        self._pressed = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel(text)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet(
            "font-size:14px; font-weight:600; color:#FFFFFF;"
            "font-family:'Segoe UI'; background:transparent; border:none;"
        )
        layout.addWidget(self._label)

        self._anim = QPropertyAnimation(self, b"hoverVal")
        self._anim.setDuration(120)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def getHoverVal(self):
        return self._bg_anim_val

    def setHoverVal(self, value):
        self._bg_anim_val = value
        self.update()

    hoverVal = pyqtProperty(int, getHoverVal, setHoverVal)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 8, 8)

        # Interpolasi antara #4F6EF7 normal dan #3B5CE6 hover.
        t = self._bg_anim_val / 255
        r = int(0x4F + (0x3B - 0x4F) * t)
        g = int(0x6E + (0x5C - 0x6E) * t)
        b = int(0xF7 + (0xE6 - 0xF7) * t)

        if self._pressed:
            r, g, b = 0x2B, 0x49, 0xD4

        painter.fillPath(path, QColor(r, g, b))
        painter.end()

    def _anim_to(self, value):
        self._anim.stop()
        self._anim.setStartValue(self._bg_anim_val)
        self._anim.setEndValue(value)
        self._anim.start()

    def enterEvent(self, event):
        self._anim_to(255)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._anim_to(0)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.update()

        if self._on_click and self.rect().contains(event.position().toPoint()):
            self._on_click()

        super().mouseReleaseEvent(event)


class GhostButton(QWidget):
    def __init__(self, text, on_click=None):
        super().__init__()
        self._on_click = on_click
        self._bg_alpha = 0

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel(text)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet(
            "font-size:14px; font-weight:500; color:#5F5E5A;"
            "font-family:'Segoe UI'; background:transparent;border:none;"
        )
        layout.addWidget(self._label)

        self._anim = QPropertyAnimation(self, b"bgAlpha")
        self._anim.setDuration(120)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def getBgAlpha(self):
        return self._bg_alpha

    def setBgAlpha(self, value):
        self._bg_alpha = value
        self.update()

    bgAlpha = pyqtProperty(int, getBgAlpha, setBgAlpha)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 8, 8)

        bg = QColor("#ECEAE6")
        bg.setAlpha(self._bg_alpha)
        painter.fillPath(path, bg)

        border = QColor("#C8C4BC")
        if self._bg_alpha > 30:
            border.setAlpha(min(self._bg_alpha + 75, 255))
        else:
            border.setAlpha(255)

        painter.setPen(border)
        painter.drawPath(path)
        painter.end()

    def _anim_to(self, value):
        self._anim.stop()
        self._anim.setStartValue(self._bg_alpha)
        self._anim.setEndValue(value)
        self._anim.start()

    def enterEvent(self, event):
        self._anim_to(220)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._anim_to(0)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._anim_to(255)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._anim_to(220)

        if self._on_click and self.rect().contains(event.position().toPoint()):
            self._on_click()

        super().mouseReleaseEvent(event)
