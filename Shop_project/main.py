import os
from postgres import Postgres
from information_infrastructure import InformationInfrastructure


pg_handler = Postgres(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    database=os.getenv("POSTGRES_DATABASE", "postgres"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD", "postgres"),
)

information_infrastructure = InformationInfrastructure(db_handler=pg_handler)

# This function prints the main menu for the user to select an option from.
def print_menu():
    print("Welcome to the system, please choose a number from the menu.")
    print("Menu choice:")
    print("\t Press 1 for list of customers")
    print("\t Press 2 for list of orders")
    print("\t Press 3 for list of products")
    print("\t Press 4 to create an order")
    print("\t Press 5 to create a new product")
    print("\t Press 6 to create a new customer")
    print("\t Press 7 to exit")

# This function allows the user to input details for a new customer.
def create_customer(information_infrastructure: InformationInfrastructure):
    print("Please fill in the details:")
    while True:
        try:
            name = input("Name: ")
            surname = input("Surname: ")
            contact = input("Tel. number: ")
        except Exception as e:
            print(e)
            print("Error during filling in the details. Please re-enter the details.")
            continue
        break
    information_infrastructure.insert_customers({"name": name, "surname": surname, "contact": contact})

# This function allows the user to input details for a new product.
def create_product(information_infrastructure: InformationInfrastructure):
    print("Please fill in the details:")
    while True:
        try:
            name = input("Product name: ")
            price = float(input("Product price: "))
        except Exception as e:
            print(e)
            print("Error during filling in the details. Please re-enter the details.")
            continue
        break
    information_infrastructure.insert_products({"name": name, "price": price})

# This function allows the user to create a new order.
def create_order(information_infrastructure: InformationInfrastructure):
    customers = information_infrastructure.get_customers()
    products = information_infrastructure.get_products()

    if not customers:
        print("Sorry, you need to have customers first.")
        return

    if not products:
        print("Sorry, there are no products available.")
        return
    
    print("Please fill in the details")
    while True:
        try:
            print("Select a customer:")
            for idx, customer in enumerate(customers):
                print(f"{idx}. {customer['name']} {customer['surname']}")
            customer_idx = int(input("Enter customer number: "))
            
            if customer_idx < 0 or customer_idx >= len(customers):
                print("Please select a valid customer.")
                continue
            
            customer_id = customers[customer_idx]['customer_id']
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    
    order_id = information_infrastructure.insert_order(customer_id)

    total_price = 0
    while True:
        try:
            print("Select a product:")
            for idx, product in enumerate(products):
                print(f"{idx}. {product['name']} (Price: {product['price']})")
            product_idx = int(input("Enter product number: "))
            
            if product_idx < 0 or product_idx >= len(products):
                print("Please select a valid product.")
                continue

            quantity = int(input("Enter quantity: "))
            if quantity <= 0:
                print("Please enter a valid quantity.")
                continue

            product_id = products[product_idx]['product_id']
            product_price = float(products[product_idx]['price'])
            total_item_price = product_price * quantity
            total_price += total_item_price

            #
            information_infrastructure.insert_order_item(order_id, product_id, quantity, total_item_price)
            
            add_more = input("Do you want to add another product? (y/n): ")
            if add_more.lower() != 'y':
                break
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    
    information_infrastructure.update_order_price(order_id, total_price)
    print(f"Order created successfully with total price: {total_price}")

# This function retrieves and displays a list of all customers from the database
def list_customers(information_infrastructure: InformationInfrastructure):
    customers = information_infrastructure.get_customers()
    if customers:
        print("List of customers:")
        for customer in customers:
            print(f"ID: {customer['customer_id']}, Name: {customer['name']} {customer['surname']}, Contact: {customer['contact']}")
    else:
        print("No customers found.")

# This function retrieves and displays a list of all products from the database.
def list_products(information_infrastructure: InformationInfrastructure):
    products = information_infrastructure.get_products()
    if products:
        print("List of products:")
        for product in products:
            print(f"ID: {product['product_id']}, Name: {product['name']}, Price: {product['price']}")
    else:
        print("No products found.")

# This function retrieves and displays a list of all orders from the database.
def list_orders(information_infrastructure: InformationInfrastructure):
    orders = information_infrastructure.get_orders()
    if orders:
        print("List of orders:")
        for order in orders:
            print(f"Order ID: {order['order_id']}, Customer ID: {order['customer_id']}")
            order_items = information_infrastructure.get_order_items(order['order_id'])
            for item in order_items:
                print(f"\tProduct ID: {item['product_id']}, Quantity: {item['quantity']}, Price: {item['price']}")
    else:
        print("No orders found.")

if __name__ == "__main__":
    while True:
        print_menu()
        try:
            answer = int(input("\tYour choice: "))
            if answer < 1 or answer > 7:
                print("Invalid choice. Please try again.")
                continue
        except Exception as e:
            print(f"Input error: {e}")
            continue

        if answer == 1:
            list_customers(information_infrastructure)
        elif answer == 2:
            list_orders(information_infrastructure)
        elif answer == 3:
            list_products(information_infrastructure)
        elif answer == 4:
            create_order(information_infrastructure)
        elif answer == 5:
            create_product(information_infrastructure)
        elif answer == 6:
            create_customer(information_infrastructure)
        elif answer == 7:
            print("\tGoodbye!")
            break
