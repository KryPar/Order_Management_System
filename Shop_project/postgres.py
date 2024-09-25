import psycopg2
import psycopg2.extras
import traceback
from psycopg2 import sql

class Postgres:
    def __init__(self, host, database, user, password, debug=False):
        self.connection=None
        self.host=host
        self.database=database
        self.user=user
        self.password=password
        self.debug=debug
    
    # Establishes a connection to the PostgreSQL database using the stored parameters.
    def connect(self):
        self.connection = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )
        if self.debug:
            print("Connected")

    # Inserts a new row of data into the specified table.
    def insert_data(self, table_name, data_dict):
        if self.connection is None or self.connection.closed:
            print("Attempting to connect to the database...")
            self.connect()  # Zkontroluj, že se úspěšně připojuje

        keys = data_dict.keys()
        values = data_dict.values()

        insert_query = sql.SQL(
            "INSERT INTO {} ({}) VALUES ({}) RETURNING *;"
        ).format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, keys)),
            sql.SQL(', ').join(sql.Placeholder() * len(values))
        )

        try:
            with self.connection.cursor() as cur:
                print(f"Insert query: {insert_query.as_string(cur)}")
                print(f"Values: {tuple(values)}")
                cur.execute(insert_query, tuple(values))
                inserted = cur.fetchone()
                self.connection.commit()
                return inserted
        except Exception as e:
            print(f"Error during insert: {e}")
            raise

    # Inserts a new order for the specified customer, along with the associated order items.
    def insert_order_with_items(self, customer_id, items):
        if self.connection is None or self.connection.closed:
            self.connect()
        with self.connection, self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            try:
                # Vložení nové objednávky
                order_query = sql.SQL(
                    """
                    INSERT INTO orders (customer_id)
                    VALUES (%s)
                    RETURNING order_id;
                    """
                )
                cur.execute(order_query, (customer_id,))
                order_id = cur.fetchone()['order_id']

                total_price = 0
                for item in items:
                    product_id = item['product_id']
                    quantity = item['quantity']
                    price = item['price']
                    total_item_price = quantity * price
                    total_price += total_item_price

                    # Vložení položek objednávky
                    item_query = sql.SQL(
                        """
                        INSERT INTO order_items (order_id, product_id, quantity, price)
                        VALUES (%s, %s, %s, %s);
                        """
                    )
                    cur.execute(item_query, (order_id, product_id, quantity, price))

                # Aktualizace celkové ceny objednávky
                update_order_query = sql.SQL(
                    """
                    UPDATE orders
                    SET total_price = %s
                    WHERE order_id = %s;
                    """
                )
                cur.execute(update_order_query, (total_price, order_id))

                self.connection.commit()
                return order_id

            except Exception as e:
                self.connection.rollback()
                traceback.print_exc()
                print(f"Fail during insert_order_with_items {e}")
        self.connection.close()

    # Retrieves data from the specified table based on optional conditions.
    def get_data_simple_condition(self, table_name, columns=[], target_column=None, target_value=None):
        result = []
        if self.connection is None or self.connection.closed:
            self.connect()
        
        with self.connection, self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            try:
                if target_column is None:
                    select_query = sql.SQL(
                        """
                        SELECT {} 
                        FROM {}
                        """
                    ).format(
                        sql.SQL(',').join(map(sql.Identifier, columns)),
                        sql.Identifier(table_name),
                    )
                else:
                    select_query = sql.SQL(
                        """
                        SELECT {} 
                        FROM {}
                        WHERE {} = {}
                        """
                    ).format(
                        sql.SQL(',').join(map(sql.Identifier, columns)),
                        sql.Identifier(table_name),
                        sql.Identifier(target_column),
                        sql.Literal(target_value)
                    )
                if self.debug:
                    print(select_query.as_string(cur))  # Pre kontrolu
                cur.execute(select_query)
                result = cur.fetchall()
            except Exception as e:
                traceback.print_exc()
                print(f"Fail during get_data_simple_condition {e}")
        self.connection.close()
        return result

    # Performs a SQL JOIN between two tables using a common column.
    def get_join_results(self, table_name_a, table_name_b, join_coulmn_name_a, join_coulmn_name_b=None):
        result = []
        join_coulmn_name_b = join_coulmn_name_b or join_coulmn_name_a
        if self.connection is None or self.connection.closed:
            self.connect()
        
        with self.connection, self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            try:
                join_query = sql.SQL(
                    """
                    SELECT *
                    FROM {}
                    JOIN {} ON {}.{} = {}.{}
                    """
                ).format(
                    sql.Identifier(table_name_a),
                    sql.Identifier(table_name_b),
                    sql.Identifier(table_name_a),
                    sql.Identifier(join_coulmn_name_a),
                    sql.Identifier(table_name_b),
                    sql.Identifier(join_coulmn_name_b),
                )
                if self.debug:
                    print(join_query.as_string(cur))
                cur.execute(join_query)
                result = cur.fetchall()
            except Exception as e:
                traceback.print_exc()
                print(f"Fail during get_join_results {e}")
        self.connection.close()
        return result
    
    # Updates records in the specified table based on a given condition.
    def update_data(self, table_name, update_dict, condition):
        if self.connection is None or self.connection.closed:
            self.connect()
        with self.connection, self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            try:
                set_clause = sql.SQL(', ').join(
                    sql.SQL('{} = {}').format(sql.Identifier(k), sql.Literal(v))
                    for k, v in update_dict.items()
                )
                condition_clause = sql.SQL(' AND ').join(
                    sql.SQL('{} = {}').format(sql.Identifier(k), sql.Literal(v))
                    for k, v in condition.items()
                )

                update_query = sql.SQL(
                    "UPDATE {} SET {} WHERE {}"
                ).format(
                    sql.Identifier(table_name),
                    set_clause,
                    condition_clause
                )
                if self.debug:
                    print(update_query.as_string(cur))
                cur.execute(update_query)
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                traceback.print_exc()
                print(f"Fail during update_data {e}")


