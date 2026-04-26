# 03 - API Reference

Semua modul API menggunakan koneksi global dari `api/db_master.py`.

## db_master

- `connect_db(databaseFile)`
- `require_connection()`
- `init_db(databaseFile, sqlFile)`
- `init()`

## cashier

- `create_cashier(first_name, last_name, salary)`
- `read_cashier(cashier_id)`
- `update_cashier(cashier_id, first_name, last_name, salary)`
- `delete_cashier(cashier_id)`
- `list_cashiers()`

## customer

- `create_customer(name, phone=None)`
- `read_customer(customer_id)`
- `update_customer(customer_id, name, phone=None)`
- `delete_customer(customer_id)`
- `list_customers()`

## product

- `create_product(name, brand, stock, price)`
- `read_product(product_id)`
- `update_product(product_id, name, brand, stock, price)`
- `delete_product(product_id)`
- `list_products()`

## sales

- `create_sale(customer_id, cashier_id, time, payment, paid_amount)`
- `create_sale_return_id(customer_id, cashier_id, time, payment, paid_amount)`
- `read_sale(sale_id)`
- `update_sale(sale_id, customer_id, cashier_id, time, payment, paid_amount)`
- `delete_sale(sale_id)`
- `list_sales()`

## sales_detail

- `create_sales_detail(sales_id, product_id, quantity, discount=0.0)`
- `read_sales_detail(detail_id)`
- `update_sales_detail(detail_id, sales_id, product_id, quantity, discount=0.0)`
- `delete_sales_detail(detail_id)`
- `list_sales_details()`
