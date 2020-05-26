import socket
import sys
import pickle

REGISTRATION = "!726567697374726174696f6e" # !HEX use to something like handshake
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
    HEADER = 10                         # keep length of message
    FORMAT = 'utf-8'                    # set format

    PORT = 5050                         # set port
    SERVER = socket.gethostbyname(socket.gethostname()) # local IP have to be change to server ip
    ADDR = (SERVER, PORT)               # address

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # try to create socket
    except socket.error as e:
        print("Failed To Create A Scoket")
        print("Reason : ", str(e))
        sys.exit()                                                      # exit
    print("Socket Created Successfully")

    def connect(self):
        try:
            self.client.connect(self.ADDR)                              # try to connect to server
            print("Socket connected to host ", self.SERVER + " on port ", self.PORT)
        except socket.error as e:
            print("Failed connection to host ", self.SERVER, " on port ", self.PORT)
            print("Reason", str(e))
            sys.exit()                                                  # exit

    def send(self, msg):
        message = msg.encode(self.FORMAT)                               # code message to utf-8
        msg_length = len(message)                                       # take message length
        send_length = str(msg_length).encode(self.FORMAT)               # create encode message length
        send_length += b' ' * (self.HEADER - len(send_length))          # add empty bytes
        self.client.send(send_length)                                   # send message length
        self.client.send(message)                                       # send message

    def recv(self):
        msg_length = self.client.recv(self.HEADER).decode(self.FORMAT)  # receive HEADER bytes
        if msg_length:
            msg_length = int(msg_length)                                # take messages length
            msg = self.client.recv(msg_length).decode(self.FORMAT)  # receive and decode message of length as msg_length
            if msg == PICKLE:                                       # if server send you PICKLE
                msg_length = self.client.recv(self.HEADER).decode(self.FORMAT)  # repeat sequence
                if msg_length:
                    msg_length = int(msg_length)
                    msg = self.client.recv(msg_length)              # receive pickled data
                    msg = pickle.loads(msg)                         # unpickle data
                return msg
            return msg
