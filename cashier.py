from flask import Flask, jsonify, request
import sqlite3
import json
from flasgger import Swagger
from datetime import datetime, timedelta
from products import create_database, add_fixtures
from orders import create_orders_table

app = Flask(__name__)
swagger = Swagger(app)

# Function to add a new order to the orders table
def add_order(name, product_id, product_price, product_date, order_date, status):
    # Calculate the difference in months between product_date and order_date
    months_difference = (order_date.year - product_date.year) * 12 + order_date.month - product_date.month

    # Calculate the price based on the difference
    if months_difference > 1:
        price = round(0.8 * product_price, 2)  # 80% of the product price, rounded to 2 decimal places
    else:
        price = round(product_price, 2)  # Rounded to 2 decimal places

    conn = sqlite3.connect('hardware_store.db')  # Assume orders are in the same database as products
    cursor = conn.cursor()

    # Insert the new order into the orders table
    cursor.execute('''
        INSERT INTO orders (name, product_id, price, date, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, product_id, price, order_date.strftime("%Y-%m-%d"), status))

    conn.commit()
    conn.close()

# Function to generate a bill for a given order ID
def generate_bill(order_id):
    conn = sqlite3.connect('hardware_store.db')  # Assume orders are in the same database as products
    cursor = conn.cursor()

    # Fetch order details
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order_details = cursor.fetchone()

    if order_details is None:
        conn.close()
        return jsonify({'error': f'Order with ID {order_id} not found'}), 404

    order_id, order_name, product_id, price, date, status = order_details

    # Fetch product details
    cursor.execute('SELECT name, price FROM products WHERE id = ?', (product_id,))
    product_details = cursor.fetchone()

    if product_details is None:
        conn.close()
        return jsonify({'error': f'Product with ID {product_id} not found'}), 404

    product_name, product_price = product_details

    # Calculate discount
    discount = '20% off' if price < product_price else ''

    # Calculate sum
    sum_price = price

    # Close the database connection
    conn.close()

    # Format the table data as a list of dictionaries
    table_data = [
        {'№': 1, 'product': product_name, 'price': product_price, 'discount': discount, 'sum': sum_price}
    ]

    # Format the bill data manually
    bill_data = {
        'id': order_id,
        'date': datetime.now().strftime("%Y-%m-%d"),
        'provider': 'Store details',
        'buyer': order_name,
        'table': table_data
    }

    response_data = json.dumps(bill_data, sort_keys=False)  # Disable sorting keys in json.dumps

    # Create a Flask Response object with the JSON data
    response = app.response_class(
        response=response_data,
        status=200,
        mimetype='application/json'
    )

    return response

# Function to fetch all orders with status "Done" from the orders table
def get_done_orders():
    conn = sqlite3.connect('hardware_store.db')  # Assume orders are in the same database as products
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM orders WHERE status = "Done"')
    done_orders = cursor.fetchall()

    conn.close()

    return done_orders

# Function to change the status of an order from "Done" to "Paid"
def mark_order_as_paid(order_id):
    conn = sqlite3.connect('hardware_store.db')  # Assume orders are in the same database as products
    cursor = conn.cursor()

    # Update the status of the order with the given ID
    cursor.execute('UPDATE orders SET status = "Paid" WHERE id = ?', (order_id,))
    conn.commit()

    conn.close()

# Function to fetch all orders with status "Paid" from the orders table
def get_paid_orders():
    conn = sqlite3.connect('hardware_store.db')  # Assume orders are in the same database as products
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM orders WHERE status = "Paid"')
    paid_orders = cursor.fetchall()

    conn.close()

    return paid_orders

# Endpoint to add a new order
@app.route('/api/cashier/add_order', methods=['POST'])
def api_add_order():
    """
    Add a new order

    ---
    parameters:
      - name: name
        in: formData
        type: string
        required: true
        description: The name of the buyer
      - name: product_id
        in: formData
        type: integer
        required: true
        description: The ID of the product being ordered

    responses:
      201:
        description: Order added successfully
      400:
        description: Missing required data or invalid data type for product_id
      404:
        description: Product with the specified ID not found
    """
    data = request.get_json()

    name = data.get('name')
    product_id = data.get('product_id')

    # Set the order date to the current date
    order_date = datetime.now()

    # Set the status to "Accepted" regardless of the value provided in the request
    status = "Accepted"

    if not all([name, product_id]):
        return jsonify({'error': 'Missing required data'}), 400

    try:
        product_id = int(product_id)
    except ValueError:
        return jsonify({'error': 'Invalid data type for product_id'}), 400

    # Query the product table to get the price and date based on the provided product_id
    conn = sqlite3.connect('hardware_store.db')
    cursor = conn.cursor()
    cursor.execute('SELECT price, date FROM products WHERE id = ?', (product_id,))
    result = cursor.fetchone()

    if result is None:
        return jsonify({'error': f'Product with id {product_id} not found'}), 404

    product_price, product_date_str = result
    product_date = datetime.strptime(product_date_str, "%Y-%m-%d")

    # Close the database connection
    conn.close()

    add_order(name, product_id, product_price, product_date, order_date, status)
    return jsonify({'message': 'Order added successfully'}), 201

# Endpoint to get all orders with status "Done"
@app.route('/api/cashier/get_done_orders', methods=['GET'])
def api_get_done_orders():
    """
    Get all orders with status "Done"

    ---
    responses:
      200:
        description: List of orders with status "Done"
        schema:
          type: object
          properties:
            done_orders:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  product_id:
                    type: integer
                  price:
                    type: float
                  date:
                    type: string
                  status:
                    type: string
      204:
        description: No orders with status "Done" found
    """
    done_orders = get_done_orders()

    if not done_orders:
        return jsonify({'message': 'No orders with status "Done" found'}), 204

    # Format the data as a list of dictionaries
    orders_data = [
        {'id': order[0], 'name': order[1], 'product_id': order[2], 'price': order[3], 'date': order[4], 'status': order[5]}
        for order in done_orders
    ]

    # Create a Flask Response object with the JSON data
    response = app.response_class(
        response=json.dumps({'done_orders': orders_data}, sort_keys=False),
        status=200,
        mimetype='application/json'
    )

    return response

# Endpoint to change the status of an order to "Paid"
@app.route('/api/cashier/mark_order_as_paid/<int:order_id>', methods=['PUT'])
def api_mark_order_as_paid(order_id):
    """
    Change the status of an order to "Paid"

    ---
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: The ID of the order to be marked as "Paid"

    responses:
      200:
        description: Status of the order changed to "Paid"
      404:
        description: Order with the specified ID not found
    """
    mark_order_as_paid(order_id)
    return jsonify({'message': f'Status of order {order_id} changed to "Paid"'}), 200

# Endpoint to get all orders with status "Paid"
@app.route('/api/cashier/get_paid_orders', methods=['GET'])
def api_get_paid_orders():
    """
    Get all orders with status "Paid"

    ---
    responses:
      200:
        description: List of orders with status "Paid"
        schema:
          type: object
          properties:
            paid_orders:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  product_id:
                    type: integer
                  price:
                    type: float
                  date:
                    type: string
                  status:
                    type: string
      204:
        description: No orders with status "Paid" found
    """
    paid_orders = get_paid_orders()

    if not paid_orders:
        return jsonify({'message': 'No orders with status "Paid" found'}), 204

    # Format the data as a list of dictionaries
    orders_data = [
        {'id': order[0], 'name': order[1], 'product_id': order[2], 'price': order[3], 'date': order[4], 'status': order[5]}
        for order in paid_orders
    ]

    # Create a Flask Response object with the JSON data
    response = app.response_class(
        response=json.dumps({'paid_orders': orders_data}, sort_keys=False),
        status=200,
        mimetype='application/json'
    )

    return response

# Endpoint to generate a bill for a given order ID
@app.route('/api/cashier/generate_bill/<int:order_id>', methods=['GET'])
def api_generate_bill(order_id):
    """
    Generate a bill for a given order ID

    ---
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: The ID of the order for which to generate a bill

    responses:
      200:
        description: Bill generated successfully
      404:
        description: Order with the specified ID not found
    """
    return generate_bill(order_id)

if __name__ == "__main__":
    # Create the database and products table if it doesn't exist
    create_database()
    
    # Add fixtures to the products table
    add_fixtures()

    # Create the orders table
    create_orders_table()

    # Run the Flask app
    app.run(debug=True)