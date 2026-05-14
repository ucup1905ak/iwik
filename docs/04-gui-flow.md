# GUI Flow & Navigation Map

This document explains how the graphical user interface components connect and route within the Warung+ application.

## 1. Application Shell Structure
The application adopts an overarching container using a shell structure.
- **`AppShell`**: Determines whether the user sees the Authentication flow or the Main Workspace.
- **`MainShell`**: The root of the logged-in workspace. Holds the persistent state, the Sidebar, and renders active pages.

## 2. Global Navigation (Sidebar)
The Sidebar allows switching between core application views:
1. **Dashboard** (`dashboard_page.py`)
2. **Products** (`product_page.py`)
3. **Suppliers** (`supplier_page.py`)
4. **Purchases** (`purchases_page.py`)
5. **Sales (POS)** (`sales_page.py`)
6. **Transactions** (`transactions_page.py`)
7. **Receivables** (`receivables_page.py`)
8. **Reports** (`reports_page.py`)
9. **Users** (`user_page.py`)

## 3. Standard Interface Patterns
Most data administration pages (Products, Suppliers, Customers) follow a similar layout:
- **Top Actions Bar**: Search input, "+ Add New" button.
- **Data View**: A `QTableWidget` filling the horizontal space.
- **Action Column**: Inside the table, rows have edit/delete buttons triggering action specific `QDialog`s.

## 4. Window Modals & Dialogs 
Actions such as Adding or Editing open custom popup modals centered on the screen overlaying a drop shadow to focus the user's attention.