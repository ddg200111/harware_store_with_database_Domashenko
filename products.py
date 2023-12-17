from flask import Flask, jsonify
import sqlite3
import json
from datetime import datetime
import os
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)

# Function to create the database and table
def create_database():
    if not os.path.exists('hardware_store.db'):
        conn = sqlite3.connect('hardware_store.db')
        cursor = conn.cursor()

        # Create the products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

# Function to add fixtures (sample data) to the database
def add_fixtures():
    conn = sqlite3.connect('hardware_store.db')
    cursor = conn.cursor()

    # Check if the products table is empty
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]

    if count == 0:
        # Sample data with a specific date for the first product
        fixtures = [
            ('Microwave Gorenje MO17E1W', 2720.00, '2023-10-03'),
            ('Robot vacuum Xiaomi Mi Robot Vacuum S10+ White', 14600.00, '2023-12-02'),
            ('Electric shaver Philips razor 7000 series S7882/55', 7200.00, '2023-12-04'),
            ('Coffee machine Krups EA895N10', 18425.00, '2023-10-03'),
            ('Electric fireplace Artiflame AF23S', 15790.00, '2023-12-02'),
        ]

        # Insert fixtures into the products table
        cursor.executemany('INSERT INTO products (name, price, date) VALUES (?, ?, ?)', fixtures)

        conn.commit()

    conn.close()

# Function to fetch all products from the database
def get_all_products_with_fields():
    conn = sqlite3.connect('hardware_store.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, price, date FROM products')
    products = cursor.fetchall()

    conn.close()

    return [{'id': product[0], 'name': product[1], 'price': product[2], 'date': product[3]} for product in products]

# Route to get all products with specific fields as JSON
@app.route('/api/products', methods=['GET'])
def api_get_all_products():
    """
    Get all products

    ---
    responses:
      200:
        description: A list of products
        content:
          application/json:
            schema:
              type: object
              properties:
                products:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                        description: The product unique identifier
                      name:
                        type: string
                        description: The product name
                      price:
                        type: float
                        description: The product price
                      date:
                        type: string
                        description: The product date
    """
    products = get_all_products_with_fields()

    # Use json.dumps to control the sorting of keys
    response_data = json.dumps({'products': products}, sort_keys=False)

    # Create a Flask Response object with the JSON data
    response = app.response_class(
        response=response_data,
        status=200,
        mimetype='application/json'
    )

    return response

if __name__ == "__main__":
    # Create the database only if it doesn't exist
    create_database()

    # Add fixtures to the database if it's empty
    add_fixtures()

    # Run the Flask app
    app.run(debug=True)
