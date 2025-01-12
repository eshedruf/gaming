import socket
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding as sym_padding
import os
import base64

class Protocol:
    def __init__(self):
        self.SEPERATOR = "\r"
        self.CMDS = ["SIGNUP", "LOGIN", "STOP", "CHECK", "CRYPT", "GIVE_RANGE", "GIVE_MD5"]
        self.LENGTH_FIELD_SIZE = 4
        self.FOUND = "FOUND"
        self.NOT_FOUND = "NOT_FOUND"

    def check_cmd(self, cmd):
        return cmd in self.CMDS

    def create_msg(self, cmd, msg_parts, aes_key=None):
        """
        Creates a message to send. If aes_key is provided, it encrypts the message using AES.
        """
        if self.check_cmd(cmd):
            msg = cmd
            for part in msg_parts:
                msg += self.SEPERATOR + str(part)
            #raw_msg = (str(len(msg)).zfill(self.LENGTH_FIELD_SIZE) + msg).encode()
            raw_msg = msg.encode()

            if aes_key:
                # Encrypt the message if AES key is provided
                encrypted_msg = self.aes_encrypt(aes_key, raw_msg)
                length_field = str(len(encrypted_msg)).zfill(self.LENGTH_FIELD_SIZE).encode()
                return length_field + encrypted_msg
            else:
                # Plaintext communication
                return raw_msg
        else:
            raise FileExistsError


    def get_msg(self, socket_gaming, aes_key=None):
        """
        Receives a message from the socket. If aes_key is provided, it decrypts the message using AES.
        """
        try:
            # Receive the fixed-length header indicating the encrypted message size
            length_field = socket_gaming.recv(self.LENGTH_FIELD_SIZE)
            if not length_field:
                return False, "", ""
            
            length = int(length_field.decode())

            # Receive the encrypted message of the specified length
            encrypted_data = socket_gaming.recv(length)
            while len(encrypted_data) < length:
                encrypted_data += socket_gaming.recv(length - len(encrypted_data))

            if aes_key:
                # Decrypt the message if AES key is provided
                decrypted_data = self.aes_decrypt(aes_key, encrypted_data)
                msg = decrypted_data.decode()
            else:
                # If no encryption, assume data is plaintext
                msg = encrypted_data.decode()

            # Parse the command and message parts
            command = msg.split(self.SEPERATOR)[0]
            lst = msg.split(self.SEPERATOR)[1::]
            return True, command, lst

        except (ValueError, UnicodeDecodeError):
            return False, "", ""


    # RSA functions
    def generate_rsa_keys(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        return private_key, public_key

    def rsa_encrypt(self, public_key, message):
        return public_key.encrypt(
            message,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

    def rsa_decrypt(self, private_key, ciphertext):
        return private_key.decrypt(
            ciphertext,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

    def serialize_public_key(self, public_key):
        return public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

    def load_public_key(self, pem_key):
        return serialization.load_pem_public_key(pem_key)

    # AES functions
    def generate_aes_key(self):
        return os.urandom(32)

    def aes_encrypt(self, key, plaintext):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ciphertext

    def aes_decrypt(self, key, ciphertext):
        iv = ciphertext[:16]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext[16:]) + decryptor.finalize()
        unpadder = sym_padding.PKCS7(128).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()
