import hmac
import sqlite3
import datetime
from flask import Flask, request, jsonify, redirect, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS, cross_origin
from flask_mail import Mail, Message
from smtplib import SMTPRecipientsRefused, SMTPAuthenticationError
from werkzeug.utils import redirect


class User(object):
    def __init__(self, id, first_name, last_name, username, password, user_email, phone_number, address):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.user_email = user_email
        self.phone_number = phone_number
        self.address = address


# user tables
def user_reg():
    conn = sqlite3.connect('final_project_backend.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL, address TEXT NOT NULL, phone_number INT NOT NULL, user_email TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


# products table
def products():
    conn = sqlite3.connect('final_project_backend.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS product(prod_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "image TEXT NOT NULL,"
                 "product_name TEXT NOT NULL,"
                 "price NUMERIC NOT NULL," 
                 "brand TEXT NOT NULL," 
                 "product_type TEXT NOT NULL,"
                 "size TEXT," 
                 "color TEXT," 
                 "order_id INTEGER," 
                 "FOREIGN KEY (order_id) REFERENCES orders(order_id))")
    print("products table created successfully")
    conn.close()


# bussinesess table
def bussines_application():
    conn = sqlite3.connect('final_project_backend.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS business(buss_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "Business_name TEXT NOT NULL,"
                 "products_sold TEXT NOT NULL,"
                 "motivation TEXT NOT NULL,"
                 "contact_number NUMERIC NOT NULL, business_email TEXT NOT NULL, business_address TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


# optional shipping address table
def shipping_address():
    conn = sqlite3.connect('final_project_backend.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS shipping_table(ship_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "recipient_name TEXT NOT NULL,"
                 "recipient_lastname TEXT NOT NULL,"
                 "company TEXT,"
                 "recipient_address TEXT NOT NULL,"
                 "building_name TEXT NOT NULL," "city TEXT NOT NULL,"
                 "country TEXT NOT NULL," "province TEXT NOT NULL,"
                 "postal_code TEXT NOT NULL," "recipient_phone TEXT NOT NUll," "user_id INTEGER,"
                 "FOREIGN KEY(user_id) REFERENCES users(user_id))")
    print("shipping table created successfully")
    conn.close()


# order table
def orders_table():
    conn = sqlite3.connect('final_project_backend.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS orders(order_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "product_image TEXT NOT NULL,"
                 "order_date TEXT NOT NULL, "
                 "order_number INTEGER,"
                 "product_name TEXT NOT NULL,"
                 "total_price TEXT INTEGER NOT NULL,"
                 "product_quantity INTEGER NOT NULL,"
                 "FOREIGN KEY (order_number) REFERENCES users (user_id))")
    print("orders table created successfully")
    conn.close()


def returns_table():
    conn = sqlite3.connect('final_project_backend.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS returns(return_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "order_date TEXT NOT NULL,"
                 "address_delivered TEXT NOT NULL,"
                 "delivery_contact NUMERIC NOT NULL,"
                 "order_number INTEGER,"
                 "product_name TEXT NOT NULL,"
                 "product_code TEXT NOT NULL,"
                 "reason_for_return TEXT NOT NULL,"
                 "product_condition TEXT NOT NULL,"
                 "other_details TEXT NOT NULL,"
                 "FOREIGN KEY (order_number) REFERENCES orders(order_id) )")
    print("returns table created successfully")
    conn.close()

def contact_us():
    conn = sqlite3.connect('final_project_backend.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS contact(contact_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "name TEXT NOT NULL,"
                 "email_address TEXT NOT NULL, "
                 "enquiry TEXT NOT NULL)")
    print("orders table created successfully")
    conn.close()

user_reg()
products()
bussines_application()
orders_table()
shipping_address()
returns_table()
contact_us()



def fetch_users():
    with sqlite3.connect('final_project_backend.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[1], data[2], data[3], data[4], data[5], data[6],
                                 data[7]))  # append all data to new_data empty list
    return new_data


users = fetch_users()  # declare users tables to a variable "users"
# print(users)

username_table = {u.username: u for u in users}  # make a dictionary for username
userid_table = {u.id: u for u in users}  # make a dictionary for user id


# print(username_table)
# print(userid_table)

def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


# identify registered user by user id
def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=2)

# authanticate a loggen in user
jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


# register a new user
@app.route('/users/', methods=["POST", "GET"])

def user_registration():
    response = {}
    if request.method == "POST":
        try:

            first_name = request.form['first_name']
            last_name = request.form['last_name']
            username = request.form['username']
            password = request.form['password']
            address = request.form['address']
            phone_number = request.form['phone_number']
            user_email = request.form['user_email']

            with sqlite3.connect("final_project_backend.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users("
                               "first_name,"
                               "last_name,"
                               "username,"
                               "password,address,phone_number,user_email) VALUES(?, ?, ?, ?, ?, ?, ?)",
                               (first_name, last_name, username, password, address, phone_number, user_email))
                conn.commit()
                response["message"] = "User registered successfully "
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Invalid user information supplied"
            response["status_code"] = 401
            return response

    if request.method == "GET":
        response = {}
        with sqlite3.connect("final_project_backend.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM users")
            posts = cursor.fetchall()
            accumulator = []

            for i in posts:
                accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        return jsonify(response)


# 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
# View all products
@app.route('/product/', methods=["POST", "GET"])
def products_info():
    response = {}
    if request.method == "POST":
        try:
            image = request.form['image']
            product_name = request.form['product_name']
            price = request.form['price']
            brand = request.form['brand']
            product_type = request.form['product_type']
            size = request.form['size']
            color = request.form['color']
            order_id = request.form['order_id']

            with sqlite3.connect("final_project_backend.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO product("
                               "image,"
                               "product_name,"
                               "price,"
                               "brand,"
                               "product_type,"
                               "size,"
                               "color,"
                               "order_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (image, product_name, price, brand, product_type, size, color, order_id))
                conn.commit()
                response["message"] = "Product added successfully successfully "
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Enter correct product information"
            response["status_code"] = 401
            return response
    if request.method == "GET":

        with sqlite3.connect("final_project_backend.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM product")
            posts = cursor.fetchall()
            accumulator = []

            for i in posts:
                accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        return jsonify(response)





# register a new business partner

# Flask-Mail==0.9.1

# git config --global user.email "you@example.com"
# git config --global user.name "Your Name"

if __name__ == '__main__':
    app.run(debug=True)
