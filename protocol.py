import socket


class Protocol:
    def __init__(self):
        self.SEPERATOR = "\r\n"
        self.CMDS = ["SIGNUP", "LOGIN", "STOP", "CHECK", "GIVE_RANGE"]
        self.LENGTH_FIELD_SIZE = 4

    def check_cmd(self, cmd):
        return cmd in self.CMDS

    def create_msg(self, cmd, msg_parts):
        if self.check_cmd(cmd):
            msg = cmd
            for part in msg_parts:
                msg += self.SEPERATOR + part
            return str(len(msg)) + msg
        else:
            raise FileExistsError

    def get_msg(self, socket_gaming):
        try:
            data = socket_gaming.recv(self.LENGTH_FIELD_SIZE).decode()
            length = int(data)
            data_str = socket_gaming.recv(length)
            while len(data_str) < length:
                data_str += socket_gaming.recv(length - len(data_str))
            return True, data_str.decode()
        except ValueError:
            return False, ""



