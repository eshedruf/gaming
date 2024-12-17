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

def add_range_to_mission(clientnum, start_of_range, hop):
    conn = sqlite3.connect('my_database.db')
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    end_of_range = start_of_range + hop - 1
    cursor.execute('''
    INSERT INTO mission (client, start_of_range, end_of_range, status)
    VALUES (?, ?, ?, 'PENDING')
    ''', (clientnum, start_of_range, end_of_range))
    conn.commit()
    conn.close()
# Example: Create a table
def update_scaned_range(clientnum, status):
    conn = sqlite3.connect('my_database.db')
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    cursor.execute("""UPDATE mission SET status = ? WHERE client = ? AND status = 'PENDING'""", (status, clientnum))
    conn.commit()
    conn.close()

#return start and end of range in a tuple or None if num was found, status = None if client just loged in
def give_new_range_to_client(clientnum, hop, status = None):
    conn = sqlite3.connect('my_database.db')
    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    if status != None:
        update_scaned_range(clientnum, status)

    cursor.execute('SELECT * FROM mission')
    rows = cursor.fetchall()  # You can also use fetchone() or fetchmany(n)
    for row in rows:
        if row[4] == 'YES': #if status == 'YES'
            conn.commit()
            conn.close()
            return None
    for row in rows:
        if row[4] == 'CRASHED': #if status == 'CRASHED'
            cursor.execute("""UPDATE mission SET client = ?, status = 'PENDING' WHERE status = 'CRASHED'""",(clientnum,))
            conn.commit()
            conn.close()
            return row[2], row[3]
    add_range_to_mission(clientnum, rows[-1][3] + 1, hop)
    conn.commit()
    conn.close()
    return rows[-1][2] + 1, rows[-1][2] + hop

def update_client_crashing(clientnum):
    update_scaned_range(clientnum, 'CRASHED')

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
    client STRING NOT NULL,
    start_of_range INTEGER NOT NULL,
    end_of_range INTEGER NOT NULL,
    status STRING NOT NULL
)
''')

# Example: Insert a record
"""
cursor.execute('''
INSERT INTO users (username, password, age)
VALUES ('omer', '12345', 20)
''')
"""

#remove
"""
cursor.execute('''
DELETE FROM users WHERE username = "noa"
''')
"""

"""
cursor.execute('''
DELETE FROM mission WHERE client = "c1"
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

#add_range_to_mission('c3', 1020000000, 10 ** 7)
#update_scaned_range('c3', 'CRASHED')
give_new_range_to_client('c1', 10 ** 7, 'NO')

cursor.execute('SELECT * FROM mission')
rows = cursor.fetchall()  # You can also use fetchone() or fetchmany(n)
for row in rows:
    print(row)
conn.close()
print("Database connection and operations completed successfully")
