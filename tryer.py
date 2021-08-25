import sqlite3
conn = sqlite3.connect('Point_of_Sale.db')
print("Opened database successfully")

conn.execute("CREATE TABLE IF NOT EXISTS order(order_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "order_date TEXT NOT NULL,"
                 "address_delivered TEXT NOT NULL,"
                 "delivery_contact NUMERIC NOT NULL, order_number INTEGER NOT NULL, FOREIGN KEY (order_number) REFERENCES user (user_id) )")
print("user table created successfully")
conn.close()