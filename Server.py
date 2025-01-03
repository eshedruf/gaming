import socket
import sqlite3
from protocol import Protocol
from threading import Thread
import hashlib


class Server:
    def __init__(self):
        self.clients = set()  # do not duplicate the clients
        self.list_of_proc = []  # [[(username, client), (min,max)],...]
        self.temp_ranges = []
        self.HOPS = 10 ** 7
        self.MINIMUM_RANGE = 10 ** 9
        self.MAXIMUM_RANGE = 10 ** 10
        self.INVALID_COMMANDO = "Your command is invalid, try again."
        self.protocol = Protocol()
        self.run = True

    def handle_client(self, client_socket, server_socket):  # Takes client socket as argument.
        """Handles a single client connection."""
        while self.run:
            valid, commando, msg_list = self.protocol.get_msg(client_socket)
            if self.protocol.check_cmd(commando) and valid:
                valid = self.handle_response(client_socket, commando, msg_list)
                if not valid:
                    continue

    def handle_response(self, client_socket, command, msg_list):
        valid, message = None, None
        if command == self.protocol.CMDS[0]:  # signup
            username = msg_list[0]
            password = msg_list[1]
            age = msg_list[2]
            valid, message = self.client_sign_up_if_possible(username, password, age)
            print(message)
            num = hashlib.md5(str(1_030_000_000).encode()).hexdigest()
            msg_md5 = self.protocol.create_msg(self.protocol.CMDS[-1], [num])
            print(msg_md5)
            client_socket.send(msg_md5)
            self.handle_client_range(client_socket, username)

        if command == self.protocol.CMDS[1]:  # login
            username = msg_list[0]
            password = msg_list[1]
            valid, message = self.client_log_in_if_possible(username, password)
            print(message)
            client_socket.send(self.protocol.create_msg(self.protocol.CMDS[3], [valid]))
            if valid:
                num = hashlib.md5(str(1_030_000_000).encode()).hexdigest()
                msg_md5 = self.protocol.create_msg(self.protocol.CMDS[-1], [num])
                client_socket.send(msg_md5)
                self.handle_client_range(client_socket, username)

        if command == self.protocol.CMDS[3]:  # check
            status = msg_list[0]
            number = msg_list[1]
            if status == self.protocol.FOUND:
                print(number)
                for c in self.clients:
                    c.close()
                self.run = False
            if status == self.protocol.NOT_FOUND and number == "-1":
                self.handle_client_range(client_socket, self.get_username_of_client(client_socket))

        return True

    def pick_biggest_max_range(self):
        maximums = []
        if len(self.list_of_proc) == 0:
            return self.MINIMUM_RANGE
        for i in range(0, len(self.list_of_proc)):
            maximums.append(self.list_of_proc[i][1][1])
        return max(maximums)

    def get_username_of_client(self, client_socket):
        for proc in self.list_of_proc:
            for tuples in proc:
                if client_socket in tuples:
                    return tuples[1]

    def handle_client_range(self, client_socket, username):  # without handling disconnections...yet
        min_range = self.pick_biggest_max_range()
        max_range = min_range + self.HOPS
        if self.is_client_in_list(username):
            for proc in self.list_of_proc:
                if (username, client_socket) in proc:
                    proc[1] = (min_range, max_range)
        else:
            self.list_of_proc.append([(username, client_socket), (min_range, max_range)])
        range_msg = self.protocol.create_msg(self.protocol.CMDS[-2], [min_range, max_range])
        print(range_msg)
        client_socket.send(range_msg)
        print("yes")

    def is_client_in_list(self, username):
        for proc in self.list_of_proc:
            if username == proc[0][0]:
                return True
        else:
            return False

    def client_log_in_if_possible(self, username1, password1):
        conn = sqlite3.connect('my_database.db')
        # Create a cursor object to interact with the database
        cursor = conn.cursor()
        # need to check if user in active user list
        if self.is_client_in_list(username1):  # right code
            conn.close()
            return False, "User is not in the active user list"
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

        # use username to find password in db
        cursor.execute("SELECT * FROM users WHERE username == ?", (username1,))

        # Step 4: Fetch the row
        row = cursor.fetchone()
        print(row)
        # Step 5: Print the row (it will print as a tuple)
        if str(password1) == row[2]:
            conn.close()
            # add to active user list
            return True, "logged in successfully"
        conn.close()
        return False, "incorrect password"

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
        INSERT INTO mission (client, start_of_range, end_of_range, status)
        VALUES (?, ?, ?, 'PENDING')
        ''', (clientnum, start_of_range, end_of_range))
        conn.commit()
        conn.close()

    def update_scaned_range(self, clientnum, status):
        conn = sqlite3.connect('my_database.db')
        # Create a cursor object to interact with the database
        cursor = conn.cursor()
        cursor.execute("""UPDATE mission SET status = ? WHERE client = ? AND status = 'PENDING'""", (status, clientnum))
        conn.commit()
        conn.close()

    # Example: Create a table

    def give_new_range_to_client(self, clientnum, hop, status=None):
        conn = sqlite3.connect('my_database.db')
        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        if status != None:
            self.update_scaned_range(clientnum, status)

        cursor.execute('SELECT * FROM mission')
        rows = cursor.fetchall()  # You can also use fetchone() or fetchmany(n)
        for row in rows:
            if row[4] == 'YES':  # if status == 'YES'
                conn.commit()
                conn.close()
                return None
        for row in rows:
            if row[4] == 'CRASHED':  # if status == 'CRASHED'
                cursor.execute("""UPDATE mission SET client = ?, status = 'PENDING' WHERE status = 'CRASHED'""",
                               (clientnum,))
                conn.commit()
                conn.close()
                return row[2], row[3]
        self.add_range_to_mission(clientnum, rows[-1][3] + 1, hop)
        conn.commit()
        conn.close()
        return rows[-1][2] + 1, rows[-1][2] + hop

    def update_client_crashing(self, clientnum):
        self.update_scaned_range(clientnum, 'CRASHED')

    def main(self):
        print("server start")
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', 8820))
        server_socket.listen(5)  # Increase the queue size to handle more connections

        while self.run:
            client_socket, client_address = server_socket.accept()
            print("New client connected:", client_address)
            self.clients.add(client_socket)

            # Start the client handling in a new thread
            client_thread = Thread(target=self.handle_client, args=(client_socket, server_socket))
            client_thread.daemon = True  # Ensure threads are terminated when the main program ends
            client_thread.start()

        server_socket.close()  # Ensure server socket is closed when stopping


if __name__ == "__main__":
    s = Server()
    s.main()
