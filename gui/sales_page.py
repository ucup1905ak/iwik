import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from api.sales import create_sale_return_id
from api.sales_detail import create_sales_detail, list_sales_details
from utils.export_csv import export_to_csv
from utils.generate_pdf import generate_pdf_report


class SalesPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._detail_rows: list[tuple[int, int, float]] = []

        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        header_box = ttk.LabelFrame(main, text="Input Penjualan")
        header_box.pack(fill=tk.X, pady=(0, 10))

        self.customer_id_var = tk.StringVar()
        self.cashier_id_var = tk.StringVar()
        self.time_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.payment_var = tk.StringVar()
        self.paid_amount_var = tk.StringVar()

        self._build_labeled_entry(header_box, "Customer ID (opsional)", self.customer_id_var, 0, 0)
        self._build_labeled_entry(header_box, "Cashier ID", self.cashier_id_var, 0, 1)
        self._build_labeled_entry(header_box, "Time", self.time_var, 1, 0)
        self._build_labeled_entry(header_box, "Payment", self.payment_var, 1, 1)
        self._build_labeled_entry(header_box, "Paid Amount", self.paid_amount_var, 2, 0)

        detail_box = ttk.LabelFrame(main, text="Detail Barang")
        detail_box.pack(fill=tk.BOTH, expand=True)

        self.product_id_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.discount_var = tk.StringVar(value="0")

        self._build_labeled_entry(detail_box, "Product ID", self.product_id_var, 0, 0)
        self._build_labeled_entry(detail_box, "Quantity", self.quantity_var, 0, 1)
        self._build_labeled_entry(detail_box, "Discount", self.discount_var, 1, 0)

        ttk.Button(detail_box, text="Tambah Detail", command=self.add_detail_row).grid(
            row=1, column=1, padx=8, pady=6, sticky=tk.EW
        )

        self.detail_tree = ttk.Treeview(
            detail_box,
            columns=("ProductID", "Quantity", "Discount"),
            show="headings",
            height=8,
        )
        for col in ("ProductID", "Quantity", "Discount"):
            self.detail_tree.heading(col, text=col)
            self.detail_tree.column(col, width=120)

        self.detail_tree.grid(row=2, column=0, columnspan=2, sticky=tk.NSEW, padx=8, pady=(8, 6))
        detail_box.columnconfigure(0, weight=1)
        detail_box.columnconfigure(1, weight=1)
        detail_box.rowconfigure(2, weight=1)

        action_row = ttk.Frame(main)
        action_row.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(action_row, text="Hapus Detail Terpilih", command=self.remove_selected_detail).pack(side=tk.LEFT)
        ttk.Button(action_row, text="Simpan Penjualan", command=self.save_sale).pack(side=tk.RIGHT)

        history_box = ttk.LabelFrame(main, text="Sales Detail Tersimpan")
        history_box.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.saved_tree = ttk.Treeview(
            history_box,
            columns=("ID", "SalesID", "ProductID", "Quantity", "Discount"),
            show="headings",
            height=8,
        )
        for col in ("ID", "SalesID", "ProductID", "Quantity", "Discount"):
            self.saved_tree.heading(col, text=col)
            self.saved_tree.column(col, width=110)

        self.saved_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ttk.Button(main, text="Refresh Riwayat Detail", command=self.load_saved_details).pack(anchor=tk.E, pady=(6, 0))
        
        # Export buttons for Sales Details
        export_frame = ttk.Frame(main)
        export_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(export_frame, text="Ekspor Detail ke CSV", command=self.export_details_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Ekspor Detail ke PDF", command=self.export_details_pdf).pack(side=tk.LEFT, padx=5)
        
        self.load_saved_details()

    def _build_labeled_entry(self, parent, label_text: str, var: tk.StringVar, row: int, col: int) -> None:
        wrapper = ttk.Frame(parent)
        wrapper.grid(row=row, column=col, sticky=tk.EW, padx=8, pady=6)
        ttk.Label(wrapper, text=label_text).pack(anchor=tk.W)
        ttk.Entry(wrapper, textvariable=var).pack(fill=tk.X)
        parent.columnconfigure(col, weight=1)

    def add_detail_row(self) -> None:
        try:
            product_id = int(self.product_id_var.get())
            quantity = int(self.quantity_var.get())
            discount_text = self.discount_var.get().strip() or "0"
            discount = float(discount_text)

            if quantity <= 0:
                raise ValueError("Quantity harus lebih dari 0")

            self._detail_rows.append((product_id, quantity, discount))
            self.detail_tree.insert("", tk.END, values=(product_id, quantity, discount))

            self.product_id_var.set("")
            self.quantity_var.set("")
            self.discount_var.set("0")
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))

    def remove_selected_detail(self) -> None:
        selected = self.detail_tree.selection()
        if not selected:
            return

        indexes = [self.detail_tree.index(item) for item in selected]
        for item in selected:
            self.detail_tree.delete(item)

        for idx in sorted(indexes, reverse=True):
            if 0 <= idx < len(self._detail_rows):
                self._detail_rows.pop(idx)

    def save_sale(self) -> None:
        try:
            customer_text = self.customer_id_var.get().strip()
            cashier_id = int(self.cashier_id_var.get().strip())
            time_value = self.time_var.get().strip()
            payment = self.payment_var.get().strip() or None
            paid_text = self.paid_amount_var.get().strip()
            paid_amount = float(paid_text) if paid_text else None
            customer_id = int(customer_text) if customer_text else None

            if not self._detail_rows:
                raise ValueError("Minimal 1 detail barang")

            sale_id = create_sale_return_id(customer_id, cashier_id, time_value, payment, paid_amount)

            for product_id, quantity, discount in self._detail_rows:
                create_sales_detail(sale_id, product_id, quantity, discount)

            messagebox.showinfo("Sukses", f"Penjualan tersimpan. Sales ID: {sale_id}")
            self._clear_form_after_save()
            self.load_saved_details()
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
        except Exception as exc:
            messagebox.showerror("Save Error", str(exc))
    
    def _clear_form_after_save(self) -> None:
        """Clear the form after saving a sale"""
        self.customer_id_var.set("")
        self.cashier_id_var.set("")
        self.time_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.payment_var.set("")
        self.paid_amount_var.set("")
        self.product_id_var.set("")
        self.quantity_var.set("")
        self.discount_var.set("0")
        self._detail_rows.clear()
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
    
    def load_saved_details(self) -> None:
        """Load saved sales details into the tree"""
        for item in self.saved_tree.get_children():
            self.saved_tree.delete(item)
        try:
            details = list_sales_details()
            for detail in details:
                self.saved_tree.insert('', tk.END, values=detail)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data: {e}")
    
    def export_details_csv(self) -> None:
        """Export sales details to CSV"""
        try:
            details = list_sales_details()
            if not details:
                messagebox.showwarning("Warning", "Tidak ada data detail penjualan untuk diekspor")
                return
            
            # Add header
            headers = ['ID', 'SalesID', 'ProductID', 'Quantity', 'Discount']
            data = [headers] + list(details)
            
            success, message = export_to_csv(data, 'sales_details.csv')
            if success:
                messagebox.showinfo("Sukses", message)
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor CSV: {e}")
    
    def export_details_pdf(self) -> None:
        """Export sales details to PDF"""
        try:
            details = list_sales_details()
            if not details:
                messagebox.showwarning("Warning", "Tidak ada data detail penjualan untuk diekspor")
                return
            
            # Add header
            headers = [['ID', 'SalesID', 'ProductID', 'Quantity', 'Discount']]
            data = headers + [[str(val) if val is not None else '' for val in row] for row in details]
            
            success, message = generate_pdf_report(
                data,
                filename='assets/pdf/sales_details.pdf',
                title='Laporan Detail Penjualan'
            )
            if success:
                messagebox.showinfo("Sukses", message)
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor PDF: {e}")

    def _clear_form_after_save(self) -> None:
        self.customer_id_var.set("")
        self.cashier_id_var.set("")
        self.time_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.payment_var.set("")
        self.paid_amount_var.set("")
        self.product_id_var.set("")
        self.quantity_var.set("")
        self.discount_var.set("0")

        self._detail_rows.clear()
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)

    def load_saved_details(self) -> None:
        for item in self.saved_tree.get_children():
            self.saved_tree.delete(item)

        for row in list_sales_details():
            self.saved_tree.insert("", tk.END, values=row)
