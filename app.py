import hmac
import sqlite3
import datetime
from flask import Flask, request, jsonify, redirect, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS, cross_origin
from flask_mail import Mail,Message
from smtplib import SMTPRecipientsRefused, SMTPAuthenticationError
from werkzeug.utils import redirect

class User(object):
    def __init__(self, id, first_name,last_name ,username, password,user_email,phone_number,address):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = password
        self.user_email = user_email
        self.phone_number = phone_number
        self.address = address


def user_reg():

    conn = sqlite3.connect('Point_of_Sale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL, address TEXT NOT NULL, phone_number INT NOT NULL, user_email TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()

def products():

    conn = sqlite3.connect('Point_of_Sale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS product(prod_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "image TEXT NOT NULL,"
                 "product_name TEXT NOT NULL,"
                 "price NUMERIC NOT NULL," "brand TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()

def bussines_application():

    conn = sqlite3.connect('Point_of_Sale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS business(buss_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "Business_name TEXT NOT NULL,"
                 "products_sold TEXT NOT NULL,"
                 "motivation TEXT NOT NULL,"
                 "contact_number NUMERIC NOT NULL, business_email TEXT NOT NULL, business_address TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()

def shipping_address():
    conn = sqlite3.connect('Point_of_Sale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS shipping(ship_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "recipient_name TEXT NOT NULL,"
                 "recipient_lastname TEXT NOT NULL,"
                 "company TEXT,"
                 "recipient_address TEXT NOT NULL, building_name TEXT NOT NULL, city TEXT NOT NULL, country TEXT NOT NULL, province TEXT NOT NULL, postal_code TEXT NOT NULL, recipient_phone TEXT NOT NUll)")
    print("shipping table created successfully")
    conn.close()

def orders_table():
    conn = sqlite3.connect('Point_of_Sale.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS orders(order_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "order_date TEXT NOT NULL,"
                 "address_delivered TEXT NOT NULL,"
                 "delivery_contact NUMERIC NOT NULL, business_email TEXT NOT NULL, business_address TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()



user_reg()
products()
bussines_application()

def fetch_users():

    with sqlite3.connect('Point_of_Sale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0],data[1], data[2], data[3], data[4],data[5],data[6],data[7])) # append all data to new_data empty list
    return new_data
users = fetch_users()# declare users tables to a variable "users"
#print(users)

username_table = { u.username: u for u in users } # make a dictionary for username
userid_table = { u.id: u for u in users } # make a dictionary for user id
#print(username_table)
#print(userid_table)

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

#authanticate a loggen in user
jwt = JWT(app, authenticate, identity)

@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity

# register a new user
@app.route('/user-registration/', methods=["POST"])
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

            with sqlite3.connect("Point_of_Sale.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user("
                               "first_name,"
                               "last_name,"
                               "username,"
                               "password,address,phone_number,user_email) VALUES(?, ?, ?, ?, ?, ?, ?)", (first_name, last_name, username, password,address,phone_number,user_email))
                conn.commit()
                response["message"] = "User registered successfully "
                response["status_code"] = 201

                return response
        except Exception:
            response["message"] = "Invalid user information supplied"
            response["status_code"] = 401
            return response


# View all registered users
@app.route('/view-users/',methods=['GET'])
@jwt_required()
def view_all_users():
    response = {}
    with sqlite3.connect("Point_of_Sale.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM user")
        posts = cursor.fetchall()
        accumulator = []

        for i in posts:
           accumulator.append({k: i[k] for k in i.keys()})

    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)



# register a new business partner



if __name__ == '__main__':
    app.run(debug=True)

