from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit


class NameInput(QWidget):
    def __init__(self, label="Nama", placeholder=""):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            "font-size:12px;color:#5F5E5A;font-family:'Segoe UI';font-weight:500;border:none;"
        )
        layout.addWidget(lbl)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setFixedHeight(40)
        self.input.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF;
                border: 1px solid #DDD9D2;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
                color: #1b1b1b;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus { border: 1px solid #4F6EF7; }
            QLineEdit:hover { border: 1px solid #B4B0AA; }
        """)
        layout.addWidget(self.input)

        self._err_lbl = QLabel("")
        self._err_lbl.setStyleSheet(
            "font-size:11px;color:#E05252;font-family:'Segoe UI';border:none;"
        )
        self._err_lbl.setVisible(False)
        layout.addWidget(self._err_lbl)

    def value(self):
        return self.input.text().strip()

    def showError(self, msg=""):
        self.input.setStyleSheet("""
            QLineEdit {
                background: #FFF8F8;
                border: 1px solid #E05252;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
                color: #1b1b1b;
                font-family: 'Segoe UI';
            }
        """)
        if msg:
            self._err_lbl.setText(msg)
            self._err_lbl.setVisible(True)

    def clearError(self):
        self.input.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF;
                border: 1px solid #DDD9D2;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
                color: #1b1b1b;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus { border: 1px solid #4F6EF7; }
            QLineEdit:hover { border: 1px solid #B4B0AA; }
        """)
        self._err_lbl.setVisible(False)