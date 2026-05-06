# gui/signals.py
"""
Global Signal Manager untuk sinkronisasi antar halaman
Menggunakan PyQt6 signals untuk reactive updates
"""

from PyQt6.QtCore import QObject, pyqtSignal
from controllers.product import Product


class ProductSignals(QObject):
    """Signals untuk perubahan data produk"""
    
    # Signal ketika produk ditambahkan
    product_added = pyqtSignal(Product)
    
    # Signal ketika produk diedit
    product_edited = pyqtSignal(Product)
    
    # Signal ketika produk dihapus
    product_deleted = pyqtSignal(int)  # product_id
    
    # Signal ketika stok produk berubah (biasanya saat transaksi)
    product_stock_changed = pyqtSignal(int, int)  # product_id, new_stock
    
    # Signal ketika multiple produk diimport
    products_imported = pyqtSignal(list)  # list of Product
    
    # Signal untuk reload semua produk
    products_reload = pyqtSignal()


class SalesSignals(QObject):
    """Signals untuk perubahan data penjualan"""
    
    # Signal ketika transaksi berhasil diproses
    sales_completed = pyqtSignal(int)  # sales_id


# Global instances - akses dari mana saja
product_signals = ProductSignals()
sales_signals = SalesSignals()
