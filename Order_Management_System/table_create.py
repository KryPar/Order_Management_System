import os
import psycopg2
from psycopg2 import sql

if __name__ == "__main__":
    print("-----TABLES WILL BE CREATED-----")
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DATABASE", "postgres"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )
    print("-----CONNECTED-----")
    with conn, conn.cursor() as cur:
        
        # Customer table
        create_customer_table_query = sql.SQL(
            """
            DROP TABLE IF EXISTS orders CASCADE;  -- Nejdříve odstraníme objednávky
            DROP TABLE IF EXISTS order_items CASCADE;  -- Poté odstraníme položky objednávek
            DROP TABLE IF EXISTS customer CASCADE;  -- Nakonec odstraníme zákazníky
            CREATE TABLE customer (
                customer_id SERIAL PRIMARY KEY,
                name VARCHAR(128),
                surname VARCHAR(128),
                contact VARCHAR(128)
            );
            """
        )
        print(create_customer_table_query.as_string(cur)) 
        cur.execute(create_customer_table_query)

        # Product table
        create_product_table_query = sql.SQL(
            """
            DROP TABLE IF EXISTS product CASCADE;  -- Přidání CASCADE pro odstranění závislostí
            CREATE TABLE product (
                product_id SERIAL PRIMARY KEY,
                name VARCHAR(128),
                price NUMERIC(10,2)
            );
            """
        )
        print(create_product_table_query.as_string(cur)) 
        cur.execute(create_product_table_query)

        # Orders table
        create_order_table_query = sql.SQL(
            """
            DROP TABLE IF EXISTS orders CASCADE;  -- Nejdříve odstraníme objednávky
            CREATE TABLE orders (
                order_id SERIAL PRIMARY KEY,
                customer_id INT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON DELETE CASCADE
            );
            """
        )
        print(create_order_table_query.as_string(cur)) 
        cur.execute(create_order_table_query)

        # Order items table
        create_order_items_table_query = sql.SQL(
            """
            DROP TABLE IF EXISTS order_items CASCADE;  -- Přidání CASCADE pro odstranění závislostí
            CREATE TABLE order_items (
                order_item_id SERIAL PRIMARY KEY,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT,
                price NUMERIC(10,2),
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES product(product_id)
            );
            """
        )
        print(create_order_items_table_query.as_string(cur)) 
        cur.execute(create_order_items_table_query)

    conn.close()
    print("-----TABLES CREATED-----")
 