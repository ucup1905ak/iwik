# views/screens/splash_screen.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    QEasingCurve,
    QParallelAnimationGroup,
    pyqtSignal,
)
from PyQt6.QtGui import QPainter, QPixmap, QFont, QColor, QPen

SPLASH_DURATION = 2200   # ms sebelum mulai fade-out
FADE_IN_DURATION = 600   # ms fade-in logo
FADE_OUT_DURATION = 400  # ms fade-out sebelum ke app


class SplashScreen(QWidget):
    """
    Full-screen loading screen yang tampil saat pertama buka.
    Emit `finished` saat animasi selesai dan app siap dilanjutkan.
    """

    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._bg_pixmap = QPixmap("assets/bg_auth.png")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._build_ui()
        self._start_animation()

    # ────────────────────────────────────────────────────────────────────────
    # UI
    # ────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Container tengah ─────────────────────────────────────────────────
        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(12)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Nama aplikasi ────────────────────────────────────────────────────
        self._lbl_name = QLabel("Warung<span style='color:#4F6EF7'>+</span>")
        self._lbl_name.setTextFormat(Qt.TextFormat.RichText)
        self._lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_name.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI';
                font-size: 56px;
                font-weight: 700;
                letter-spacing: 2px;
                color: #FFFFFF;
                background: transparent;
            }
        """)

        # ── Tagline ──────────────────────────────────────────────────────────
        self._lbl_tagline = QLabel("Kelola warungmu dengan mudah")
        self._lbl_tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_tagline.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI';
                font-size: 15px;
                font-weight: 400;
                letter-spacing: 0.5px;
                color: rgba(255, 255, 255, 0.75);
                background: transparent;
            }
        """)

        # ── Loading dots ─────────────────────────────────────────────────────
        self._dots_widget = DotsLoader()

        container_layout.addWidget(self._lbl_name)
        container_layout.addWidget(self._lbl_tagline)
        container_layout.addSpacing(28)
        container_layout.addWidget(self._dots_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addWidget(self._container)

        # ── Opacity effect pada seluruh container ────────────────────────────
        self._opacity_effect = QGraphicsOpacityEffect(self._container)
        self._opacity_effect.setOpacity(0.0)
        self._container.setGraphicsEffect(self._opacity_effect)

    # ────────────────────────────────────────────────────────────────────────
    # Background
    # ────────────────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if not self._bg_pixmap.isNull():
            scaled = self._bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            painter.drawPixmap(-x, -y, scaled)
        else:
            # Fallback: gradien gelap
            painter.fillRect(self.rect(), QColor("#1A1D2E"))

        # Overlay gelap tipis supaya teks lebih terbaca
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        painter.end()

    # ────────────────────────────────────────────────────────────────────────
    # Animation sequence
    # ────────────────────────────────────────────────────────────────────────
    def _start_animation(self):
        # 1) Fade-in container
        fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_in.setDuration(FADE_IN_DURATION)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 2) Mulai dots setelah fade-in selesai
        fade_in.finished.connect(self._dots_widget.start)

        # 3) Timer: setelah SPLASH_DURATION, fade-out
        self._hold_timer = QTimer(singleShot=True)
        self._hold_timer.setInterval(SPLASH_DURATION)
        self._hold_timer.timeout.connect(self._begin_fade_out)

        fade_in.finished.connect(self._hold_timer.start)
        fade_in.start()

        self._fade_in_anim = fade_in  # keep reference

    def _begin_fade_out(self):
        self._dots_widget.stop()

        fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_out.setDuration(FADE_OUT_DURATION)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        fade_out.finished.connect(self.finished.emit)
        fade_out.start()

        self._fade_out_anim = fade_out


# ────────────────────────────────────────────────────────────────────────────
# Animated loading dots widget
# ────────────────────────────────────────────────────────────────────────────
class DotsLoader(QWidget):
    """
    Tiga titik yang muncul bergantian (wave bounce).
    """

    DOT_COUNT = 3
    DOT_SIZE = 10
    DOT_SPACING = 14
    BOUNCE_DELAY = 160   # ms antar dot
    BOUNCE_DURATION = 500
    BOUNCE_OFFSET = 10   # px ke atas

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        total_w = self.DOT_COUNT * self.DOT_SIZE + (self.DOT_COUNT - 1) * self.DOT_SPACING
        self.setFixedSize(total_w, self.DOT_SIZE + self.BOUNCE_OFFSET + 4)

        # Posisi Y setiap dot (animasi via _offsets list)
        self._offsets = [0.0] * self.DOT_COUNT
        self._anims = []
        self._running = False

    # ── Dots positions ───────────────────────────────────────────────────────
    def _dot_x(self, i: int) -> int:
        return i * (self.DOT_SIZE + self.DOT_SPACING)

    def _dot_y(self, i: int) -> float:
        return self.BOUNCE_OFFSET + self._offsets[i]

    # ── Paint ────────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for i in range(self.DOT_COUNT):
            color = QColor(255, 255, 255, 210)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                self._dot_x(i),
                int(self._dot_y(i)),
                self.DOT_SIZE,
                self.DOT_SIZE,
            )
        painter.end()

    # ── Animation control ────────────────────────────────────────────────────
    def start(self):
        if self._running:
            return
        self._running = True
        self._schedule_bounce(0)

    def stop(self):
        self._running = False
        for a in self._anims:
            a.stop()
        self._anims.clear()

    def _schedule_bounce(self, dot_index: int):
        """Chain: dot 0 → dot 1 → dot 2 → dot 0 → ..."""
        if not self._running:
            return

        # Buat property animasi manual via timer + offset list
        delay = dot_index * self.BOUNCE_DELAY
        QTimer.singleShot(delay, lambda idx=dot_index: self._bounce_dot(idx))

        # Setelah satu putaran, loop lagi
        cycle_duration = self.BOUNCE_DELAY * self.DOT_COUNT + self.BOUNCE_DURATION
        if dot_index == 0:
            QTimer.singleShot(cycle_duration, lambda: self._schedule_bounce(0))

    def _bounce_dot(self, idx: int):
        if not self._running:
            return

        steps = 30
        duration = self.BOUNCE_DURATION
        step_ms = duration // steps

        def animate_step(step, going_up=True):
            if not self._running:
                return
            progress = step / (steps // 2)
            if going_up:
                offset = -self.BOUNCE_OFFSET * progress
            else:
                offset = -self.BOUNCE_OFFSET * (1 - (progress - 1))

            self._offsets[idx] = max(-self.BOUNCE_OFFSET, min(0, offset))
            self.update()

            if step < steps // 2:
                QTimer.singleShot(step_ms, lambda: animate_step(step + 1, going_up=True))
            elif step < steps:
                QTimer.singleShot(step_ms, lambda: animate_step(step + 1, going_up=False))
            else:
                self._offsets[idx] = 0.0
                self.update()

        animate_step(1)