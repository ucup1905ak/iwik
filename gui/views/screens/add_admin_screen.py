# views/screens/add_admin_screen.py
"""
Add Admin Screen
================
Layar tambah admin baru.
UI only — belum terhubung ke SQLite.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt

from gui.views.components import (
    Avatar,
    Divider,
    NameInput,
    PinRow,
    PrimaryButton,
    GhostButton,
)


class AddAdminScreen(QWidget):
    def __init__(self, on_back=None, on_success=None):
        super().__init__()
        self.on_back = on_back
        self.on_success = on_success

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Card ──────────────────────────────────────────────────────────────
        card = QFrame()
        card.setFixedWidth(440)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        card.setStyleSheet("""
            QFrame {
                background-color: #FAFAF8;
                border: 1px solid #DDD9D2;
                border-radius: 14px;
            }
        """)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(36, 30, 36, 30)
        cl.setSpacing(0)

        # Logo
        logo = QLabel("Warung<span style='color:#4F6EF7'>+</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet(
            "font-size:14px;color:#5F5E5A;font-weight:500;letter-spacing:1px;border:none;"
        )
        cl.addWidget(logo)
        cl.addSpacing(10)

        # Header
        title = QLabel("Buat admin pertama")
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        cl.addWidget(title)

        subtitle = QLabel("Mulai Warung+ dengan membuat akun admin utama")
        subtitle.setStyleSheet("font-size:12px;color:#888780;border:none;")
        cl.addWidget(subtitle)
        cl.addSpacing(16)

        cl.addWidget(Divider())
        cl.addSpacing(18)

        # ── Preview avatar (dinamis) ──────────────────────────────────────────
        avatar_row = QHBoxLayout()
        avatar_row.setSpacing(14)
        self._avatar = Avatar("?", bg_color="#F1EFE8", text_color="#888780")
        self._avatar.setStyleSheet("border: none; background: transparent;")
        avatar_row.addWidget(self._avatar)

        avatar_info = QVBoxLayout()
        avatar_info.setSpacing(2)
        self._preview_name = QLabel("Nama admin")
        self._preview_name.setStyleSheet(
            "font-size:14px; font-weight:500; color:#BBBAB6; font-family:'Segoe UI'; border:none;"
        )
        self._preview_role = QLabel("Admin")
        self._preview_role.setStyleSheet(
            "font-size:12px; color:#BBBAB6; font-family:'Segoe UI'; border:none;"
        )
        avatar_info.addWidget(self._preview_name)
        avatar_info.addWidget(self._preview_role)
        avatar_row.addLayout(avatar_info)
        avatar_row.addStretch()
        cl.addLayout(avatar_row)
        cl.addSpacing(18)

        # ── Nama Admin ────────────────────────────────────────────────────────
        self._name_input = NameInput("Nama", "Contoh: Budi Santoso")
        self._name_input.input.textChanged.connect(self._on_name_changed)
        cl.addWidget(self._name_input)
        cl.addSpacing(14)

        # ── PIN ───────────────────────────────────────────────────────────────
        self._pin_input = PinRow("PIN (6 digit)")
        cl.addWidget(self._pin_input)
        cl.addSpacing(14)

        # ── Konfirmasi PIN ────────────────────────────────────────────────────
        self._pin_confirm = PinRow("Konfirmasi PIN")
        cl.addWidget(self._pin_confirm)
        cl.addSpacing(22)

        # ── Tombol ────────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        simpan_btn = PrimaryButton("Buat Admin", on_click=self._handle_submit)

        btn_row.addWidget(simpan_btn)
        cl.addLayout(btn_row)
        cl.addSpacing(16)

        root.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    # ── Handlers ─────────────────────────────────────────────────────────────
    def _on_name_changed(self, text: str):
        """Update preview avatar & nama secara realtime."""
        text = text.strip()
        if text:
            # Ambil 1-2 huruf pertama nama
            parts = text.split()
            if len(parts) >= 2:
                initials = parts[0][0].upper() + parts[1][0].upper()
            else:
                initials = parts[0][:2].upper()

            # Pilih warna avatar sesuai urutan (reuse palet dari select_user)
            palettes = [
                ("#EEF0FD", "#3B52C4"),
                ("#FDF0EC", "#B04A28"),
                ("#E6F1FB", "#185FA5"),
                ("#EAF3DE", "#3B6D11"),
            ]
            idx = (ord(initials[0]) - ord('A')) % len(palettes)
            bg, fg = palettes[idx]

            self._avatar.bg_color = bg
            self._avatar.text_color = fg
            self._avatar.setText(initials)
            self._avatar.update()

            self._preview_name.setText(text)
            self._preview_name.setStyleSheet(
                "font-size:14px; font-weight:500; color:#1b1b1b; font-family:'Segoe UI'; border:none;"
            )
        else:
            self._avatar.bg_color = "#F1EFE8"
            self._avatar.text_color = "#888780"
            self._avatar.setText("?")
            self._avatar.update()
            self._preview_name.setText("Nama")
            self._preview_name.setStyleSheet(
                "font-size:14px; font-weight:500; color:#BBBAB6; font-family:'Segoe UI'; border:none;"
            )

    def _handle_back(self):
        if self.on_back:
            self.on_back()

    def _handle_submit(self):
        valid = True

        name = self._name_input.value().strip()
        pin = self._pin_input.value().strip()
        pin_confirm = self._pin_confirm.value().strip()

        # Reset error
        self._name_input.clearError()
        self._pin_input.clearError()
        self._pin_confirm.clearError()

        # Validasi nama
        if not name:
            self._name_input.showError("Nama admin tidak boleh kosong")
            valid = False

        # Validasi PIN harus tepat 6 digit angka
        if not pin.isdigit() or len(pin) != 6:
            self._pin_input.showError("PIN harus 6 digit angka")
            valid = False

        # Validasi konfirmasi PIN
        if pin != pin_confirm:
            self._pin_confirm.showError("Konfirmasi PIN tidak cocok")
            valid = False

        # Jika valid → kirim hanya name + pin
        if valid and self.on_success:
            self.on_success({
                "name": name,
                "pin": pin,
            })