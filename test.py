from __future__ import annotations

import os
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox
from tkinter import ttk

from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "data.sqlite")
DB_URL = f"sqlite:///{DB_PATH}"  # file-based SQLite in the project folder


def _migrate_old_db_name_if_needed() -> None:
    old_path = os.path.join(APP_DIR, "app.db")
    if os.path.exists(old_path) and not os.path.exists(DB_PATH):
        try:
            os.replace(old_path, DB_PATH)
        except PermissionError:
            # Old DB may be locked by another running process.
            # Keep going; the app will use data.sqlite.
            pass


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, default="")


_migrate_old_db_name_if_needed()

engine = create_engine(DB_URL, echo=False, future=True)
Base.metadata.create_all(engine)


@dataclass(frozen=True)
class ContactInput:
    name: str
    email: str


def _clean_input(name: str, email: str) -> ContactInput:
    name = (name or "").strip()
    email = (email or "").strip()
    if not name:
        raise ValueError("Name is required")
    return ContactInput(name=name, email=email)


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"SQLite CRUD ({os.path.basename(DB_PATH)})")
        self.minsize(720, 420)

        self._selected_id: int | None = None

        self._build_ui()
        self.refresh_table()

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        form = ttk.LabelFrame(container, text="Contact", padding=12)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Name").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        ttk.Label(form, text="Email").grid(row=1, column=0, sticky=tk.W, padx=(0, 8))

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()

        self.name_entry = ttk.Entry(form, textvariable=self.name_var, width=50)
        self.email_entry = ttk.Entry(form, textvariable=self.email_var, width=50)

        self.name_entry.grid(row=0, column=1, sticky=tk.W)
        self.email_entry.grid(row=1, column=1, sticky=tk.W)

        btns = ttk.Frame(form)
        btns.grid(row=0, column=2, rowspan=2, sticky=tk.NS, padx=(12, 0))

        ttk.Button(btns, text="Create", command=self.create_contact).pack(fill=tk.X)
        ttk.Button(btns, text="Update", command=self.update_contact).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(btns, text="Delete", command=self.delete_contact).pack(fill=tk.X, pady=(8, 0))
        ttk.Button(btns, text="Clear", command=self.clear_form).pack(fill=tk.X, pady=(8, 0))

        form.columnconfigure(1, weight=1)

        table_frame = ttk.LabelFrame(container, text="Contacts", padding=12)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        columns = ("id", "name", "email")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("email", text="Email")

        self.tree.column("id", width=70, anchor=tk.W, stretch=False)
        self.tree.column("name", width=220, anchor=tk.W)
        self.tree.column("email", width=320, anchor=tk.W)

        yscroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        bottom = ttk.Frame(container)
        bottom.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(bottom, text="Refresh", command=self.refresh_table).pack(side=tk.LEFT)
        ttk.Label(
            bottom,
            text=f"Database: {os.path.basename(DB_PATH)}",
        ).pack(side=tk.RIGHT)

    def _session(self) -> Session:
        return Session(engine)

    def refresh_table(self) -> None:
        try:
            with self._session() as session:
                rows = session.execute(select(Contact).order_by(Contact.id.desc())).scalars().all()

            self.tree.delete(*self.tree.get_children())
            for c in rows:
                self.tree.insert("", tk.END, values=(c.id, c.name, c.email))
        except SQLAlchemyError as ex:
            messagebox.showerror("DB Error", str(ex))

    def clear_form(self) -> None:
        self._selected_id = None
        self.name_var.set("")
        self.email_var.set("")
        self.tree.selection_remove(self.tree.selection())
        self.name_entry.focus_set()

    def on_select(self, _event: object) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        values = item.get("values")
        if not values:
            return

        contact_id, name, email = values
        self._selected_id = int(contact_id)
        self.name_var.set(str(name))
        self.email_var.set(str(email))

    def create_contact(self) -> None:
        try:
            data = _clean_input(self.name_var.get(), self.email_var.get())
        except ValueError as ex:
            messagebox.showwarning("Validation", str(ex))
            return

        try:
            with self._session() as session:
                contact = Contact(name=data.name, email=data.email)
                session.add(contact)
                session.commit()
        except SQLAlchemyError as ex:
            messagebox.showerror("DB Error", str(ex))
            return

        self.clear_form()
        self.refresh_table()

    def update_contact(self) -> None:
        if self._selected_id is None:
            messagebox.showinfo("Update", "Select a row first")
            return

        try:
            data = _clean_input(self.name_var.get(), self.email_var.get())
        except ValueError as ex:
            messagebox.showwarning("Validation", str(ex))
            return

        try:
            with self._session() as session:
                contact = session.get(Contact, self._selected_id)
                if contact is None:
                    messagebox.showwarning("Update", "Selected row no longer exists")
                    self.refresh_table()
                    self.clear_form()
                    return

                contact.name = data.name
                contact.email = data.email
                session.commit()
        except SQLAlchemyError as ex:
            messagebox.showerror("DB Error", str(ex))
            return

        self.refresh_table()

    def delete_contact(self) -> None:
        if self._selected_id is None:
            messagebox.showinfo("Delete", "Select a row first")
            return

        if not messagebox.askyesno("Confirm", "Delete selected contact?"):
            return

        try:
            with self._session() as session:
                contact = session.get(Contact, self._selected_id)
                if contact is None:
                    messagebox.showwarning("Delete", "Selected row no longer exists")
                else:
                    session.delete(contact)
                    session.commit()
        except SQLAlchemyError as ex:
            messagebox.showerror("DB Error", str(ex))
            return

        self.clear_form()
        self.refresh_table()


def main() -> None:
    try:
        app = App()
        app.mainloop()
    except Exception as ex:  # last-resort UI error
        messagebox.showerror("Fatal error", str(ex))


if __name__ == "__main__":
    main()
