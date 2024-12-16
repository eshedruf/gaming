import socket


class Protocol:
    def __init__(self):
        self.SEPERATOR = "\r\n"
        self.CMDS = ["SIGNUP", "LOGIN", "STOP", "CHECK", "GIVE_RANGE", "GIVE_MD5"]
        self.LENGTH_FIELD_SIZE = 4
        self.FOUND = "FOUND"
        self.NOT_FOUND = "NOT_FOUND"

    def check_cmd(self, cmd):
        return cmd in self.CMDS

    def create_msg(self, cmd, msg_parts):
        if self.check_cmd(cmd):
            msg = cmd
            for part in msg_parts:
                msg += self.SEPERATOR + str(part)
            return str(len(msg)) + msg
        else:
            raise FileExistsError

    def get_msg(self, socket_gaming):
        try:
            length = int(socket_gaming.recv(self.LENGTH_FIELD_SIZE).decode())
            data_str = socket_gaming.recv(length)
            while len(data_str) < length:
                data_str += socket_gaming.recv(length - len(data_str))
            msg = data_str.decode()
            command = msg.split(self.SEPERATOR)[0]
            lst = [part for part in msg[len(command):len(msg)].split(self.SEPERATOR)][::2]
            return True, command, lst
        except ValueError:
            return False, "", ""

