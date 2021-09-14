import sqlite3
#Connecting to sqlite
conn = sqlite3.connect('final_backend.db')

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#print('\nColumns in EMPLOYEE table:')
#data = cursor.execute('''SELECT * FROM shipment''')
#for column in data.description:
    #print(column[0])

# Display data
#print('\nData in EMPLOYEE table:')
#data = cursor.execute('''SELECT * FROM shipment''')
#for row in data:
    #print(row)

# Commit your changes in the database
#conn.commit()

# Closing the connection
#conn.close()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

print(cursor.fetchall())

#Doping EMPLOYEE table if already exists
#cursor.execute("DROP TABLE shipment")
#print("Table dropped... ")

#Commit your changes in the database
#conn.commit()

#Closing the connection
#conn.close()