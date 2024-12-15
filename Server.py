import socket
import sqlite3
import sys
from protocol import Protocol
from threading import Thread


class Server:
    def __init__(self):
        self.clients = set()  # do not duplicate the clients
        self.list_of_proc = []  # [[(username, client), (min,max)],...]
        self.temp_ranges = []
        self.HOPS = 10 ** 6
        self.MINIMUM_RANGE = 10 ** 9
        self.MAXIMUM_RANGE = 10 ** 10
        self.INVALID_COMMANDO = "Your command is invalid, try again."

    def handle_client(self, client_socket, server_socket):  # Takes client socket as argument.
        """Handles a single client connection."""
        while True:
            valid, commando, msg_list = Protocol().get_msg(server_socket)

            if Protocol().check_cmd(commando) and valid:
                valid = self.handle_response(username, password, age, command)
                if not valid:
                    continue
            else:
                client_socket.send(self.INVALID_COMMANDO.encode())
                continue
            self.handle_client_range(client_socket, username)
            status_length = client_socket.recv(4)
            status = client_socket.recv(status_length)
            if status == self.FOUND:
                ... # take the
                for c in self.clients:
                    c.close()
                server_socket.stop()
                sys.exit()

            if status == self.NOT_FOUND:
                self.handle_client_range(client_socket, username)

    def handle_response(self, client_socket, command, msg_list):
        valid, message = None, None
        if command == Protocol().CMDS[0]:
            username = msg_list[0]
            password = msg_list[1]
            age = msg_list[2]
            valid, message = self.client_sign_up_if_possible(username, password, age)
        if command == Protocol().CMDS[1]:
            username = msg_list[0]
            password = msg_list[1]
            valid, message = self.client_log_in_if_possible(username, password)
        if command == Protocol().CMDS[3]: # check
            
        if valid:
            return valid
        else:
            client_socket.send((str(len(message)) + Protocol().SEPERATOR + message).encode())

    def pick_biggest_max_range(self):
        maximums = []
        if len(self.list_of_proc) == 0:
            return self.MINIMUM_RANGE
        for i in self.list_of_proc:
            maximums.append(self.list_of_proc[i][1][1])
        return max(maximums)

    def handle_client_range(self, client_socket, username):  # without handling disconnections...yet
        min_range = self.pick_biggest_max_range()
        max_range = min_range + self.HOPS
        if self.is_client_in_list(username, client_socket):
            for proc in self.list_of_proc:
                if (username, client_socket) in proc:
                    proc[1] = (min_range, max_range)
        else:
            self.list_of_proc.append([(username, client_socket), (min_range, max_range)])
        md5_range_msg = str(22) + str(min_range) + Protocol().SEPERATOR + str(max_range)
        client_socket.send((md5_range_msg.encode()))

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
            client_counter = len(self.clients)
            client_socket.send(str(client_counter).encode())
            a = Thread(target=self.handle_client, args=(client_socket, server_socket))
            a.start()


if __name__ == "__main__":
    s = Server()
    s.main()
