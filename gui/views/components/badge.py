from PyQt6.QtWidgets import QLabel


class Badge(QLabel):
    def __init__(self, text, bg="#EAF3DE", color="#3B6D11"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                font-size: 11px;
                font-weight: 500;
                padding: 2px 10px;
                border-radius: 10px;
                font-family: 'Segoe UI';
            }}
        """)