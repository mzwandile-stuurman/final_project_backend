import sqlite3
#Connecting to sqlite
conn = sqlite3.connect('Final_Project.db')

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

print(cursor.fetchall())

#Doping EMPLOYEE table if already exists
#cursor.execute("DROP TABLE business")
#print("Table dropped... ")

#Commit your changes in the database
#conn.commit()

#Closing the connection
#conn.close()