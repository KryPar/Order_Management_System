import os
from postgres import Postgres

# Tabulky
CUSTOMER_TABLE = os.getenv("CUSTOMER_TABLE", "customer")
PRODUCT_TABLE = os.getenv("PRODUCT_TABLE", "product")
ORDER_TABLE = os.getenv("ORDER_TABLE", "orders")
ORDER_ITEMS_TABLE = os.getenv("ORDER_ITEMS_TABLE", "order_items")

# Připojení k databázi
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")


class InformationInfrastructure:
    def __init__(self, db_handler: Postgres):
        self.db_handler = db_handler

    # Retrieves the list of customers from the customer table.
    def get_customers(self):
        customers = self.db_handler.get_data_simple_condition(CUSTOMER_TABLE, ["customer_id", "name", "surname", "contact"])
        return customers

    # Inserts a new customer into the customer table.
    def insert_customers(self, data_dict):
        return self.db_handler.insert_data(CUSTOMER_TABLE, data_dict)

    # Retrieves the list of products from the product table.
    def get_products(self):
        products = self.db_handler.get_data_simple_condition(PRODUCT_TABLE, ["product_id", "name", "price"])
        return products

    # Inserts a new product into the product table.
    def insert_products(self, data_dict):
        self.db_handler.insert_data(PRODUCT_TABLE, data_dict)

    # Retrieves the list of orders from the orders table.
    def get_orders(self):
        orders = self.db_handler.get_data_simple_condition(ORDER_TABLE, ["order_id", "customer_id"])
        return orders

    # Inserts a new order into the orders table.
    def insert_order(self, customer_id):
        order_data = {
            "customer_id": customer_id
        }
        result = self.db_handler.insert_data(ORDER_TABLE, order_data)
        return result[0]  # Vracíme první položku z výsledku, což by měl být 'order_id'


    # Inserts a new order item into the order_items table.
    def insert_order_item(self, order_id, product_id, quantity, price):
        order_item_data = {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "price": price
        }
        self.db_handler.insert_data(ORDER_ITEMS_TABLE, order_item_data)

    # Retrieves the list of order items for a specific order, filtered by order_id.
    def get_order_items(self, order_id):
        order_items = self.db_handler.get_data_simple_condition(ORDER_ITEMS_TABLE, ["order_item_id", "order_id", "product_id", "quantity", "price"], "order_id", order_id)
        return order_items
    
    # Updates the total price of an order in the orders table.
    def update_order_price(self, order_id, total_price):
        update_query = {
            "total_price": total_price
        }
        condition = {
            "order_id": order_id
        }
        self.db_handler.update_data(ORDER_TABLE, update_query, condition)
