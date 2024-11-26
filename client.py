import sys
import socket
from protocol import Protocol
from threading import Thread


class Client:
    def __init__(self):
        self.p1 = Protocol()

    def client_recv_from_server(self, my_socket):
        data = my_socket.recv(1024)
        print("Server : " + data.decode('ascii'))


    def run(self):
        print("client start")
        my_socket = socket.socket()
        my_socket.connect(("127.0.0.1", 8820))
        print("client connect to server")
        client_num = int(my_socket.recv(1024).decode())
        while True:
            name = input("enter name: ")
            password = input("enter password: ")
            age = input("enter age: ")
            msg = self.p1.sign_up(name, password, age)


if __name__ == "__main__":
    c1 = Client()
    c1.run()
