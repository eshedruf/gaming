import socket
import sqlite3
import threading

from protocol import Protocol
from threading import Thread
import hashlib


class Server:
    def __init__(self):
        self.clients = set()  # do not duplicate the clients
        self.list_of_proc = []  # [(username, client, aes),...]
        self.temp_ranges = []
        self.HOPS = 10 ** 7
        self.MINIMUM_RANGE = 10 ** 9
        self.MAXIMUM_RANGE = 10 ** 10
        self.INVALID_COMMANDO = "Your command is invalid, try again."
        self.protocol = Protocol()
        self.run = True
        self.lock = threading.Lock()
        self.PRIVATE_KEY, self.PUBLIC_KEY = self.protocol.generate_rsa_keys()
        self.PUBLIC_KEY_PEM = self.protocol.serialize_public_key(self.PUBLIC_KEY)

    def handle_client(self, client_socket, server_socket):
        try:
            # Generate RSA keys
             # Serialize the public key to send to the client
            # Receive the encrypted AES key
            client_socket.send(self.protocol.create_msg(self.protocol.CMDS[4], [self.PUBLIC_KEY_PEM]))
            client_aes_key = self.get_client_aes(client_socket)
            while self.run:
                valid, commando, msg_list = self.protocol.get_msg(client_socket, client_aes_key)
                if self.protocol.check_cmd(commando) and valid:
                    valid = self.handle_response(client_socket, commando, msg_list, server_socket, client_aes_key)
                    if not valid:
                        continue

        except ConnectionResetError:
            username = self.get_username_of_client(client_socket)
            for tuple1 in self.list_of_proc:
                if client_socket in tuple1:
                    self.list_of_proc.remove(tuple1)
            self.lock.acquire()
            self.update_client_crashing(username)
            self.lock.release()

    def get_client_aes(self, client_socket):
        for tuple1 in self.list_of_proc:
            if client_socket in tuple1:
                return tuple1[2]


    def handle_response(self, client_socket, command, msg_list, server_socket, aes_key=None):
        valid, message = None, None
        if command == self.protocol.CMDS[0]:  # signup
            username = msg_list[0]
            password = msg_list[1]
            age = msg_list[2]
            self.lock.acquire()
            valid, message = self.client_sign_up_if_possible(username, password, age)
            self.lock.release()
            print(message)
            client_socket.send(self.protocol.create_msg(self.protocol.CMDS[3], [valid], aes_key))
            if valid:
                num = hashlib.md5(str(1_200_000_000).encode()).hexdigest()
                msg_md5 = self.protocol.create_msg(self.protocol.CMDS[-1], [num], aes_key)
                client_socket.send(msg_md5)
                self.list_of_proc.append((username, client_socket))
                self.handle_client_range(client_socket, username)

        if command == self.protocol.CMDS[1]:  # login
            username = msg_list[0]
            password = msg_list[1]
            self.lock.acquire()
            valid, message = self.client_log_in_if_possible(username, password)
            self.lock.release()
            print(message)
            client_socket.send(self.protocol.create_msg(self.protocol.CMDS[3], [valid]))
            if valid:
                num = hashlib.md5(str(1_200_000_000).encode()).hexdigest()
                msg_md5 = self.protocol.create_msg(self.protocol.CMDS[-1], [num])
                client_socket.send(msg_md5)
                self.list_of_proc.append((username, client_socket))
                self.handle_client_range(client_socket, username)

        if command == self.protocol.CMDS[3]:  # check
            status = msg_list[0]
            number = msg_list[1]
            if status == self.protocol.FOUND:
                print(number)
                server_socket.close()
                for c in self.clients:
                    c.close()
                self.run = False
            if status == self.protocol.NOT_FOUND and number == "-1":
                self.handle_client_range(client_socket, self.get_username_of_client(client_socket), status)

        if command == self.protocol.CMDS[4]: # crypt
            aes_key_encrypted_by_public = msg_list[0]
            self.aes_key = self.protocol.rsa_decrypt(self.PRIVATE_KEY, aes_key_encrypted_by_public)
        return True

    def get_username_of_client(self, client_socket):
        for proc in self.list_of_proc:
            if client_socket in proc:
                return proc[0]

    def handle_client_range(self, client_socket, username, status=None):
        min_range, max_range = self.give_new_range_to_client(username, status)
        range_msg = self.protocol.create_msg(self.protocol.CMDS[-2], [min_range, max_range])
        print(range_msg)
        client_socket.send(range_msg)

    def update_client_crashing(self, username):
        """Handles a client's crash and adds its range to temp_ranges."""
        self.update_scaned_range(username, 'CRASHED')

    def is_client_in_list(self, username):
        for proc in self.list_of_proc:
            if username == proc[0]:
                return True
        else:
            return False

    def client_log_in_if_possible(self, username1, password1):
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()

        # Check if the user is already in the active user list
        if self.is_client_in_list(username1):
            conn.close()
            return False, "User is already in the active user list"

        # Query the database for the user
        cursor.execute("SELECT * FROM users WHERE username == ?", (username1,))
        row = cursor.fetchone()

        # Check if the user exists
        if row is None:
            conn.close()
            return False, "Failed to log in, username doesn't exist"

        # Check if the password matches
        if str(password1) == row[1]:  # Compare with the password column
            conn.close()
            return True, "Logged in successfully"

        conn.close()
        return False, "Incorrect password"

    def client_sign_up_if_possible(self, username1, password1, age1):
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
            if username1 == row[0]:  # if username exists
                conn.close()
                return False, "failed to sign up, username exists"
        cursor.execute('''
        INSERT INTO users (username, password, age)
        VALUES (?, ?, ?)
        ''', (username1, password1, age1))
        conn.commit()
        conn.close()
        # need to add to user list
        return True, "user added successfully"

    def add_range_to_mission(self, clientnum, start_of_range, hop):
        conn = sqlite3.connect('my_database.db')
        # Create a cursor object to interact with the database
        cursor = conn.cursor()
        end_of_range = start_of_range + hop - 1
        cursor.execute('''
        INSERT INTO mission (username, start_of_range, end_of_range, status)
        VALUES (?, ?, ?, 'PENDING')
        ''', (clientnum, start_of_range, end_of_range))
        conn.commit()
        conn.close()

    def update_scaned_range(self, clientnum, status):
        conn = sqlite3.connect('my_database.db')
        # Create a cursor object to interact with the database
        cursor = conn.cursor()
        cursor.execute("""UPDATE mission SET status = ? WHERE username = ? AND status = 'PENDING'""", (status, clientnum))
        conn.commit()
        conn.close()

    # Example: Create a table

    def give_new_range_to_client(self, username, status=None):
        conn = sqlite3.connect('my_database.db')
        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        if status is not None:
            self.update_scaned_range(username, status)

        cursor.execute('SELECT * FROM mission')
        rows = cursor.fetchall()  # You can also use fetchone() or fetchmany(n)
        for row in rows:
            if row[4] == 'FOUND':  # if status == 'YES'
                conn.commit()
                conn.close()
                return None
        for row in rows:
            if row[4] == 'CRASHED':  # if status == 'CRASHED'
                cursor.execute("""UPDATE mission SET username = ?, status = 'PENDING' WHERE status = 'CRASHED'""",
                               (username,))
                conn.commit()
                conn.close()
                return row[2], row[3]
        if rows == []:
            self.add_range_to_mission(username, self.MINIMUM_RANGE, self.HOPS)
            conn.commit()
            conn.close()
            return self.MINIMUM_RANGE, self.MINIMUM_RANGE + self.HOPS + 1
        else:
            self.add_range_to_mission(username, rows[-1][3] + 1, self.HOPS)
        conn.commit()
        conn.close()
        return rows[-1][2] + 1, rows[-1][2] + self.HOPS + 1

    def main(self):
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()
        cursor.execute("""DROP TABLE IF EXISTS mission""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS mission (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username STRING NOT NULL,
        start_of_range INTEGER NOT NULL,
        end_of_range INTEGER NOT NULL,
        status STRING NOT NULL);""")
        conn.commit()
        conn.close()
        print("server start")
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', 8818))
        server_socket.listen(0)  # Increase the queue size to handle more connections

        while self.run:
            try:
                client_socket, client_address = server_socket.accept()
                print("New client connected:", client_address)
                self.clients.add(client_socket)

                # Start the client handling in a new thread
                client_thread = Thread(target=self.handle_client, args=(client_socket, server_socket))
                client_thread.daemon = True  # Ensure threads are terminated when the main program ends
                client_thread.start()
            except OSError:
                break


if __name__ == "__main__":
    s = Server()
    s.main()
