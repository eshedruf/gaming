import socket


class Protocol:
    def __init__(self):
        self.SEPERATOR = "\r\n"

    def sign_up(self, name, password, age):
        msg = name + self.SEPERATOR + password + self.SEPERATOR + age
        length = len(msg)
        return length, msg