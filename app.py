import hmac
import sqlite3
from datetime import datetime
import datetime
from flask import Flask, request, jsonify, redirect, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS, cross_origin
from flask_mail import Mail, Message
from smtplib import SMTPRecipientsRefused, SMTPAuthenticationError
from werkzeug.utils import redirect


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


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
    conn = sqlite3.connect('final_backend.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL,"
                 "address TEXT NOT NULL,"
                 "phone_number INT NOT NULL,"
                 "user_email TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


# products table
def products():
    conn = sqlite3.connect('final_backend.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS product(prod_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "image TEXT NOT NULL,"
                 "product_name TEXT NOT NULL,"
                 "price NUMERIC NOT NULL,"
                 "brand TEXT NOT NULL,"
                 "product_type TEXT NOT NULL,"
                 "size TEXT,"
                 "color TEXT,"
                 "order_id INTEGER NOT NULL,"
                 "FOREIGN KEY (order_id) REFERENCES users(user_id))")
    print("products table created successfully")
    conn.close()


# bussinesess table
def bussines_application():
    conn = sqlite3.connect('final_backend.db')
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
    conn = sqlite3.connect('final_backend.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS shipping_table(ship_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "recipient_name TEXT NOT NULL,"
                 "recipient_lastname TEXT NOT NULL,"
                 "company TEXT,"
                 "recipient_address TEXT NOT NULL,"
                 "building_name TEXT NOT NULL," "city TEXT NOT NULL,"
                 "country TEXT NOT NULL," "province TEXT NOT NULL,"
                 "postal_code TEXT NOT NULL," "recipient_phone TEXT NOT NUll," "user_id INTEGER NOT NULL,"
                 "FOREIGN KEY(user_id) REFERENCES users(user_id))")
    print("shipping table created successfully")
    conn.close()


# order table
def orders_table():
    conn = sqlite3.connect('final_backend.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS orders(order_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "product_image TEXT NOT NULL,"
                 "order_date TEXT NOT NULL, "
                 "order_number INTEGER NOT NULL ,"
                 "product_name TEXT NOT NULL,"
                 "total_price TEXT INTEGER NOT NULL,"
                 "product_quantity INTEGER NOT NULL,"
                 "FOREIGN KEY (order_number) REFERENCES users (user_id))")
    print("orders table created successfully")
    conn.close()


def returns_table():
    conn = sqlite3.connect('final_backend.db')
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
                 "FOREIGN KEY (order_number) REFERENCES users(user_id) )")
    print("returns table created successfully")
    conn.close()


def contact_us():
    conn = sqlite3.connect('final_backend.db')
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
    with sqlite3.connect('final_backend.db') as conn:
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
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=2)

# authanticate a loggen in user
jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@cross_origin()
@jwt_required()
def protected():
    return '%s' % current_identity


# register a new user
@app.route('/users/', methods=["POST", "GET", "PATCH"])
@cross_origin()
def user_registration():
    response = {}
    if request.method == "POST":

        try:

            first_name = request.json['first_name']
            last_name = request.json['last_name']
            username = request.json['username']
            password = request.json['password']
            address = request.json['address']
            phone_number = request.json['phone_number']
            user_email = request.json['user_email']

            with sqlite3.connect("final_backend.db") as conn:
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

            response["message"] = "Invalid user injsonation supplied"
            response["status_code"] = 401
            return response

    if request.method == "GET":
        response = {}
        with sqlite3.connect("final_backend.db") as conn:
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
    # LOGIN
    if request.method == "PATCH":
        username = request.json["username"]
        password = request.json["password"]

        with sqlite3.connect("final_backend.db") as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password,))
            user = cursor.fetchone()
        response['status_code'] = 200
        response['data'] = user
        return response


