from PyQt6.QtWidgets import QFrame


class Divider(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet("background-color: #DDD9D2; border: none;")