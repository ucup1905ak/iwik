# gui/views/components/toast.py

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor


class Toast(QFrame):
    def __init__(self, message: str, kind: str = "success", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        configs = {
            "success": ("✓", "#27AE60", "#EAFAF1", "#27AE60", "Berhasil"),
            "error":   ("✕", "#E05252", "#FFF8F8", "#E05252", "Gagal"),
            "info":    ("i", "#4F6EF7", "#EEF1FE", "#4F6EF7", "Info"),
        }
        icon, text_color, bg, border, title = configs.get(kind, configs["success"])

        self.setFixedWidth(350)
        self.setStyleSheet(f"""
            QFrame {{
                background:    {bg};
                border:        1px solid {border};
                border-radius: 5px;
            }}
        """)

        # ── Drop shadow efek manual via nested frame ───────────────────────
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 2, 12, 2)
        lay.setSpacing(12)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # ── Icon circle ───────────────────────────────────────────────────
        icon_circle = QFrame()
        icon_circle.setFixedSize(32, 32)
        icon_circle.setStyleSheet(f"""
            QFrame {{
                background:    {border};
                border-radius: 16px;
                border:        none;
            }}
        """)
        icon_lay = QHBoxLayout(icon_circle)
        icon_lay.setContentsMargins(0, 0, 0, 0)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            font-size:   13px;
            font-weight: 700;
            color:       #FFFFFF;
            background:  transparent;
            border:      none;
        """)
        icon_lay.addWidget(icon_lbl)

        # ── Text block ────────────────────────────────────────────────────
        text_block = QVBoxLayout()
        text_block.setSpacing(2)
        text_block.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   12px;
            font-weight: 700;
            color:       {text_color};
            background:  transparent;
            border:      none;
        """)

        msg_lbl = QLabel(message)
        msg_lbl.setTextFormat(Qt.TextFormat.RichText)  
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"""
            font-family: 'Segoe UI';
            font-size:   12px;
            color:       {text_color};
            background:  transparent;
            border:      none;
            opacity:     0.85;
        """)

        text_block.addWidget(title_lbl)
        text_block.addWidget(msg_lbl)

        lay.addWidget(icon_circle)
        lay.addLayout(text_block, stretch=1)

    @staticmethod
    def show_toast(message: str, kind: str = "success", parent: QWidget = None):
        toast = Toast(message, kind, parent)
        toast.adjustSize()

        margin = 20
        x = parent.width()  - toast.width()  - margin
        y = parent.height() - toast.height() - margin

        toast.move(x, y + 30)
        toast.raise_()
        toast.show()

        anim = QPropertyAnimation(toast, b"pos", toast)
        anim.setDuration(250)
        anim.setStartValue(QPoint(x, y + 30))
        anim.setEndValue(QPoint(x, y))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()

        def _remove():
            try:
                # Guard: cek apakah toast masih valid
                toast.objectName()  # akan raise RuntimeError jika sudah deleted
            except RuntimeError:
                return

            anim_out = QPropertyAnimation(toast, b"pos", toast)
            anim_out.setDuration(200)
            anim_out.setStartValue(QPoint(x, y))
            anim_out.setEndValue(QPoint(x, y + 30))
            anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
            anim_out.finished.connect(lambda: (toast.hide(), toast.deleteLater()))
            anim_out.start()

        QTimer.singleShot(2800, _remove)