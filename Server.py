import socket
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
        self.LOGIN = "LOGIN"
        self.SIGNUP = "SIGNUP"
        self.COMMANDS = [self.LOGIN, self.SIGNUP]
        self.INVALID_COMMANDO = "Your command is invalid, try again."
        self.FOUND = "FOUND"
        self.NOT_FOUND = "NOT_FOUND"

    def handle_client(self, client_socket, server_socket):  # Takes client socket as argument.
        """Handles a single client connection."""
        while True:
            client_msg_length = client_socket.recv(4)
            msg = client_socket.recv(client_msg_length)
            command = msg.split(Protocol().SEPERATOR)[0]
            username = msg.split(Protocol().SEPERATOR)[1]
            password = msg.split(Protocol().SEPERATOR)[2]
            age = msg.split(Protocol().SEPERATOR)[3]
            print(username, password, age)
            if self.check_valid_command(command):
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
                for c in self.clients:
                    c.close()
                server_socket.stop()
                sys.exit()

            if status == self.NOT_FOUND:
                self.handle_client_range(client_socket, username)

    def handle_response(self, name, password, age, command):
        if command == self.LOGIN:
            oren1(name, password, age)
            # return true if he logs in :D
            return True
        if command == self.SIGNUP:
            oren2(name, password, age)
            return True

    def pick_biggest_max_range(self):
        maximums = []
        if len(self.list_of_proc) == 0:
            return self.MINIMUM_RANGE
        for i in self.list_of_proc:
            maximums.append(self.list_of_proc[i][1][1])
        return max(maximums)

    def handle_client_range(self, client_socket, username): # without handling disconnections...yet
        min_range = self.pick_biggest_max_range()
        max_range = min_range + self.HOPS
        if self.is_client_in_list(username, client_socket):
            for proc in self.list_of_proc:
                if (username, client_socket) in proc:
                    proc[1] = (min_range, max_range)
        else:
            self.list_of_proc.append([(username, client_socket), (min_range, max_range)])
        md5_range_msg = str(min_range) + Protocol().SEPERATOR + str(max_range)
        client_socket.send((md5_range_msg.encode()))

    def is_client_in_list(self, username, client_socket):
        for proc in self.list_of_proc:
            if (username, client_socket) in proc:
                return True
        else:
            return False
    def check_valid_command(self, command):
        if command in self.COMMANDS:
            return True
        return False

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
