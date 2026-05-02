# views/screens/splash_screen.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    pyqtSignal,
    QRect,
    QPoint,
)
from PyQt6.QtGui import (
    QPainter,
    QPixmap,
    QFont,
    QColor,
    QPen,
    QLinearGradient,
    QRadialGradient,
    QBrush,
    QPainterPath,
    QFontMetrics,
)
import math

SPLASH_DURATION   = 2400   # ms tahan setelah fade-in selesai
FADE_IN_DURATION  = 700    # ms fade-in konten
FADE_OUT_DURATION = 450    # ms fade-out sebelum ke app

# ── Palette warna — disamakan dengan select_user_screen.py ───────────────────
CLR_BG_TOP      = QColor("#F5F3EF")   # off-white hangat (turunan #FAFAF8)
CLR_BG_BTM      = QColor("#E8E5E0")   # sedikit lebih gelap
CLR_BORDER      = QColor("#DDD9D2")   # border card
CLR_BRAND       = QColor("#4F6EF7")   # biru-ungu brand (sama persis)
CLR_TEXT        = QColor("#1B1B1B")   # teks utama
CLR_MUTED       = QColor("#888780")   # teks subtitle/muted
CLR_FOOTER      = QColor("#B4B2A9")   # footer sangat muted (turunan #5F5E5A)


