# Application Functionality and Features Documentation

This document outlines the core functionalities available in the Warung+ application, mapping each feature to its corresponding graphical user interface (GUI) screen and underlying logic.

## 1. Authentication & Session Management
- **Splash Screen** (`splash_screen.py`): The entry point of the application. Handles initial loading, database connection checks, and application initialization.
- **Select User Screen** (`select_user_screen.py`): Displays a list of available users (cashiers/admins) based on database records. Allows quick selection via avatars.
- **Login Screen** (`login_screen.py`): Handles user authentication using a secure pin/password system. Verifies credentials before granting access to the main application shell.
- **Add Admin Screen** (`add_admin_screen.py`): Initial setup wizard that allows the creation of the first administrator account if no users exist in the database.

## 2. Main Dashboard & Navigation
- **App Shell & Main Shell** (`app_shell.py`, `main_shell.py`): The master layouts that hold the sidebar navigation and the active workspace. Manages switching between different screens.
- **Dashboard** (`dashboard_page.py`): The main landing page post-login. Displays high-level metrics, recent activities, and key summary statistics for the business (e.g., today's sales, low stock alerts).

## 3. Inventory Management (Products)
- **Product Page** (`product_page.py`):
  - **View Products**: Displays a tabulated list of all inventory items, including stock levels, purchase prices, and selling prices.
  - **Add/Edit Product**: Dialogs for inputting product details, including linking images and assigning categories or barcodes.
  - **Stock Management**: Helps monitor which products are running low on stock.
  - **Delete Product**: Allows authorized users to remove products from the system with confirmation prompts.

## 4. Supply Chain (Suppliers & Purchases)
- **Supplier Page** (`supplier_page.py`):
  - **Manage Suppliers**: Allows adding, editing, and deleting supplier profiles (name, contact info, address).
  - **Supplier Directory**: Tabular view to search and filter through supplier records.
- **Purchases Page** (`purchases_page.py`):
  - **Record Restocks**: Logs incoming inventory restocks linked to specific suppliers.
  - **Purchase Details**: Tracks the specific items, quantities, and cost prices of goods acquired to update the general inventory accurately.
  - **Historical View**: Grid view of past purchase orders and their statuses.

## 5. Point of Sale (Sales & Transactions)
- **Sales Page** (`sales_page.py`):
  - **Cashier Interface**: The primary POS interface for ringing up customer orders.
  - **Cart Management**: Add items to a cart, adjust quantities, and calculate totals, taxes, and discounts.
  - **Checkout**: Processes the final transaction and deducts sold quantities from the main product inventory.
- **Transactions/History Page** (`transactions_page.py`):
  - **Audit Trail**: Lists all completed sales transactions.
  - **Receipts**: Ability to view details of past transactions for refunds or reprints.

## 6. Financials (Receivables & Reports)
- **Receivables Page** (`receivables_page.py`):
  - **Debt/Credit Tracking**: Tracks unpaid or partially paid transactions (accounts receivable) for loyal customers or specific accounts.
  - **Payment Logging**: Allows logging partial or full payments against specific debts.
- **Reports Page** (`reports_page.py`):
  - **Business Intelligence**: Generates sales charts, profit margins, and performance metrics over defined time periods (daily, weekly, monthly).
  - **Analytics**: Identifies best-selling products and overall revenue trends.

## 7. Administrative Tools
- **User Management Page** (`user_page.py`):
  - **Manage Roles**: Allows admins to create, edit, or delete user accounts.
  - **Permissions**: Defines roles (e.g., Admin vs. Cashier) and controls access to sensitive pages like Reports or User Management.
- **Data Import/Export** (`import_export_dialog.py`):
  - **CSV Integration**: Dialog interfaces to batch import products from CSV/XLSX or export sales data for external accounting.
  - **Database Backup**: Provides functionality to export current database metrics.

---
*Note: All pages inherit a uniform design system powered by PyQt6, utilizing custom CSS/styling strings, responsive table widgets, and modular dialogs for a cohesive user experience.*