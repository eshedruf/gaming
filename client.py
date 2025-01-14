import hashlib
import multiprocessing
import sys
import tkinter
import protocol
import socket
import time
from window import Window
from Crypto.Random import get_random_bytes


class Client:
    def __init__(self):
        """
        Initializes the Client with the target MD5 hash and the search range.
        """
        self.protocol = protocol.Protocol()
        self.server_ip = "127.0.0.1"
        self.server_port = 8818
        self.target_md5 = "g"
        self.range_start = 3
        self.range_end = 6
        self.cpu_count = multiprocessing.cpu_count()
        self.client_socket = socket.socket()
        self.finish = False
        self.window = Window()
        self.server_public_key = None
        self.aes_key = None
        self.cipher_for_encryption = None
        self.cipher_for_decryption = None

    def number_to_md5(self, num):
        num_hash = hashlib.md5(str(num).encode()).hexdigest()
        return num_hash

    def connect(self):
        print("client connecting to server...")
        self.client_socket.connect((self.server_ip, self.server_port))
        is_valid, command, msg_parts = self.protocol.get_msg(self.client_socket)
        if is_valid and command == self.protocol.CMDS[4]:
            self.server_public_key = msg_parts[0]
            print(type(self.server_public_key))
            print(self.server_public_key)
            print(msg_parts[0])
            self.aes_key = get_random_bytes(self.protocol.KEY_LENGTH)
            rsa_cipher = self.protocol.get_rsa_cipher(self.server_public_key)
            #encrypted_aes_key = self.protocol.rsa_encrypt_message(self.aes_key, rsa_cipher)
            msg = self.protocol.create_msg(self.protocol.CMDS[4], [self.aes_key], rsa_cipher)
            self.client_socket.send(msg)
            self.cipher_for_encryption = self.protocol.get_aes_cipher(self.aes_key)
            self.cipher_for_decryption = self.protocol.get_aes_cipher(self.aes_key)
        bool = True
        age = "-1"
        while bool:
            self.window.update()
            if self.window.submitted == True:
                username = self.window.username_val
                password = self.window.password_val
                age = self.window.age_val
                print(username)
                print(password)
                print(age)

                if age != "-1":
                    # sign up
                    self.client_socket.send(self.protocol.create_msg("SIGNUP", [username, password, age], self.cipher_for_encryption))
                    is_valid = self.protocol.get_msg(self.client_socket, self.cipher_for_decryption)[0]
                    print(is_valid)
                    if is_valid:
                        self.window.clear_screen()
                        self.window.connection_window.destroy()
                        bool = False
                    else:
                        self.window.reset_val(self.window.username_entry)
                        if self.window.error_message is None:
                            self.window.error_message = tkinter.Label(self.window.connection_window, text="L + Ratio + תפוס", font=('Calibri', 16))
                            self.window.error_message.pack(pady=20)
                        self.window.submitted = False

                else:
                    # log in
                    self.client_socket.send(self.protocol.create_msg("LOGIN", [username, password], self.cipher_for_encryption))
                    is_valid = self.protocol.get_msg(self.client_socket, self.cipher_for_decryption)[2]
                    if is_valid[0] == "True":
                        self.window.clear_screen()
                        self.window.connection_window.destroy()
                        bool = False
                    else:
                        self.window.reset_val(self.window.username_entry)
                        self.window.reset_val(self.window.password_entry)
                        if self.window.error_message is None:
                            self.window.error_message = tkinter.Label(self.window.connection_window, text="לא קיים / סיסמה לא נכונה", font=('Calibri', 16))
                            self.window.error_message.pack(pady=20)
                        self.window.submitted = False

        """while bool:
            sign_log = input("sign up or log in? ")
            if sign_log == "sign_up" or sign_log == "log_in":
                username = input("Enter username: ")
                password = input("Enter password: ")
                if sign_log == "sign_up":
                    age = input("Enter age: ")
                    print("entered details")
                    self.client_socket.send(self.protocol.create_msg("SIGNUP", [username, password, age]))
                    is_valid = self.protocol.get_msg(self.client_socket)[2]
                    if is_valid[0] == "True":
                        bool = False
                elif sign_log == "log_in":
                    self.client_socket.send(self.protocol.create_msg("LOGIN", [username, password]))
                    is_valid = self.protocol.get_msg(self.client_socket)[2]
                    if is_valid[0] == "True":
                        bool = False"""

        print("waiting for md5")
        md5 = self.protocol.get_msg(self.client_socket, self.cipher_for_decryption)[2] # should get give md5
        self.target_md5 = str(md5[0])
        print("got md5: " + str(self.target_md5))

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
        step = max(1, (self.range_end - self.range_start) // self.cpu_count)
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
                self.finish = True
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
        try:
            print("Starting search...")

            data = self.protocol.get_msg(self.client_socket, self.cipher_for_decryption)[2] # should get give range
            start_time = time.time()
            print(str(data))
            self.range_start = int(data[0])
            self.range_end = int(data[1])

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
        except ConnectionResetError:
            print("The server got what he wanted, now go away.")
            sys.exit()
        except KeyboardInterrupt:
            self.client_socket.send(self.protocol.create_msg("CRASH"))
            print("crashed")

    def send(self, found):
        if found == -1:
            msg = self.protocol.create_msg("CHECK", [self.protocol.NOT_FOUND, found], self.cipher_for_encryption)
        else:
            msg = self.protocol.create_msg("CHECK", [self.protocol.FOUND, found], self.cipher_for_encryption)
        self.client_socket.send(msg)


if __name__ == "__main__":
    client = Client()
    client.connect()
    del client.window
    while not client.finish:
        client.actual_run()
