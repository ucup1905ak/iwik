from api.db_master import init

from api.cashier import list_cashiers
from api.customer import list_customers
from api.product import list_products
from api.sales import list_sales
from api.sales_detail import list_sales_details

if __name__ == "__main__":
    init()

    print("Cashier:", len(list_cashiers()))
    print("Customer:", len(list_customers()))
    print("Product:", len(list_products()))
    print("Sales:", len(list_sales()))
    print("SalesDetail:", len(list_sales_details()))
    
    
