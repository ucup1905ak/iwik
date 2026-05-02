from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt


class PinDot(QWidget):
    def __init__(self, accent="#4F6EF7"):  # ← tambahkan ini
        super().__init__()
        self.setFixedSize(22, 22)  # ← samakan ukuran dengan versi lama (22, bukan 14)
        self.accent = accent
        self._filled = False
        self._error = False
        self._shake_offset = 0  # ← diperlukan oleh shake animation di LoginScreen

    def set_filled(self, v: bool):  # ← LoginScreen pakai set_filled, bukan setFilled
        self._filled = v
        self._error = False
        self.update()

    def set_error(self, v: bool):   # ← LoginScreen pakai set_error
        self._error = v
        self.update()

    # Untuk shake animation di LoginScreen
    def get_shake(self): return self._shake_offset
    def set_shake(self, v):
        self._shake_offset = v
        self.update()
    from PyQt6.QtCore import pyqtProperty
    shake = pyqtProperty(int, get_shake, set_shake)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx = self.rect().center().x() + self._shake_offset
        cy = self.rect().center().y()
        r = 8
        if self._error:
            painter.setBrush(QColor("#E0443A"))
        elif self._filled:
            painter.setBrush(QColor(self.accent))
        else:
            pen = painter.pen()
            pen.setColor(QColor("#C8C4BC"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)
            painter.end()
            return
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)
        painter.end()