# ─────────────────────────────────────────────────────────────────────────────
# Splash Screen Utama
# ─────────────────────────────────────────────────────────────────────────────
class SplashScreen(QWidget):
    """
    Full-screen splash screen dengan desain premium.
    Emit `finished` saat animasi selesai dan app siap dilanjutkan.
    """

    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._bg_pixmap = QPixmap("assets/bg_auth.png")
        self._time = 0  # untuk animasi shimmer pada background

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._build_ui()
        self._start_animation()

        # Subtle pulse timer untuk background
        self._bg_timer = QTimer()
        self._bg_timer.setInterval(40)
        self._bg_timer.timeout.connect(self._tick_background)
        self._bg_timer.start()

    # ──────────────────────────────────────────────────────────────────────────
    # UI Build
    # ──────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Container tengah ──────────────────────────────────────────────────
        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Badge / pill atas ─────────────────────────────────────────────────
        self._badge = BadgePill("POINT OF SALE")
        container_layout.addWidget(self._badge, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addSpacing(20)

        # ── Nama aplikasi ─────────────────────────────────────────────────────
        self._lbl_name = AppNameLabel()
        container_layout.addWidget(self._lbl_name, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addSpacing(10)

        # ── Divider line ──────────────────────────────────────────────────────
        self._divider = DividerWidget()
        container_layout.addWidget(self._divider, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addSpacing(10)

        # ── Tagline ───────────────────────────────────────────────────────────
        self._lbl_tagline = QLabel("Kelola warungmu dengan mudah & cepat")
        self._lbl_tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_tagline.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 500;
                letter-spacing: 3px;
                color: rgba(136, 135, 128, 0.75);
                background: transparent;
            }
        """)
        container_layout.addWidget(self._lbl_tagline)
        container_layout.addSpacing(48)

        # ── Loading dots ──────────────────────────────────────────────────────
        self._dots_widget = DotsLoader()
        container_layout.addWidget(self._dots_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addWidget(self._container)

        # Bottom bar
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addStretch()

        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background: transparent;")
        bottom_widget.setLayout(bottom_layout)

        root.addWidget(bottom_widget)

        # ── Opacity effect pada seluruh container ─────────────────────────────
        self._opacity_effect = QGraphicsOpacityEffect(self._container)
        self._opacity_effect.setOpacity(0.0)
        self._container.setGraphicsEffect(self._opacity_effect)

        # ── Opacity effect terpisah untuk bottom bar ──────────────────────────
        self._bottom_effect = QGraphicsOpacityEffect(bottom_widget)
        self._bottom_effect.setOpacity(0.0)
        bottom_widget.setGraphicsEffect(self._bottom_effect)

    # ──────────────────────────────────────────────────────────────────────────
    # Background Painting
    # ──────────────────────────────────────────────────────────────────────────
    def _tick_background(self):
        self._time += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # ── 1. Background image (atau fallback off-white gradient) ────────────
        if not self._bg_pixmap.isNull():
            scaled = self._bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (scaled.width() - w) // 2
            y = (scaled.height() - h) // 2
            painter.drawPixmap(-x, -y, scaled)

            # Scrim off-white agar teks gelap terbaca di atas foto apapun
            scrim = QLinearGradient(0, 0, 0, h)
            scrim.setColorAt(0.0, QColor(245, 243, 239, 200))
            scrim.setColorAt(0.5, QColor(239, 236, 234, 185))
            scrim.setColorAt(1.0, QColor(232, 229, 224, 205))
            painter.fillRect(self.rect(), scrim)
        else:
            # Fallback: off-white warm gradient
            bg_grad = QLinearGradient(0, 0, w * 0.4, h)
            bg_grad.setColorAt(0.0, CLR_BG_TOP)
            bg_grad.setColorAt(1.0, CLR_BG_BTM)
            painter.fillRect(self.rect(), bg_grad)

        # ── 2. Dot pattern halus (#5F5E5A sangat transparan) ─────────────────
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(95, 94, 90, 20))
        spacing = 28
        for gx in range(0, w + spacing, spacing):
            for gy in range(0, h + spacing, spacing):
                painter.drawEllipse(gx - 1, gy - 1, 3, 3)

        # ── 3. Brand radial glow (#4F6EF7, sangat halus) ─────────────────────
        cx, cy = w / 2, h * 0.45
        glow = QRadialGradient(cx, cy, min(w, h) * 0.42)
        glow.setColorAt(0.0, QColor(79, 110, 247, 35))
        glow.setColorAt(0.5, QColor(79, 110, 247, 12))
        glow.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(self.rect(), glow)

        # ── 4. Soft vignette tepi (netral) ───────────────────────────────────
        vignette = QRadialGradient(cx, cy, max(w, h) * 0.72)
        vignette.setColorAt(0.0,  QColor(255, 255, 255, 0))
        vignette.setColorAt(0.65, QColor(180, 178, 169, 18))
        vignette.setColorAt(1.0,  QColor(95, 94, 90, 40))
        painter.fillRect(self.rect(), vignette)

        # ── 5. Decorative rings (warna border #DDD9D2) ───────────────────────
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(221, 217, 210, 120), 1))
        ring_r = int(min(w, h) * 0.30)
        painter.drawEllipse(int(cx) - ring_r, int(cy) - ring_r, ring_r * 2, ring_r * 2)

        painter.setPen(QPen(QColor(221, 217, 210, 70), 1))
        ring_r2 = int(min(w, h) * 0.42)
        painter.drawEllipse(int(cx) - ring_r2, int(cy) - ring_r2, ring_r2 * 2, ring_r2 * 2)

        painter.end()

    # ──────────────────────────────────────────────────────────────────────────
    # Animation Sequence
    # ──────────────────────────────────────────────────────────────────────────
    def _start_animation(self):
        # 1) Fade-in konten utama
        fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_in.setDuration(FADE_IN_DURATION)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 2) Fade-in bottom bar sedikit lebih lambat
        fade_in_bottom = QPropertyAnimation(self._bottom_effect, b"opacity")
        fade_in_bottom.setDuration(FADE_IN_DURATION + 200)
        fade_in_bottom.setStartValue(0.0)
        fade_in_bottom.setEndValue(1.0)
        fade_in_bottom.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Mulai dots & timer setelah fade-in selesai
        fade_in.finished.connect(self._dots_widget.start)

        self._hold_timer = QTimer(singleShot=True)
        self._hold_timer.setInterval(SPLASH_DURATION)
        self._hold_timer.timeout.connect(self._begin_fade_out)
        fade_in.finished.connect(self._hold_timer.start)

        fade_in.start()
        QTimer.singleShot(120, fade_in_bottom.start)  # slight stagger

        self._fade_in_anim = fade_in
        self._fade_in_bottom_anim = fade_in_bottom

    def _begin_fade_out(self):
        self._dots_widget.stop()
        self._bg_timer.stop()

        fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_out.setDuration(FADE_OUT_DURATION)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        fade_out.finished.connect(self.finished.emit)
        fade_out.start()

        fade_out_bottom = QPropertyAnimation(self._bottom_effect, b"opacity")
        fade_out_bottom.setDuration(FADE_OUT_DURATION)
        fade_out_bottom.setStartValue(1.0)
        fade_out_bottom.setEndValue(0.0)
        fade_out_bottom.setEasingCurve(QEasingCurve.Type.InCubic)
        fade_out_bottom.start()

        self._fade_out_anim = fade_out
        self._fade_out_bottom_anim = fade_out_bottom


# ─────────────────────────────────────────────────────────────────────────────
# Badge / Pill Label
# ─────────────────────────────────────────────────────────────────────────────
class BadgePill(QWidget):
    """Pill kecil berisi teks kategori aplikasi."""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self._text = text
        self.setStyleSheet("background: transparent;")

        font = QFont("Segoe UI", 9)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3.5)
        font.setWeight(QFont.Weight.Medium)
        fm = QFontMetrics(font)
        text_w = fm.horizontalAdvance(text)
        self.setFixedSize(text_w + 28, 26)
        self._font = font

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = self.rect()

        # Pill border amber
        painter.setPen(QPen(QColor(79, 110, 247, 130), 1))
        painter.setBrush(QBrush(QColor(79, 110, 247, 22)))
        painter.drawRoundedRect(r.adjusted(0, 0, -1, -1), r.height() / 2, r.height() / 2)

        # Text
        painter.setPen(QColor(79, 110, 247, 210))
        painter.setFont(self._font)
        painter.drawText(r, Qt.AlignmentFlag.AlignCenter, self._text)
        painter.end()


# ─────────────────────────────────────────────────────────────────────────────
# App Name Label (custom paint untuk kontrol penuh)
# ─────────────────────────────────────────────────────────────────────────────
class AppNameLabel(QWidget):
    """
    Render nama 'Warung+' dengan tipografi besar, kontras tinggi,
    dan tanda '+' berwarna biru brand.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        self._font_main = QFont("Segoe UI", 62, QFont.Weight.Bold)
        self._font_plus = QFont("Segoe UI", 62, QFont.Weight.Bold)

        fm = QFontMetrics(self._font_main)
        w_warung = fm.horizontalAdvance("Warung")
        w_plus   = fm.horizontalAdvance("+")
        total_w  = w_warung + w_plus + 4
        height   = fm.height() + 8

        self.setFixedSize(total_w + 8, height)
        self._w_warung = w_warung
        self._w_plus   = w_plus

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        fm = QFontMetrics(self._font_main)
        baseline = fm.ascent() + 4

        # "Warung" — hitam hangat, shadow sangat tipis
        painter.setFont(self._font_main)
        painter.setPen(QColor(27, 27, 27, 35))
        painter.drawText(1, baseline + 2, "Warung")
        painter.setPen(QColor("#1B1B1B"))
        painter.drawText(0, baseline, "Warung")

        # "+" — biru brand
        x_plus = self._w_warung + 4

        # Subtle blue glow behind +
        glow_grad = QRadialGradient(x_plus + self._w_plus / 2, baseline - fm.ascent() / 2,
                                     self._w_plus * 2.2)
        glow_grad.setColorAt(0.0, QColor(79, 110, 247, 55))
        glow_grad.setColorAt(1.0, QColor(79, 110, 247, 0))
        painter.fillRect(
            int(x_plus - self._w_plus),
            0,
            int(self._w_plus * 3),
            self.height(),
            glow_grad,
        )

        painter.setFont(self._font_plus)
        painter.setPen(QColor(79, 110, 247, 50))
        painter.drawText(x_plus + 1, baseline + 2, "+")
        painter.setPen(QColor("#4F6EF7"))
        painter.drawText(x_plus, baseline, "+")

        painter.end()


# ─────────────────────────────────────────────────────────────────────────────
# Divider Widget
# ─────────────────────────────────────────────────────────────────────────────
class DividerWidget(QWidget):
    """Garis tipis dengan gradient fade di kedua sisi."""

    def __init__(self, width=220, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.setFixedSize(width, 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0,  QColor(255, 255, 255, 0))
        grad.setColorAt(0.2,  QColor(79, 110, 247, 90))
        grad.setColorAt(0.5,  QColor(79, 110, 247, 145))
        grad.setColorAt(0.8,  QColor(79, 110, 247, 90))
        grad.setColorAt(1.0,  QColor(255, 255, 255, 0))

        painter.fillRect(self.rect(), grad)
        painter.end()


# ─────────────────────────────────────────────────────────────────────────────
# Animated Loading Dots
# ─────────────────────────────────────────────────────────────────────────────
class DotsLoader(QWidget):
    """
    Tiga titik animasi wave bounce dengan warna biru brand.
    Ukuran dan warna diperhalus untuk kesan premium.
    """

    DOT_COUNT     = 3
    DOT_SIZE      = 8
    DOT_SPACING   = 12
    BOUNCE_DELAY  = 150    # ms antar dot
    BOUNCE_STEPS  = 32
    STEP_MS       = 14     # ≈ 60 fps per half-cycle
    BOUNCE_OFFSET = 9      # px ke atas

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        total_w = self.DOT_COUNT * self.DOT_SIZE + (self.DOT_COUNT - 1) * self.DOT_SPACING
        self.setFixedSize(total_w, self.DOT_SIZE + self.BOUNCE_OFFSET + 6)

        self._offsets  = [0.0] * self.DOT_COUNT
        self._alphas   = [180] * self.DOT_COUNT  # opacity tiap dot
        self._running  = False

    def _dot_x(self, i):
        return i * (self.DOT_SIZE + self.DOT_SPACING)

    def _dot_y(self, i):
        return self.BOUNCE_OFFSET + self._offsets[i]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(self.DOT_COUNT):
            t = abs(self._offsets[i]) / self.BOUNCE_OFFSET  # 0..1 saat naik
            # Saat naik: brand penuh #4F6EF7, saat diam: lebih muted
            r = int(79  + 20 * t)    # 79 → 99
            g = int(110 + 15 * t)    # 110 → 125
            b = int(247)
            a = int(120 + 135 * t)
            painter.setBrush(QColor(r, g, b, a))
            painter.drawEllipse(
                self._dot_x(i),
                int(self._dot_y(i)),
                self.DOT_SIZE,
                self.DOT_SIZE,
            )
        painter.end()

    def start(self):
        if self._running:
            return
        self._running = True
        self._loop()

    def stop(self):
        self._running = False

    def _loop(self):
        """Kick off satu siklus penuh, lalu ulangi."""
        if not self._running:
            return
        cycle = self.BOUNCE_DELAY * self.DOT_COUNT + self.BOUNCE_STEPS * self.STEP_MS * 2
        for i in range(self.DOT_COUNT):
            QTimer.singleShot(i * self.BOUNCE_DELAY, lambda idx=i: self._bounce(idx))
        QTimer.singleShot(cycle, self._loop)

    def _bounce(self, idx: int):
        if not self._running:
            return
        half = self.BOUNCE_STEPS

        def step(s, going_up):
            if not self._running:
                self._offsets[idx] = 0.0
                self.update()
                return
            progress = s / half
            # Easing: smooth sine
            eased = (1 - math.cos(progress * math.pi)) / 2
            if going_up:
                self._offsets[idx] = -self.BOUNCE_OFFSET * eased
            else:
                self._offsets[idx] = -self.BOUNCE_OFFSET * (1 - eased)
            self.update()

            if s < half:
                QTimer.singleShot(self.STEP_MS, lambda: step(s + 1, going_up))
            elif going_up:
                # Mulai turun
                QTimer.singleShot(self.STEP_MS, lambda: step(0, False))
            else:
                self._offsets[idx] = 0.0
                self.update()

        step(0, True)