from flask import Flask, jsonify, request
import sqlite3
import json
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)

# Assume orders are in the same database as products
DATABASE_PATH = 'hardware_store.db'

# Function to create the database and table
def create_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create the orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            price REAL NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Function to add fixtures (sample data) to the orders table
def add_fixtures():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if the orders table is empty
    cursor.execute('SELECT COUNT(*) FROM orders')
    count = cursor.fetchone()[0]

    if count == 0:
        # Sample data
        fixtures = [
            ('John Doe', 1, 19.99, '2023-11-25', 'Accepted'),
            ('Jane Smith', 2, 29.99, '2023-10-25', 'Accepted'),
            ('Jake Doe', 3, 39.99, '2023-09-25', 'Accepted'),
        ]

        # Insert fixtures into the orders table
        cursor.executemany('INSERT INTO orders (name, product_id, price, date, status) VALUES (?, ?, ?, ?, ?)', fixtures)

        conn.commit()

    conn.close()

# Function to fetch all accepted orders from the orders table
def get_accepted_orders():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM orders WHERE status = "Accepted"')
    accepted_orders = cursor.fetchall()

    conn.close()

    return accepted_orders

# Function to change the status of an order from "Accepted" to "Done"
def mark_order_as_done(order_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Update the status of the order with the given ID
    cursor.execute('UPDATE orders SET status = "Done" WHERE id = ?', (order_id,))
    conn.commit()

    conn.close()

# Endpoint to get all accepted orders
@app.route('/api/consultant/get_accepted_orders', methods=['GET'])
def api_get_accepted_orders():
    """
    Get all accepted orders

    ---
    responses:
      200:
        description: A list of accepted orders
        content:
          application/json:
            schema:
              type: object
              properties:
                accepted_orders:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        description: The order unique identifier
                      name:
                        type: string
                        description: The buyer's name
                      product_id:
                        type: integer
                        description: The product unique identifier
                      price:
                        type: float
                        description: The order price
                      date:
                        type: string
                        description: The order date
                      status:
                        type: string
                        description: The order status
    """
    accepted_orders = get_accepted_orders()

    # Format the data as a list of dictionaries
    orders_data = [{'id': order[0], 'name': order[1], 'product_id': order[2], 'price': order[3], 'date': order[4], 'status': order[5]} for order in accepted_orders]

    # Create a Flask Response object with the JSON data
    response = app.response_class(
        response=json.dumps({'accepted_orders': orders_data}, sort_keys=False),
        status=200,
        mimetype='application/json'
    )

    return response

# Endpoint to change the status of an order to "Done"
@app.route('/api/consultant/mark_order_as_done/<int:order_id>', methods=['PUT'])
def api_mark_order_as_done(order_id):
    """
    Mark an order as Done

    ---
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: The order ID

    responses:
      200:
        description: The order status changed successfully
      404:
        description: Order not found
    """
    mark_order_as_done(order_id)
    return jsonify({'message': f'Status of order {order_id} changed to "Done"'}), 200

if __name__ == "__main__":
    # Create the database and orders table if it doesn't exist
    create_database()

    # Add fixtures to the orders table
    add_fixtures()

    # Run the Flask app
    app.run(debug=True, port=5002)