# get single user
@app.route('/user/<int:user_id>', methods=["GET"])
@cross_origin()
# @jwt_required()
def get_user(user_id):
    response = {}
    with sqlite3.connect("final_backend.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        # cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM users WHERE user_id=" + str(user_id))
        user = cursor.fetchone()
        # accumulator = []
        # for i in user:
        # accumulator.append({k: i[k] for k in i.keys()})

    response['status_code'] = 200
    response['data'] = user  # tuple(accumulator)
    return response


# delete user by id
@app.route("/delete-user/<int:post_id>", methods=['POST'])
@cross_origin()
# @jwt_required()
def delete_product(post_id):
    response = {}
    with sqlite3.connect("final_backend.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id=" + str(post_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "User deleted successfully."
    return response


# update single user
@app.route('/update-user/<int:user_id>/', methods=["PUT"])
@cross_origin()
# @jwt_required()
def edit_user(user_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('final_backend.db') as conn:
            incoming_data = dict(request.json)

            put_data = {}

            if incoming_data.get("first_name") is not None:  # check if the updated column is price
                put_data["first_name"] = incoming_data.get("first_name")
                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET first_name =? WHERE user_id=?", (put_data["first_name"], user_id))
                    conn.commit()
                    response['message'] = "First name updated"
                    response['status_code'] = 200
            if incoming_data.get("last_name") is not None:
                put_data['last_name'] = incoming_data.get('last_name')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET last_name =? WHERE user_id=?", (put_data["last_name"], user_id))
                    conn.commit()

                    response["content"] = "Last name updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("username") is not None:
                put_data['username'] = incoming_data.get('username')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET username =? WHERE user_id=?", (put_data["username"], user_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("password") is not None:
                put_data['password'] = incoming_data.get('password')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET password =? WHERE user_id=?", (put_data["password"], user_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("address") is not None:
                put_data['address'] = incoming_data.get('address')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET address =? WHERE user_id=?", (put_data["address"], user_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("phone_number") is not None:
                put_data['phone_number'] = incoming_data.get('phone_number')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET phone_number =? WHERE user_id=?",
                                   (put_data["phone_number"], user_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("user_email") is not None:
                put_data['user_email'] = incoming_data.get('user_email')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET user_email =? WHERE user_id=?", (put_data["user_email"], user_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

    return response


# 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
# View all products
@app.route('/product/', methods=["POST", "GET"])
@cross_origin()
def products_info():
    response = {}
    if request.method == "POST":
        try:
            image = request.json['image']
            product_name = request.json['product_name']
            price = request.json['price']
            brand = request.json['brand']
            product_type = request.json['product_type']
            size = request.json['size']
            color = request.json['color']
            order_id = request.json['order_id']

            with sqlite3.connect("final_backend.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO product("
                               "image,"
                               "product_name,"
                               "price,"
                               "brand,"
                               "product_type,"
                               "size,"
                               "color,"
                               "order_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                               (image, product_name, price, brand, product_type, size, color, order_id))
                conn.commit()
                response["message"] = "Product added successfully successfully "
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Enter correct product injsonation"
            response["status_code"] = 401
            return response
    if request.method == "GET":

        with sqlite3.connect("final_backend.db") as conn:
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


# get product by id
@app.route('/single_product/<int:order_id>', methods=["GET"])
@cross_origin()
def get_product(order_id):
    response = {}
    with sqlite3.connect("final_backend.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM product WHERE order_id=" + str(order_id))
        user = cursor.fetchone()
        accumulator = []
        for i in user:
            accumulator.append({k: i[k] for k in i.keys()})
    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)


# update product by id
@app.route('/update-product/<int:prod_id>/', methods=["PUT"])
@cross_origin()
# @jwt_required()
def update_product(prod_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('final_backend.db') as conn:
            incoming_data = dict(request.json)

            put_data = {}

            if incoming_data.get("image") is not None:  # check if the updated column is price
                put_data["image"] = incoming_data.get("image")
                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET image =? WHERE prod_id=?", (put_data["first_name"], prod_id))
                    conn.commit()
                    response['message'] = "First name updated"
                    response['status_code'] = 200

            if incoming_data.get("last_name") is not None:
                put_data['product_name'] = incoming_data.get('product_name')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET product_name =? WHERE prod_id=?",
                                   (put_data["last_name"], prod_id))
                    conn.commit()

                    response["content"] = "Last name updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET price =? WHERE prod_id=?", (put_data["price"], prod_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("brand") is not None:
                put_data['brand'] = incoming_data.get('brand')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET brand =? WHERE prod_id=?", (put_data["brand"], prod_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("product_type") is not None:
                put_data['product_type'] = incoming_data.get('product_type')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET product_type =? WHERE prod_id=?",
                                   (put_data["product_type"], prod_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("size") is not None:
                put_data['size'] = incoming_data.get('size')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET size =? WHERE prod_id=?",
                                   (put_data["size"], prod_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("color") is not None:
                put_data['color'] = incoming_data.get('color')

                with sqlite3.connect('final_backend.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET color =? WHERE prod_id=?", (put_data["color"], prod_id))
                    conn.commit()

                    response["content"] = "Product description updated successfully"
                    response["status_code"] = 200

    return response


# delete product by id
@app.route("/delete-product/<int:prod_id>", methods=['POST'])
@cross_origin()
# @jwt_required()
def delete_single_product(prod_id):
    response = {}
    with sqlite3.connect("final_backend.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE prod_id=" + str(prod_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product deleted successfully."
    return response


@app.route('/orders/', methods=["POST", "GET"])
@cross_origin()
# @jwt_required()
def orders_info():
    response = {}
    now = datetime.now()
    if request.method == "POST":
        try:
            product_image = request.json['product_image']
            order_number = request.json['order_number']
            product_name = request.json['product_name']
            total_price = request.json['total_price']
            product_quantity = request.json['product_quantity']

            with sqlite3.connect("final_backend.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO orders("
                               "product_image,"
                               "order_date,"
                               "order_number,"
                               "product_name,"
                               "total_price,"
                               "product_quantity) VALUES(?, ?, ?, ?, ?, ?)",
                               (product_image, now, order_number, product_name, total_price, product_quantity))
                conn.commit()
                response["message"] = "Order added successfully successfully "
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Enter correct order injsonation"
            response["status_code"] = 401
            return response
    if request.method == "GET":

        with sqlite3.connect("final_backend.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM orders")
            posts = cursor.fetchall()
            accumulator = []

            for i in posts:
                accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        return jsonify(response)


# get single order by id
@app.route('/single_order/<int:order_number>', methods=["GET"])
@cross_origin()
# @jwt_required()
def get_order(order_number):
    response = {}
    with sqlite3.connect("final_backend.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM orders WHERE order_number=" + str(order_number))
        user = cursor.fetchone()
        accumulator = []
        for i in user:
            accumulator.append({k: i[k] for k in i.keys()})
    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)


# delete single order
@app.route("/delete-order/<int:order_id>", methods=['POST'])
@cross_origin()
# @jwt_required()
def delete_order(order_id):
    response = {}
    with sqlite3.connect("final_backend.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id=" + str(order_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "User deleted successfully."
    return response


# get and fetch all returns
@app.route('/returns/', methods=["GET", "POST"])
@cross_origin()
# @jwt_required()
def returns_info():
    response = {}
    now = datetime.now()
    if request.method == "POST":
        try:

            address_delivered = request.json['address_delivered']
            delivery_contact = request.json['delivery_contact']
            order_number = request.json['order_number']
            product_name = request.json['product_name']
            product_code = request.json['product_code']
            reason_for_return = request.json['reason_for_return']
            product_condition = request.json['product_condition']
            other_details = request.json['other_details']

            with sqlite3.connect("final_backend.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO returns("
                               "order_date,"
                               "address_delivered,"
                               "delivery_contact,"
                               "order_number,"
                               "product_name,"
                               "product_code,"
                               "reason_for_return,"
                               "product_condition,"
                               "other_details,) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                               (now, address_delivered, delivery_contact, order_number, product_name, product_code,
                                reason_for_return, product_condition, other_details))
                conn.commit()
                response["message"] = "Return lodged successfully successfully "
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Enter full injsonation"
            response["status_code"] = 401
            return response
    if request.method == "GET":

        with sqlite3.connect("final_backend.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM returns")
            posts = cursor.fetchall()
            accumulator = []

            for i in posts:
                accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        return jsonify(response)


# get returns by id
@app.route('/get-returns/<int:orde_number>', methods=["GET"])
@cross_origin()
# @jwt_required()
def returns(order_number):
    response = {}
    with sqlite3.connect("final_backend.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM returns WHERE order_number=" + str(order_number))
        user = cursor.fetchone()
        accumulator = []
        for i in user:
            accumulator.append({k: i[k] for k in i.keys()})
    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)


# shipping address
@app.route('/shipping/', methods=["POST", "GET"])
@cross_origin()
# @jwt_required()
def shipping_address():
    response = {}
    now = datetime.now()
    if request.method == "POST":
        try:

            recipient_name = request.json['recipient_name']
            recipient_lastname = request.json['recipient_lastname']
            company = request.json['company']
            recipient_address = request.json['recipient_address']
            building_name = request.json['building_name']
            country = request.json['country']
            postal_code = request.json['product_condition']

            with sqlite3.connect("final_backend.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO shipping_table("
                               "recipient_name,"
                               "recipient_lastname,"
                               "company,"
                               "recipient_address,"
                               "building_name,"
                               "country,"
                               "postal_code) VALUES(?, ?, ?, ?, ?, ?, ?)",
                               (recipient_name, recipient_lastname, company, recipient_address, building_name, country,
                                postal_code))
                conn.commit()
                response["message"] = "Alternate address added"
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Enter full injsonation"
            response["status_code"] = 401
            return response
    if request.method == "GET":

        with sqlite3.connect("final_backend.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM shipping_address")
            posts = cursor.fetchall()
            accumulator = []

            for i in posts:
                accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        return jsonify(response)


# contact section
@app.route('/contact-us/', methods=["POST", "GET"])
@cross_origin()
# @jwt_required()
def contact():
    response = {}
    if request.method == "POST":
        try:

            name = request.json['name']
            email_address = request.json['email_address']
            enquiry = request.json['enquiry']

            with sqlite3.connect("final_backend.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO contact("
                               "name,"
                               "email_address,"
                               "enquiry) VALUES(?, ?, ?)",
                               (name, email_address, enquiry))
                conn.commit()
                response["message"] = "User registered successfully "
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Enter valid injsonation"
            response["status_code"] = 401
            return response

    if request.method == "GET":
        response = {}
        with sqlite3.connect("final_backend.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM contact")
            posts = cursor.fetchall()
            accumulator = []

            for i in posts:
                accumulator.append({k: i[k] for k in i.keys()})

        response['status_code'] = 200
        response['data'] = tuple(accumulator)
        return jsonify(response)


# business partner registration
@app.route('/business-register/', methods=["POST", "GET"])
@cross_origin()
# @jwt_required()
def business_site_application():
    response = {}
    if request.method == "POST":
        try:

            business_name = request.json['business_name']
            products_sold = request.json['products_sold']
            motivation = request.json['motivation']
            contact_number = request.json['contact_number']
            business_email = request.json['business_email']
            business_address = request.json['business_address']

            with sqlite3.connect("final_backend.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO contact("
                               "name,"
                               "email_address,"
                               "enquiry) VALUES(?, ?, ?, ?, ?, ?)",
                               (business_name, products_sold, motivation, contact_number, business_email,
                                business_address))
                conn.commit()
                response["message"] = " Application received, please wait for response "
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Enter valid injsonation"
            response["status_code"] = 401
            return response

    if request.method == "GET":
        response = {}
        with sqlite3.connect("final_backend.db") as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            cursor.execute("SELECT * FROM shipping_table")
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
