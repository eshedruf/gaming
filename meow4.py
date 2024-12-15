import sqlite3

# Connect to SQLite database (it creates the file if it doesn't exist)
conn = sqlite3.connect('my_database.db')
# Create a cursor object to interact with the database
cursor = conn.cursor()
"""
username - string
password - string
"""


def client_sign_up_if_possible(username1, password1, age1):
    conn = sqlite3.connect('my_database.db')
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()

    """
    collumn 0 - username
    collumn 1 - password
    collumn 2 - age
    """
    for row in rows:
        if username1 == row[0]: #if username exists
            conn.close()
            return False, "failed to sign up, username exists"
    cursor.execute('''
    INSERT INTO users (username, password, age)
    VALUES (?, ?, ?)
    ''', (username1, password1, age1))
    conn.commit()
    conn.close()
    #need to add to user list
    return True, "user added successfully"

def client_log_in_if_possible(username1, password1):
    conn = sqlite3.connect('my_database.db')
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    #need to check if user in active user list
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    """
    collumn 0 - username
    collumn 1 - password
    collumn 2 - age
    """
    users = []
    for row in rows:
        users.append(row[0])
    if username1 not in users:  # if username doesn't exist
        conn.close()
        return False, "failed to log in, username doesn't exist"

    #use username to find password in db
    cursor.execute("SELECT * FROM users WHERE username == ?", (username1,))

    # Step 4: Fetch the row
    row = cursor.fetchone()
    print(row)
    # Step 5: Print the row (it will print as a tuple)
    if str(password1) == row[2]:
        conn.close()
        #add to active user list
        return True, "logged in successfully"
    conn.close()
    return False, "incorrect password"



# Example: Create a table

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY NOT NULL,
    password TEXT NOT NULL,
    age INTEGER NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS mission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_of_range INTEGER NOT NULL,
    end_of_range INTEGER NOT NULL
)
''')

# Example: Insert a record
"""
cursor.execute('''
INSERT INTO users (username, password, age)
VALUES ('esh', '1234', 18)
''')
"""

#remove
"""
cursor.execute('''
DELETE FROM users WHERE username = "noa"
''')
"""
# Commit changes and close the connection
conn.commit()

#print(client_sign_up_if_possible("noam", 1234546, 30))

cursor.execute('SELECT * FROM users')
rows = cursor.fetchall()  # You can also use fetchone() or fetchmany(n)
for row in rows:
    print(row)

cursor.execute('SELECT * FROM users')
rows = cursor.fetchall()  # You can also use fetchone() or fetchmany(n)

# printing collunms
"""
collumn 0 - username
collumn 1 - password
collumn 2 - age
"""
for row in rows:
    print(row[0])

# printing a row based on the username
cursor.execute("SELECT * FROM users WHERE username == 'omer'")

# Step 4: Fetch the row
row = cursor.fetchone()

# Step 5: Print the row (it will print as a tuple)
if row:
    print(row)
else:
    print("No data found for the given username")
conn.close()

print("Database connection and operations completed successfully")
