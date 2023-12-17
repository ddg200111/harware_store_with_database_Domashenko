import sqlite3

# Function to create the orders table with a foreign key constraint
def create_orders_table():
    conn = sqlite3.connect('hardware_store.db')  # Use the same database as products
    cursor = conn.cursor()

    # Check if the orders table already exists
    cursor.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='orders'
    ''')
    table_exists = cursor.fetchone()

    if not table_exists:
        # Create the orders table with a foreign key constraint
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        conn.commit()

    conn.close()

# Run the function to create the orders table
if __name__ == "__main__":
    create_orders_table()
