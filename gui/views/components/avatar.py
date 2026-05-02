from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QFont


class Avatar(QLabel):
    def __init__(self, initials, bg_color="#E6F1FB", text_color="#185FA5", dashed=False, size=44):
        super().__init__(initials)
        self.bg_color = bg_color
        self.text_color = text_color
        self.dashed = dashed
        self.size = size

        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Segoe UI", int(size * 0.3), QFont.Weight.Medium))
        self.setStyleSheet("QLabel { background-color: transparent; border: 0px; }")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addEllipse(1, 1, self.size - 2, self.size - 2)

        painter.fillPath(path, QColor(self.bg_color))

        if self.dashed:
            pen = painter.pen()
            pen.setColor(QColor("#B4B2A9"))
            pen.setWidth(1)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawEllipse(1, 1, self.size - 2, self.size - 2)

        painter.setPen(QColor(self.text_color))
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()