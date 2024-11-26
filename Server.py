import multiprocessing
import socket
import sys
import random
import time
from threading import Thread

clients = set()  # do not duplicate the clients


def broadcast(data, name, current_client):
    """Broadcasts a message to all the clients."""
    for sock in clients:
        if sock != current_client:
            sock.send("1".encode())
            sock.send(str(len(data)).encode())
            sock.send(name.encode())
            sock.send(data)


def handle_client(client_socket, server_socket):  # Takes client socket as argument.
    """Handles a single client connection."""
    while True:
        client_info = client_socket.recv(1024)
        client_info_str = client_info.decode('ascii')  # convert the bytes to string
        print("got from client")
        if client_info_str == "":
            client_socket.close()
            server_socket.close()
            print("client close the socket")
            sys.exit()
        if client_info_str == "Quit":
            client_socket.close()
        print("server got: " + client_info_str)


def main():
    print("server start")
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8820))
    server_socket.listen(1)

    while True:
        (client_socket, client_address) = server_socket.accept()
        print("New client connect")
        clients.add(client_socket)
        client_counter = len(clients)
        client_socket.send(str(client_counter).encode())
        a = Thread(target=handle_client, args=(client_socket, server_socket))
        a.start()


main()
