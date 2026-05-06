# gui/views/screens/import_export_dialog.py
"""
Custom Import/Export Dialog untuk halaman Produk
Mengikuti tema UI Warung+ dengan rounded corners, warna primer biru, etc
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QFileDialog, QMessageBox, QProgressBar, QWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from utils.generate_xlsx import export_to_xlsx, import_from_xlsx
import os


# ── Color palette (from product_page.py) ──
C_BG       = "#F4F5F9"
C_WHITE    = "#FFFFFF"
C_ACCENT   = "#4F6EF7"
C_ACCENT_H = "#3A57E8"
C_TEXT_PRI = "#1A1D2E"
C_TEXT_SEC = "#6B6F80"
C_BORDER   = "#E4E6EE"
C_DANGER   = "#E05252"
C_SUCCESS  = "#27AE60"
C_TAG_BG   = "#EEF1FE"
C_TAG_TEXT = "#4F6EF7"


class ImportExportDialog(QDialog):
    """Custom dialog untuk import/export dengan tema Warung+"""
    
    RESULT_IDLE = 0
    RESULT_SUCCESS = 1
    RESULT_ERROR = 2
    RESULT_CANCELLED = 3
    
    def __init__(self, dialog_type: str = "export", products_data: list = None, parent=None):
        """
        Args:
            dialog_type: 'export' atau 'import'
            products_data: data produk (untuk export)
        """
        super().__init__(parent)
        self.dialog_type = dialog_type
        self.products_data = products_data or []
        self.result_status = self.RESULT_IDLE
        self.result_message = ""
        self.imported_data = []
        
        self.setWindowTitle("Export Produk" if dialog_type == "export" else "Import Produk")
        self.setModal(True)
        self.setFixedWidth(500)
        self.setMinimumHeight(480)
        self.setMaximumHeight(650)
        self.setStyleSheet(f"QDialog {{ background: {C_WHITE}; font-family: 'Segoe UI'; font-size: 12px; }}")
        
        self._build_ui()
        
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # ── Header ──
        header = QFrame()
        header.setStyleSheet(f"QFrame {{ background-color: #FAFAF8; }}")
        header_lay = QVBoxLayout(header)
        header_lay.setContentsMargins(36, 30, 36, 0)
        header_lay.setSpacing(0)
        
        logo = QLabel("Warung<span style='color:#4F6EF7'>+</span>")
        logo.setTextFormat(Qt.TextFormat.RichText)
        logo.setStyleSheet("font-size:14px;color:#5F5E5A;font-weight:500;letter-spacing:1px;border:none;")
        header_lay.addWidget(logo)
        header_lay.addSpacing(15)
        
        if self.dialog_type == "export":
            title = QLabel("Export Produk ke Excel")
            subtitle = QLabel("Simpan data produk sebagai file Excel untuk backup atau analisis.")
        else:
            title = QLabel("Import Produk dari Excel")
            subtitle = QLabel("Baca data produk dari file Excel dan tambahkan ke sistem.")
        
        title.setStyleSheet("font-size:20px;font-weight:600;color:#1b1b1b;border:none;")
        subtitle.setStyleSheet("font-size:12px;color:#888780;border:none;")
        
        header_lay.addWidget(title)
        header_lay.addSpacing(5)
        header_lay.addWidget(subtitle)
        header_lay.addSpacing(16)
        
        root.addWidget(header)
        
        # ── Content ──
        content = QWidget()
        content.setStyleSheet(f"background: #FAFAF8;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(36, 0, 36, 30)
        cl.setSpacing(0)
        
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: #DDD9D2; border: none;")
        cl.addWidget(divider)
        cl.addSpacing(24)
        
        # ── Status area ──
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background:    {C_TAG_BG};
                border:        1px solid {C_ACCENT};
                border-radius: 10px;
            }}
            QLabel {{
                background: transparent;
                border:     none;
            }}
        """)
        status_lay = QVBoxLayout(status_frame)
        status_lay.setContentsMargins(16, 16, 16, 16)
        status_lay.setSpacing(8)
        
        if self.dialog_type == "export":
            icon_lbl = QLabel("📤")
            icon_lbl.setStyleSheet("font-size: 32px; background: transparent;")
            status_lay.addWidget(icon_lbl)
            
            msg = QLabel(f"Siap export {len(self.products_data)} produk")
            msg.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {C_ACCENT};")
            status_lay.addWidget(msg)
            
            desc = QLabel("File Excel akan disimpan di folder Assets → XLSX")
            desc.setWordWrap(True)
            desc.setStyleSheet(f"font-size: 12px; color: {C_TEXT_SEC};")
            status_lay.addWidget(desc)
        else:
            icon_lbl = QLabel("📥")
            icon_lbl.setStyleSheet("font-size: 32px; background: transparent;")
            status_lay.addWidget(icon_lbl)
            
            msg = QLabel("Pilih file Excel untuk diimport")
            msg.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {C_ACCENT};")
            status_lay.addWidget(msg)
            
            desc = QLabel("Format: .xlsx dengan kolom: nama, brand, sku, kategori, harga, stok")
            desc.setWordWrap(True)
            desc.setStyleSheet(f"font-size: 12px; color: {C_TEXT_SEC};")
            status_lay.addWidget(desc)
        
        cl.addWidget(status_frame)
        cl.addSpacing(24)
        
        # ── Progress (hidden by default) ──
        self._progress = QProgressBar()
        self._progress.setFixedHeight(8)
        self._progress.setStyleSheet(f"""
            QProgressBar {{
                background:    {C_BORDER};
                border:        none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: {C_ACCENT};
                border-radius: 4px;
            }}
        """)
        self._progress.setVisible(False)
        cl.addWidget(self._progress)
        
        # ── Result area (hidden by default) ──
        self._result_frame = QFrame()
        self._result_frame.setStyleSheet(f"""
            QFrame {{
                background:    #E8F8F0;
                border:        1px solid {C_SUCCESS};
                border-radius: 10px;
            }}
            QLabel {{
                background: transparent;
                border:     none;
            }}
        """)
        result_lay = QVBoxLayout(self._result_frame)
        result_lay.setContentsMargins(16, 16, 16, 16)
        result_lay.setSpacing(8)
        
        result_icon = QLabel("✓")
        result_icon.setStyleSheet(f"font-size: 28px; color: {C_SUCCESS}; background: transparent;")
        result_lay.addWidget(result_icon)
        
        self._result_title = QLabel("")
        self._result_title.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {C_TEXT_PRI};")
        result_lay.addWidget(self._result_title)
        
        self._result_desc = QLabel("")
        self._result_desc.setWordWrap(True)
        self._result_desc.setStyleSheet(f"font-size: 12px; color: {C_TEXT_SEC};")
        result_lay.addWidget(self._result_desc)
        
        self._result_frame.setVisible(False)
        cl.addWidget(self._result_frame)
        
        root.addWidget(content)
        
        # ── Footer ──
        footer = QFrame()
        footer.setStyleSheet(f"QFrame {{ background-color: #FAFAF8; }}")
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(36, 0, 36, 30)
        footer_lay.setSpacing(10)
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #5F5E5A;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 500;
                border-radius: 10px; border: 1px solid #DDD9D2;
            }
            QPushButton:hover { background: #F1EFE8; border: 1px solid #C8C6BF; }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        self._action_btn = QPushButton(
            "📤 Export Sekarang" if self.dialog_type == "export" else "📥 Pilih File"
        )
        self._action_btn.setFixedHeight(40)
        self._action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._action_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_ACCENT}; color: #FFFFFF;
                font-family: 'Segoe UI'; font-size: 13px; font-weight: 600;
                border-radius: 10px; border: none;
            }}
            QPushButton:hover {{ background: {C_ACCENT_H}; }}
        """)
        
        if self.dialog_type == "export":
            self._action_btn.clicked.connect(self._do_export)
        else:
            self._action_btn.clicked.connect(self._do_import)
        
        footer_lay.addWidget(cancel_btn)
        footer_lay.addWidget(self._action_btn)
        root.addWidget(footer)
    
    def _do_export(self):
        """Proses export ke Excel"""
        try:
            if not self.products_data:
                QMessageBox.warning(self, "Export", "Tidak ada produk untuk diekspor.")
                return
            
            # Show progress
            self._action_btn.setEnabled(False)
            
            success, message = export_to_xlsx(self.products_data)
            
            if success:
                # Show result
                self._show_result(success=True, message=message)
                self.result_status = self.RESULT_SUCCESS
                self.result_message = message
                
                # Optional: open folder
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                xlsx_dir = os.path.join(base_path, 'assets', 'xlsx')
                xlsx_dir = os.path.abspath(xlsx_dir)
                
                # Schedule close after 2 seconds
                QTimer.singleShot(2000, self.accept)
            else:
                self._show_result(success=False, message=message)
                self.result_status = self.RESULT_ERROR
                self.result_message = message
                self._action_btn.setEnabled(True)
                
        except Exception as e:
            self._show_result(success=False, message=f"Terjadi kesalahan: {str(e)}")
            self.result_status = self.RESULT_ERROR
            self.result_message = str(e)
            self._action_btn.setEnabled(True)
    
    def _do_import(self):
        """Proses import dari Excel"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Pilih File Excel untuk Import",
                "",
                "Excel Files (*.xlsx);;All Files (*.*)"
            )
            
            if not file_path:
                self.result_status = self.RESULT_CANCELLED
                return
            
            # Show progress
            self._action_btn.setEnabled(False)
            self._progress.setVisible(True)
            self._progress.setValue(50)
            
            success, products_data, message = import_from_xlsx(file_path)
            
            self._progress.setValue(100)
            
            if success:
                self.imported_data = products_data
                self._show_result(success=True, message=f"Siap import {len(products_data)} produk")
                self.result_status = self.RESULT_SUCCESS
                self.result_message = message
                
                # Change button to "Confirm Import"
                self._action_btn.setText("✓ Konfirmasi Import")
                self._action_btn.clicked.disconnect()
                self._action_btn.clicked.connect(self.accept)
                self._action_btn.setEnabled(True)
            else:
                self._show_result(success=False, message=message)
                self.result_status = self.RESULT_ERROR
                self.result_message = message
                self._action_btn.setEnabled(True)
                self._progress.setVisible(False)
                
        except Exception as e:
            self._show_result(success=False, message=f"Terjadi kesalahan: {str(e)}")
            self.result_status = self.RESULT_ERROR
            self.result_message = str(e)
            self._action_btn.setEnabled(True)
            self._progress.setVisible(False)
    
    def _show_result(self, success: bool, message: str):
        """Tampilkan result di status frame"""
        if success:
            bg = "#E8F8F0"
            border = C_SUCCESS
            icon = "✓"
            color = C_SUCCESS
            title = "Berhasil" if self.dialog_type == "export" else "File Valid"
        else:
            bg = "#FDEAEA"
            border = C_DANGER
            icon = "✗"
            color = C_DANGER
            title = "Gagal" if self.dialog_type == "export" else "File Tidak Valid"
        
        self._result_frame.setStyleSheet(f"""
            QFrame {{
                background:    {bg};
                border:        1px solid {border};
                border-radius: 10px;
            }}
            QLabel {{
                background: transparent;
                border:     none;
            }}
        """)
        
        # Update result display
        for i in range(self._result_frame.layout().count()):
            widget = self._result_frame.layout().itemAt(i).widget()
            if isinstance(widget, QLabel):
                if widget.text() == "" or len(widget.text()) == 1:
                    if len(widget.text()) == 1:  # Icon
                        widget.setText(icon)
                        widget.setStyleSheet(f"font-size: 28px; color: {color}; background: transparent;")
                        break
        
        self._result_title.setText(title)
        self._result_title.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {color};")
        
        self._result_desc.setText(message)
        self._result_frame.setVisible(True)
