import socket
import sys


class Connection(object):
    HEADER = 64
    FORMAT = 'utf-8'
    DISCONNECT_MSG = "!DISC"

    PORT = 5050
    SERVER = "192.168.0.18"  # local IP
    ADDR = (SERVER, PORT)  # Address

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("Failed To Create A Scoket")
        print("Reason : ", str(e))
        sys.exit()
    print("Socket Created Successfully")

    def connect(self):
        try:
            self.client.connect(self.ADDR)
            print("Socket connected to host ", self.SERVER + " on port ", self.PORT)
        except socket.error as e:
            print("Failed connection to host ", self.SERVER, " on port ", self.PORT)
            print("Reason", str(e))
            sys.exit()

    def send(self, msg):
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
        print(self.client.recv(2048).decode(self.FORMAT))
