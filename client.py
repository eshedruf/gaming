import sys
import socket
import multiprocessing
from protocol import Protocol
from threading import Thread


class Client:
    def __init__(self):
        self.p1 = Protocol()
        self.core_num = 4
        self.range_length = 24
        self.my_socket = socket.socket()
        self.my_socket.connect(("127.0.0.1", 8820))
        self.processes
        self.name = input("enter name: ")
        self.password = input("enter password: ")
        self.age = input("enter age: ")


    def sign_up(self):
        length, msg = self.p1.sign_up(self.name, self.password, self.age)
        self.my_socket.send(length)
        self.my_socket.send(msg)


    def client_recv_from_server(self, my_socket):
        data = my_socket.recv(1024)
        print("Server : " + data.decode('ascii'))

    def find_md5(self):
        numbers = self.my_socket.recv(self.range_length).decode()
        num1 = numbers.split("\r\n")[0]
        num2 = numbers.split("\r\n")[1]



    def run(self):
        print("client start")
        print("client connect to server")
        client_num = int(self.my_socket.recv(1024).decode())



if __name__ == "__main__":
    c1 = Client()
    c1.run()
