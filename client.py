import os
import socket
import threading
import time
import multiprocessing
import hashlib
from threading import Thread


# value: shared memory between processes
# current: gets info about the current process

class Client:
    def __init__(self):
        self.start_time = time.time()
        self.core_num = os.cpu_count()
        self.range_length = 24
        self.my_socket = socket.socket()
        self.num_processes = self.core_num
        self.target_md5 = "ce039324e5a57749db69538be0252854"
        self.len = 10
        self.start = 1_000_010_000_000
        self.end = 1_000_020_000_000
        self.step = (self.end - self.start) // self.num_processes
        self.final_md5 = self.target_md5
        self.found = False
        self.found_number = -1
        # self.my_socket.connect(("127.0.0.1", 8820))
        # self.processes
        # self.name = input("enter name: ")
        # self.password = input("enter password: ")
        # self.age = input("enter age: ")

    def number_to_md5(self, number):
        return hashlib.md5(str(number).encode()).hexdigest()

    def run(self):
        print("client start")
        print("client connect to server")
        client_num = int(self.my_socket.recv(1024).decode())

    def compute(self):
        self.stop_computing = False
        with multiprocessing.Pool(processes=self.num_processes) as pool:
            step = (self.end - self.start) // self.num_processes
            # adds to the last tuple the rest that is left over (because the step may be rounded down to be an integer)
            ranges = [(self.start + i * step, self.start + (i + 1) * step) if i < self.num_processes - 1
                      else (self.start + i * step, self.end)
                      for i in range(self.num_processes)]
            results = pool.starmap(self.compute_single_process, ranges)

            for is_correct, num in results:
                if is_correct:
                    print("sjghsnlfhs")
                    self.found = True
                    self.found_number = num
                    break
        self.send()

    # includes start excludes end
    def compute_single_process(self, start, end):
        for i in range(start, end):
            md5 = hashlib.md5(str(i).encode()).hexdigest()
            if md5 == self.final_md5:
                return True, i

        return False, -1

    def send(self):
        if self.found:
            message = ("0 " + str(self.found_number))
        else:
            #  message = found does_want_another_range
            message = ("0" + "1")  # for now always want another range. in the future the user will choose

        print(message)


if __name__ == "__main__":
    c1 = Client()
    start_time = time.time()
    # Input the range and the MD5 hash

    # Find the matching number
    c1.compute()

    elapsed_time = time.time() - c1.start_time
    print(f"Time elapsed since the code started: {elapsed_time:.2f} seconds")

    # c1.run()
