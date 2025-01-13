import socket
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import hashlib


class Protocol:
    def __init__(self):
        self.SEPERATOR = "\r"
        self.CMDS = ["SIGNUP", "LOGIN", "STOP", "CHECK", "CRYPT", "GIVE_RANGE", "GIVE_MD5"]
        self.LENGTH_FIELD_SIZE = 4
        self.FOUND = "FOUND"
        self.NOT_FOUND = "NOT_FOUND"
        self.KEY_LENGTH = 16

    def check_cmd(self, cmd):
        return cmd in self.CMDS

    def create_msg(self, cmd, msg_parts, aes_key=None):
        if self.check_cmd(cmd):
            msg = cmd
            for part in msg_parts:
                msg += self.SEPERATOR + str(part)
            raw_msg = msg.encode()
            if aes_key:
                encrypted_msg = self.decrypt_message(aes_key, raw_msg)
                length_field = str(len(encrypted_msg)).zfill(self.LENGTH_FIELD_SIZE).encode()
                return length_field + encrypted_msg
            else:
                length_field = str(len(raw_msg)).zfill(self.LENGTH_FIELD_SIZE).encode()
                return length_field + raw_msg
        else:
            raise FileExistsError

    def get_msg(self, sockett, cipher=None):
        try:
            length_field = sockett.recv(self.LENGTH_FIELD_SIZE)
            if not length_field:
                return False, "", ""
            length = int(length_field.decode())
            encrypted_data = sockett.recv(length)
            while len(encrypted_data) < length:
                encrypted_data += sockett.recv(length - len(encrypted_data))

            if cipher:
                decrypted_data = self.decrypt_message(encrypted_data, cipher)
                msg = decrypted_data.decode()
            else:
                msg = encrypted_data.decode()

            command = msg.split(self.SEPERATOR)[0]
            lst = msg.split(self.SEPERATOR)[1::]
            if command == self.CMDS[4]:
                lst[0] = lst[0][2:len(lst[0]) - 1].encode().replace(b'\\n', b'\n')
            return True, command, lst

        except ValueError:
            return False, "", ""
        except UnicodeDecodeError:
            return False, "", ""

    def pad(self, s):
        padding_length = 16 - len(s) % 16
        padding = chr(padding_length) * padding_length
        return s + padding

    def unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]

    def get_aes_cipher(self, key):
        key = hashlib.sha256(key).digest()  # Making the key 32 bytes long
        return AES.new(key, AES.MODE_CBC, iv=key[:16])  # Using the first 16 bytes of the key as IV

    def encrypt_message(self, message, cipher):
        return cipher.encrypt(self.pad(message).encode())

    def decrypt_message(self, message, cipher):
        return self.unpad(cipher.decrypt(message))

    # RSA functions
    def generate_rsa_keys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key

    def get_rsa_cipher(self, public_key):
        rsa_key = RSA.import_key(public_key)
        return PKCS1_OAEP.new(rsa_key)

    def rsa_encrypt_message(self, message, rsa_cipher):
        return rsa_cipher.encrypt(message)

    def rsa_decrypt_message(self, encrypted_message, private_key):
        rsa_key = RSA.import_key(private_key)
        rsa_cipher = PKCS1_OAEP.new(rsa_key)
        return rsa_cipher.decrypt(encrypted_message)
