
from flask import Flask,request, redirect, url_for,session
from flask import Flask, render_template
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from flask_httpauth import HTTPBasicAuth
import os

app = Flask(__name__)
auth = HTTPBasicAuth()  # Initialize HTTP basic authentication
# Generate a random secret key
secret_key = os.urandom(24)
app.secret_key = 'your_secret_key_here'

# MySQL database connection details
host = 'localhost'
port = '3307'
user = 'root'
password = 'Hamada@121199'
database = 'chefaa'

# Establish a connection to the MySQL database
connection = mysql.connector.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

# Suppressing the warning about SQL connection
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy connectable*')

# Create indexes on relevant columns if not already present

# MySQL queries
order_status_query = """
SELECT order_status, COUNT(order_id) AS order_count
FROM Orders
GROUP BY order_status
"""

product_categories_query = """
SELECT product_category_name, COUNT(product_id) AS product_count
FROM Products
GROUP BY product_category_name
"""

customer_analysis_query = """
SELECT Customer_state, COUNT(DISTINCT Customer_id) AS customer_count
FROM Customers
GROUP BY Customer_state
"""

seller_analysis_query = """
SELECT seller_state, COUNT(DISTINCT seller_id) AS seller_count
FROM Sellers
GROUP BY seller_state
"""

customer_satisfaction_query = """
SELECT review_score, COUNT(review_id) AS review_count
FROM reviews
GROUP BY review_score
"""

payment_methods_query = """
SELECT payment_type, COUNT(order_id) AS payment_count
FROM Order_Payments
GROUP BY payment_type
"""

average_order_value_query = """
SELECT product_category_name, AVG(price) AS average_order_value
FROM Order_Items oi
JOIN Products p ON oi.product_id = p.product_id
GROUP BY product_category_name
"""

top_sellers_query = """
SELECT s.seller_id, s.seller_city, s.seller_state, p.product_category_name, SUM(oi.price) AS total_sales
FROM Sellers s
JOIN Order_Items oi ON s.seller_id = oi.seller_id
JOIN Products p ON oi.product_id = p.product_id
GROUP BY s.seller_id, s.seller_city, s.seller_state, p.product_category_name
ORDER BY total_sales DESC
LIMIT 10;
"""

# Execute the queries and fetch the data into pandas DataFrames
order_status_data = pd.read_sql(order_status_query, connection)
product_categories_data = pd.read_sql(product_categories_query, connection)
customer_analysis_data = pd.read_sql(customer_analysis_query, connection)
seller_analysis_data = pd.read_sql(seller_analysis_query, connection)
customer_satisfaction_data = pd.read_sql(customer_satisfaction_query, connection)
payment_methods_data = pd.read_sql(payment_methods_query, connection)
average_order_value_data = pd.read_sql(average_order_value_query, connection)
top_sellers_data = pd.read_sql(top_sellers_query, connection)



# Sample user data (you might use a database in practice)
USERS = {
    
    'Admin': '123'
}

# HTTP Basic Authentication callback function
@auth.verify_password
def verify_password(username, password):
    # Check if the provided credentials are valid
    return USERS.get(username) == password

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['username'] = username  # Store the username in the session
            return redirect(url_for('dashboard'))  # Redirect to the dashboard on successful login
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html', error=None)

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the 'username' key from the session
    return redirect(url_for('login'))  # Redirect to the login page




# Increase figure size for all plots
figure_size = (12, 8)

@app.route('/dashboard')
@auth.login_required 
def dashboard():

    if session.get('username') != 'Admin':  # Check if the user is an admin
        return redirect(url_for('login'))  # Redirect to the login page if not an admin
    # Order Status stacked bar chart
    plt.figure(figsize=figure_size)
    plt.bar(order_status_data['order_status'], order_status_data['order_count'], color='#82001A')
    plt.xlabel('Order Status')
    plt.ylabel('Order Count')
    plt.title('Order Status')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/order_status.png')  # Save the figure as an image

    # Product Categories bar chart
    plt.figure(figsize=figure_size)
    plt.bar(
        product_categories_data['product_category_name'],
        product_categories_data['product_count'],
        width=0.5,
        color='#82001A'
    )
    plt.xlabel('Product Category')
    plt.ylabel('Product Count')
    plt.title('Product Categories')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('static/product_categories.png')  # Save the figure as an image

    # Customer Analysis pie chart
    plt.figure(figsize=figure_size)
    plt.pie(
        customer_analysis_data['customer_count'],
        labels=customer_analysis_data['Customer_state'],
        colors=['#82001A', '#D46A6A', '#FFC1C1', '#FFAFAF']
    )
    plt.title('Customer Analysis')
    plt.tight_layout()
    plt.savefig('static/customer_analysis.png')  # Save the figure as an image

    # Seller Analysis bar chart
    plt.figure(figsize=figure_size)
    plt.bar(seller_analysis_data['seller_state'], seller_analysis_data['seller_count'], color='#82001A')
    plt.xlabel('Seller State')
    plt.ylabel('Seller Count')
    plt.title('Seller Analysis')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/seller_analysis.png')  # Save the figureas an image

    # Customer Satisfaction bar chart
    plt.figure(figsize=figure_size)
    plt.bar(
        customer_satisfaction_data['review_score'],
        customer_satisfaction_data['review_count'],
        color='#82001A'
    )
    plt.xlabel('Review Score')
    plt.ylabel('Review Count')
    plt.title('Customer Satisfaction')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/customer_satisfaction.png')  # Save the figure as an image

    # Payment Methods pie chart
    plt.figure(figsize=figure_size)
    plt.pie(
        payment_methods_data['payment_count'],
        labels=payment_methods_data['payment_type'],
        colors=['#82001A', '#D46A6A', '#FFC1C1', '#FFAFAF']
    )
    plt.title('Payment Methods')
    plt.tight_layout()
    plt.savefig('static/payment_methods.png')  # Save the figure as an image

    # Average Order Value by Product Category bar chart
    plt.figure(figsize=figure_size)
    plt.bar(
        average_order_value_data['product_category_name'],
        average_order_value_data['average_order_value'],
        color='#82001A'
    )
    plt.xlabel('Product Category')
    plt.ylabel('Average Order Value')
    plt.title('Average Order Value by Product Category')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('static/average_order_value.png')  # Save the figure as an image

    # Top Sellers by Total Sales bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(top_sellers_data['product_category_name'], top_sellers_data['total_sales'], color='#82001A')
    plt.xlabel('Product Category')
    plt.ylabel('Total Sales')
    plt.title('Top 10 Sellers by Total Sales')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/top_sellers.png')  # Save the figure as an image

    return render_template('dashboard.html')

@app.route('/data')
def display_data():
    # SELECT queries
    queries = [
        "SELECT * FROM Categories LIMIT 100",
        "SELECT * FROM customers LIMIT 100",
        "SELECT * FROM geolocation LIMIT 100",
        "SELECT * FROM order_items LIMIT 100",
        "SELECT * FROM order_payments LIMIT 100",
        "SELECT * FROM orders LIMIT 100",
        "SELECT * FROM products LIMIT 100",
        "SELECT * FROM reviews LIMIT 100",
        "SELECT * FROM sellers LIMIT 100"
    ]
    
    # Execute the queries and store the results in a dictionary
    data = {}
    for query in queries:
        table_name = query.split("FROM")[1].split("LIMIT")[0].strip()
        df = pd.read_sql(query, connection)
        data[table_name] = df
    
    return render_template('data.html', data=data)

if __name__ == '__main__':
    app.run()