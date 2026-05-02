from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFrame
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect
from .pin_dot import PinDot


class PinRow(QWidget):
    PIN_LEN = 6

    def __init__(self, label_text="PIN"):
        super().__init__()
        self._error = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        lbl = QLabel(label_text)
        lbl.setStyleSheet(
            "font-size:12px; color:#5F5E5A; font-family:'Segoe UI'; font-weight:500; border:none;"
        )
        outer.addWidget(lbl)

        self._dot_frame = QFrame()
        self._dot_frame.setFixedHeight(40)
        self._dot_frame.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border: 1px solid #DDD9D2;
                border-radius: 8px;
            }
            QFrame:focus-within {
                border: 1px solid #4F6EF7;
            }
        """)
        dot_layout = QHBoxLayout(self._dot_frame)
        dot_layout.setContentsMargins(14, 0, 14, 0)
        dot_layout.setSpacing(10)
        dot_layout.addStretch()

        self._dots = []
        for _ in range(self.PIN_LEN):
            d = PinDot()
            self._dots.append(d)
            dot_layout.addWidget(d)

        dot_layout.addStretch()

        self._input = QLineEdit()
        self._input.setMaxLength(self.PIN_LEN)
        self._input.setEchoMode(QLineEdit.EchoMode.Password)
        self._input.setFixedSize(1, 1)
        self._input.setStyleSheet("background:transparent; border:none; color:transparent;")
        dot_layout.addWidget(self._input)

        outer.addWidget(self._dot_frame)
        self._dot_frame.mousePressEvent = lambda e: self._input.setFocus()

        self._err_lbl = QLabel("")
        self._err_lbl.setStyleSheet(
            "font-size:11px; color:#E05252; font-family:'Segoe UI'; border:none;"
        )
        self._err_lbl.setVisible(False)  # ← sama persis dengan NameInput
        outer.addWidget(self._err_lbl)

        self._input.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text: str):
        self.clearError()
        for i, dot in enumerate(self._dots):
            dot.set_filled(i < len(text))

    def value(self) -> str:
        return self._input.text()

    def clear(self):
        self._input.clear()
        self.clearError()

    def setFocus(self):
        self._input.setFocus()

    def showError(self, msg: str = ""):
        self._error = True
        for d in self._dots:
            d.set_error(True)
        if msg:
            self._err_lbl.setText(msg)
            self._err_lbl.setVisible(True)  # ← sama persis dengan NameInput
        self._shake()

    def clearError(self):
        self._error = False
        for d in self._dots:
            d.set_error(False)
        self._err_lbl.setVisible(False)  # ← sama persis dengan NameInput

    def _shake(self):
        orig = self._dot_frame.geometry()
        anim = QPropertyAnimation(self._dot_frame, b"geometry")
        anim.setDuration(300)
        anim.setKeyValueAt(0,    QRect(orig.x(),     orig.y(), orig.width(), orig.height()))
        anim.setKeyValueAt(0.15, QRect(orig.x() - 6, orig.y(), orig.width(), orig.height()))
        anim.setKeyValueAt(0.35, QRect(orig.x() + 6, orig.y(), orig.width(), orig.height()))
        anim.setKeyValueAt(0.55, QRect(orig.x() - 4, orig.y(), orig.width(), orig.height()))
        anim.setKeyValueAt(0.75, QRect(orig.x() + 4, orig.y(), orig.width(), orig.height()))
        anim.setKeyValueAt(1,    QRect(orig.x(),     orig.y(), orig.width(), orig.height()))
        anim.setEasingCurve(QEasingCurve.Type.Linear)
        anim.finished.connect(lambda: self._dot_frame.setGeometry(orig))
        anim.start()
        self._shake_anim = anim
        