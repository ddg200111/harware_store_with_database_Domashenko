from flask import Flask, jsonify, request
import sqlite3
import json
from datetime import datetime
from products import create_database, add_fixtures
from orders import create_orders_table
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# Function to fetch all orders from the orders table
def get_all_orders():
    """
    Fetch all orders from the orders table.

    Returns:
    List: List of orders.
    """
    conn = sqlite3.connect('hardware_store.db')  # Assume orders are in the same database as products
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()

    conn.close()

    return orders

# Function to fetch orders between specified dates
def get_orders_between_dates(start_date, end_date):
    """
    Fetch orders between specified dates.

    Args:
    start_date (str): Start date in the format YYYY-MM-DD.
    end_date (str): End date in the format YYYY-MM-DD.

    Returns:
    List: List of orders between the specified dates.
    """
    conn = sqlite3.connect('hardware_store.db')  # Assume orders are in the same database as products
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM orders WHERE date BETWEEN ? AND ?', (start_date, end_date))
    orders = cursor.fetchall()

    conn.close()

    return orders

# Endpoint to get all orders
@app.route('/api/accountant/get_all_orders', methods=['GET'])
def api_get_all_orders():
    """
    Get all orders.

    ---
    responses:
      200:
        description: List of all orders
    """
    orders = get_all_orders()

    # Format the data as a list of dictionaries
    orders_data = [{'id': order[0], 'name': order[1], 'product_id': order[2], 'price': order[3], 'date': order[4], 'status': order[5]} for order in orders]

    # Create a Flask Response object with the JSON data
    response = app.response_class(
        response=json.dumps({'orders': orders_data}, sort_keys=False),
        status=200,
        mimetype='application/json'
    )

    return response

# Endpoint to get orders between specified dates
@app.route('/api/accountant/get_orders_between_dates', methods=['GET'])
def api_get_orders_between_dates():
    """
    Get orders between specified dates.

    ---
    parameters:
      - name: start_date
        in: query
        type: string
        required: true
        description: Start date in the format YYYY-MM-DD
      - name: end_date
        in: query
        type: string
        required: true
        description: End date in the format YYYY-MM-DD

    responses:
      200:
        description: List of orders between specified dates
      400:
        description: Missing required parameters or invalid date format
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not all([start_date, end_date]):
        return jsonify({'error': 'Missing required parameters (start_date, end_date)'}), 400

    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD'}), 400

    orders = get_orders_between_dates(start_date, end_date)

    # Format the data as a list of dictionaries
    orders_data = [{'id': order[0], 'name': order[1], 'product_id': order[2], 'price': order[3], 'date': order[4], 'status': order[5]} for order in orders]

    # Create a Flask Response object with the JSON data
    response = app.response_class(
        response=json.dumps({'orders_between_dates': orders_data}, sort_keys=False),
        status=200,
        mimetype='application/json'
    )

    return response

if __name__ == "__main__":
    # Create the database and products table if it doesn't exist
    create_database()
    
    # Add fixtures to the products table
    add_fixtures()

    # Create the orders table
    create_orders_table()

    app.run(debug=True, port=5003)
