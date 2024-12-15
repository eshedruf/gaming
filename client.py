import hashlib
import multiprocessing
import protocol
import socket
import time

class Client:
    def __init__(self, target_md5, range_start, range_end):
        """
        Initializes the Client with the target MD5 hash and the search range.
        """
        self.protocol = protocol.Protocol()
        self.server_ip = "127.0.0.1"
        self.server_port = 8820
        self.target_md5 = target_md5
        self.range_start = range_start
        self.range_end = range_end
        self.cpu_count = multiprocessing.cpu_count()
        self.client_socket = socket.socket()


    def number_to_md5(self, num):
        num_hash = hashlib.md5(str(num).encode()).hexdigest()
        return num_hash

    def connect(self):
        self.client_socket.connect((self.server_ip, self.server_port))
        bool = True
        while bool:
            sign_log = input("sign in or log in? ")
            if sign_log == "sign_in" or sign_log == "log_in":
                bool = False
        username = input("Enter username: ")
        password = input("Enter password: ")
        if sign_log == "sign in":
            self.protocol.create_msg("SIGNUP", [username, password])
        elif sign_log == "log in":
            self.protocol.create_msg("LOGIN", [username, password])
        self.target_md5 = self.protocol.get_msg(self.client_socket) # should get give md5

    def compute_md5_and_check(self, start, end, target_hash):
        """
        Computes MD5 hashes for numbers in the range [start, end).
        Returns (True, number) if target_hash is found, otherwise (False, -1).
        """
        for num in range(start, end):
            num_hash = hashlib.md5(str(num).encode()).hexdigest()
            if num_hash == target_hash:
                return True, num
        return False, -1

    def find_md5_hash_in_range(self):
        """
        Splits the range across available CPU cores and checks for the target MD5 hash.
        """
        step = (self.range_end - self.range_start) // self.cpu_count
        ranges = [
            (self.range_start + i * step, self.range_start + (i + 1) * step)
            for i in range(self.cpu_count)
        ]
        # Ensure the last range ends at 'self.range_end'
        ranges[-1] = (ranges[-1][0], self.range_end)

        # Use multiprocessing pool to parallelize the work
        with multiprocessing.Pool(self.cpu_count) as pool:
            results = pool.starmap(
                self.compute_md5_and_check, [(r[0], r[1], self.target_md5) for r in ranges]
            )

        # Check results for a successful match
        for is_found, num in results:
            if is_found:
                return True, num
        return False, -1

    def run(self):
        """
        Runs the search process and prints the result with the elapsed time.
        """
        print("Starting search...")
        start_time = time.time()

        found, number = self.find_md5_hash_in_range()

        end_time = time.time()
        elapsed_time = end_time - start_time

        if found:
            print(f"Hash found! The number is: {number}")
        else:
            print("Hash not found in the range.")
        print(f"Search completed in {elapsed_time:.2f} seconds.")

    def actual_run(self):
        """
        Runs the search process and prints the result with the elapsed time.
        """
        print("Starting search...")
        start_time = time.time()

        self.connect()
        data = self.protocol.get_msg(self.client_socket) # sohuld get give range
        self.range_start = data[0]
        self.range_end = data[1]

        found, number = self.find_md5_hash_in_range()

        end_time = time.time()
        elapsed_time = end_time - start_time

        if found:
            print(f"Hash found! The number is: {number}")
            self.send({number})
        else:
            print("Hash not found in the range.")
            self.send(-1)
        print(f"Search completed in {elapsed_time:.2f} seconds.")

    def send(self, found):
        if found == -1:
            msg = self.protocol.create_msg("CHECK", ["NOT_FOUND", found])
        else:
            msg = self.protocol.create_msg("CHECK", ["FOUND", found])
        self.client_socket.send(msg)



if __name__ == "__main__":
    target_md5 = input("Enter the target MD5 hash: ")
    range_start = 1_000_000_000_000
    range_end = range_start + 10_000_000

    client = Client(target_md5, range_start, range_end)
    client.run()
    print(client.number_to_md5(1_000_005_000_000))
