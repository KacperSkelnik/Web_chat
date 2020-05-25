import socket
import sys
import pickle

REGISTRATION = "!726567697374726174696f6e" # !HEX
CREATED = "!63726561746564"
LOGIN = "!6c6f67696e"
CORRECT = "!636f7272656374"
CHAT = "!636861745f746f"
NOTHING = "!6e6f7468696e67"
SEND = "!53656e6453656e64"
FRIENDS = "!667269656e6473"
ADDED = "!6164646564206164646564"
DISCONNECT = "!444953434f4e4e454354"
INCORRECT = "!696e636f7272656374"
USER = "!555345525f5f5f55534552"
EXIST = "!45584953545f5f4558495354"
OK = "!4f4b5f4f4ba"
IS_FRIEND = "!69735f667269656e64"
PICKLE = "!5049434b4c455f5f76617364"

class Connection(object):
    HEADER = 10
    FORMAT = 'utf-8'
    DISCONNECT_MSG = "!DISC"

    PORT = 5050
    SERVER = socket.gethostbyname(socket.gethostname()) # local IP
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
        try:
            message = msg.encode(self.FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(self.FORMAT)
            send_length += b' ' * (self.HEADER - len(send_length))
            self.client.send(send_length)
            self.client.send(message)
            if msg != DISCONNECT:
                socket.close()
        except Exception:
            pass

    def recv(self):
        try:
            msg_length = self.client.recv(self.HEADER).decode(self.FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = self.client.recv(msg_length).decode(self.FORMAT)
                if msg == PICKLE:
                    msg_length = self.client.recv(self.HEADER).decode(self.FORMAT)
                    if msg_length:
                        msg_length = int(msg_length)
                        msg = self.client.recv(msg_length)
                        msg = pickle.loads(msg)
                    return msg
            return msg
        except Exception:
            pass
