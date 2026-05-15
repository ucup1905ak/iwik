from PyQt6.QtCore import QObject, pyqtSignal
from controllers.product import Product


class ProductSignals(QObject):
    """Signals untuk perubahan data produk"""
    
    product_added = pyqtSignal(Product)
    product_edited = pyqtSignal(Product)
    product_deleted = pyqtSignal(int)
    product_stock_changed = pyqtSignal(int, int)
    products_imported = pyqtSignal(list)
    products_reload = pyqtSignal()


class SalesSignals(QObject):
    """Signals untuk perubahan data penjualan"""
    
    sales_completed = pyqtSignal(int)


class PurchaseSignals(QObject):
    """Signals untuk perubahan data pembelian"""
    
    purchase_completed = pyqtSignal(int)


class ReceivablesSignals(QObject):
    """Signals untuk perubahan data piutang/receivables"""
    
    receivables_updated = pyqtSignal(int)
    receivables_paid = pyqtSignal(int)


class DashboardSignals(QObject):
    """Signals untuk update tampilan dashboard"""
    
    refresh_requested = pyqtSignal()


product_signals = ProductSignals()
sales_signals = SalesSignals()
purchase_signals = PurchaseSignals()
receivables_signals = ReceivablesSignals()
dashboard_signals = DashboardSignals()
