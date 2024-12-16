import socket
import sqlite3
import sys
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

    def handle_client(self, client_socket, server_socket):  # Takes client socket as argument.
        """Handles a single client connection."""
        while True:
            valid, commando, msg_list = self.protocol.get_msg(client_socket)
            print(msg_list, commando)
            if self.protocol.check_cmd(commando) and valid:
                valid = self.handle_response(client_socket, commando, msg_list, server_socket)
                if not valid:
                    continue
            else:
                client_socket.send(self.INVALID_COMMANDO.encode())
                continue

    def handle_response(self, client_socket, command, msg_list, server_socket):
        valid, message = None, None
        if command == self.protocol.CMDS[0]:  # signup
            username = msg_list[0]
            password = msg_list[1]
            age = msg_list[2]
            valid, message = self.client_sign_up_if_possible(username, password, age)
            print(message)
            num = hashlib.md5(str(1_234_567_890).encode()).hexdigest()
            msg_md5 = self.protocol.create_msg(self.protocol.CMDS[-1], [num])
            client_socket.send(msg_md5)
            self.handle_client_range(client_socket, username)

        if command == self.protocol.CMDS[1]:  # login
            username = msg_list[0]
            password = msg_list[1]
            valid, message = self.client_log_in_if_possible(username, password)
            print(message)
            num = hashlib.md5(str(1_234_567_890).encode()).hexdigest()
            msg_md5 = self.protocol.create_msg(self.protocol.CMDS[-1], [num])
            client_socket.send(msg_md5)
            self.handle_client_range(client_socket, username)

        if command == self.protocol.CMDS[3]:  # check
            status = msg_list[0]
            number = msg_list[1]
            if status == self.protocol.FOUND:
                print("The number: " + number)
                for c in self.clients:
                    c.close()
                server_socket.stop()
                sys.exit()
            if status == self.protocol.NOT_FOUND and number == -1:
                self.handle_client_range(client_socket, self.get_username_of_client(client_socket))

        if valid:
            return valid

    def pick_biggest_max_range(self):
        maximums = []
        if len(self.list_of_proc) == 0:
            return self.MINIMUM_RANGE
        for i in self.list_of_proc:
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
        if self.is_client_in_list(username, client_socket):
            for proc in self.list_of_proc:
                if (username, client_socket) in proc:
                    proc[1] = (min_range, max_range)
        else:
            self.list_of_proc.append([(username, client_socket), (min_range, max_range)])
        range_msg = self.protocol.create_msg(self.protocol.CMDS[-2], [min_range, max_range])
        client_socket.send(range_msg)

    def is_client_in_list(self, username, client_socket):
        for proc in self.list_of_proc:
            if (username, client_socket) in proc:
                return True
        else:
            return False

    def client_log_in_if_possible(self, username1, password1):
        conn = sqlite3.connect('my_database.db')
        # Create a cursor object to interact with the database
        cursor = conn.cursor()
        # need to check if user in active user list
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        """
        collumn 0 - id
        collumn 1 - username
        collumn 2 - password
        collumn 3 - age
        """
        users = []
        for row in rows:
            users.append(row[1])
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
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()

        """
        collumn 0 - id
        collumn 1 - username
        collumn 2 - password
        collumn 3 - age
        """
        for row in rows:
            if username1 == row[1]:  # if username exists
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

    def main(self):
        print("server start")
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', 8820))
        server_socket.listen(1)

        while True:
            (client_socket, client_address) = server_socket.accept()
            print("New client connect")
            self.clients.add(client_socket)
            a = Thread(target=self.handle_client, args=(client_socket, server_socket))
            a.start()


if __name__ == "__main__":
    s = Server()
    s.main()
