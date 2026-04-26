import tkinter as tk
from tkinter import ttk, messagebox
import api.db_master

from api.cashier import list_cashiers, create_cashier, delete_cashier
from api.customer import list_customers, create_customer, delete_customer
from api.product import list_products, create_product, delete_product
from gui.sales_page import SalesPage

class DataTable(ttk.Frame):
    def __init__(self, parent, columns, list_func, delete_func, add_fields=None, add_func=None):
        super().__init__(parent)
        self.list_func = list_func
        self.delete_func = delete_func
        self.add_fields = add_fields or []
        self.add_func = add_func

        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        form_frame = ttk.Frame(self)
        form_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        ttk.Button(form_frame, text="Refresh", command=self.load_data).pack(fill=tk.X, pady=(0, 20))

        self.entries = {}
        if self.add_func and self.add_fields:
            ttk.Label(form_frame, text="Add New Item", font=("Arial", 12, "bold")).pack(pady=(0, 10))
            for field in self.add_fields:
                ttk.Label(form_frame, text=field).pack(anchor=tk.W)
                ent = ttk.Entry(form_frame)
                ent.pack(fill=tk.X, pady=(0, 5))
                self.entries[field] = ent
            
            ttk.Button(form_frame, text="Add", command=self.on_add).pack(fill=tk.X, pady=(10, 20))

        ttk.Button(form_frame, text="Delete Selected", command=self.on_delete).pack(fill=tk.X)

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            records = self.list_func()
            for record in records:
                self.tree.insert('', tk.END, values=record)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")

    def on_add(self):
        try:
            values = []
            for field in self.add_fields:
                val = self.entries[field].get()
                # Extremely primitive type casting handling
                if val.replace('.','',1).isdigit():
                    val = float(val) if '.' in val else int(val)
                elif val == "":
                    val = None
                values.append(val)
            self.add_func(*values)
            self.load_data()
            for ent in self.entries.values():
                ent.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error adding item", str(e))

    def on_delete(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        item_id = self.tree.item(selected[0])['values'][0]
        try:
            self.delete_func(item_id)
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error deleting item", str(e))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Iwik Store Manager")
        self.geometry("800x500")

        # Initialize the database connection for the API
        api.db_master.init()

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tab_customer = DataTable(
            notebook, 
            columns=('ID', 'Name', 'Phone'), 
            list_func=list_customers, 
            delete_func=delete_customer,
            add_fields=['Name', 'Phone'],
            add_func=create_customer
        )
        notebook.add(tab_customer, text='Customers')

        tab_product = DataTable(
            notebook, 
            columns=('ID', 'Name', 'Brand', 'Stock', 'Price'), 
            list_func=list_products, 
            delete_func=delete_product,
            add_fields=['Name', 'Brand', 'Stock', 'Price'],
            add_func=create_product
        )
        notebook.add(tab_product, text='Products')

        tab_cashier = DataTable(
            notebook, 
            columns=('ID', 'First Name', 'Last Name', 'Salary'), 
            list_func=list_cashiers, 
            delete_func=delete_cashier,
            add_fields=['First Name', 'Last Name', 'Salary'],
            add_func=create_cashier
        )
        notebook.add(tab_cashier, text='Cashiers')

        tab_sales_input = SalesPage(notebook)
        notebook.add(tab_sales_input, text='Input Penjualan')

if __name__ == "__main__":
    app = App()
    app.mainloop()
