#Kacper Skelnik 291566
#Wojciech Tyczyński 291563
import socket
import threading
import pickle
from database import Base, User, Messages, Friends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import netifaces as ni

# Configure database
engine = create_engine('sqlite:///users_server.db', connect_args={"check_same_thread": False}, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(bind=engine)

HEADER = 10                                             # keep length of message
FORMAT = 'utf-8'                                        # set format

ni.ifaddresses('wlo1')
ip = ni.ifaddresses('wlo1')[ni.AF_INET][0]['addr']      # get true ip
PORT = 5050                                             # set port
SERVER = ip#socket.gethostbyname(socket.getfqdn())      # local ip
ADDR = (SERVER, PORT)                                   # address

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket and pick type
server.bind(ADDR)                                           # bind address to server

clients = []

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
READY = "72656164795f5f7265616479"


def start():
    print(f"Server is listening on {SERVER}")
    thread = [None]*10                  # declaration thread array
    for i in range(10):                 # for max number of client (can be increase if need to)
        server.listen()                 # server listen for clients
        conn, addr = server.accept()    # create socket and address variable
        thread[i] = threading.Thread(target=handle_client, args=(conn, addr))   # thread initialization
        thread[i].start()               # start thread
        print("Active connectors: ", threading.active_count() - 1)


def handle_client(conn, addr):
    print(f"New connection : {addr}")
    user = None                         # user variable
    connected = True                    # tell if connected
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)       # receive message length from client
        if msg_length:
            msg_length = int(msg_length)                    # take message length
            msg = conn.recv(msg_length).decode(FORMAT)      # receive message
            if msg == DISCONNECT:                           # if message is DISCONNECT
                print("Client disconnected")
                clients.remove((conn, user[0]))             # remove user from clients array with handle online users
                conn.close()                                # close communication with client
                connected = False                           # stop loop
            elif msg == USER:                               # if message is USER
                check_username(conn)                        # check_username()
            elif msg == REGISTRATION:                       # if message is REGISTRATION
                registration(conn)                          # registration()
            elif msg == LOGIN:                              # if message is LOGIN
                login(conn)                                 # login()
            elif msg == CHAT:                               # if message is CHAT
                user = handle_chat(conn)                    # take user object from handle_chat()
                clients.append((conn, user[0])) if (conn, user[0]) not in clients else clients  # add user to online users if is not in client already
            elif msg == FRIENDS:                            # if message is FRIENDS
                add_friend(conn)                            # add_friend()
            elif msg == READY:                              # if message is READY
                if user:
                    message_handel(conn, user[1], user[0])  # message_handel()
            else:
                new_message = Messages(username_to=user[1], username_from=user[0], message=msg, date=datetime.now())
                session.add(new_message)    # add new message to database
                session.commit()            # commit new message


def send(conn, msg):
    message = msg.encode(FORMAT)                        # code message to utf-8
    msg_length = len(message)                           # take message length
    send_length = str(msg_length).encode(FORMAT)        # create encode message length
    send_length += b' ' * (HEADER - len(send_length))   # add empty bytes
    conn.send(send_length)                              # send message length
    conn.send(message)                                  # send message


def send_pickle(conn, obj):
    message = pickle.dumps(obj)                         # pickling data
    msg_length = len(message)                           # take message length
    send_length = str(msg_length).encode(FORMAT)        # create encode message length
    send_length += b' ' * (HEADER - len(send_length))   # add empty bytes
    conn.send(send_length)                              # send message length
    conn.send(message)                                  # send message


def check_username(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)       # receive message length from client
    if msg_length:
        msg_length = int(msg_length)                    # take message length
        msg = conn.recv(msg_length).decode(FORMAT)      # receive message

    user_object = session.query(Base.metadata.tables['users']).filter_by(username=msg).first()  # try to query user
    if user_object:
        send(conn, EXIST)                               # send EXIST
    else:
        send(conn, OK)                                  # send OK


def registration(conn):
    msg = []                                            # create message array
    for i in range(2):
        msg_length = conn.recv(HEADER).decode(FORMAT)   # as above
        if msg_length:
            msg_length = int(msg_length)
            msg.append(conn.recv(msg_length).decode(FORMAT))

    user = User(username=msg[0], password=msg[1])       # create user object base on messages data
    session.add(user)                                   # add user to database
    session.commit()                                    # commit changes
    send(conn, CREATED)                                 # send CREATED to client


def login(conn):
    msg = []                                            # as above
    for i in range(2):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg.append(conn.recv(msg_length).decode(FORMAT))

    user_object = session.query(Base.metadata.tables['users']).filter_by(username=msg[0]).first()   # try to query user
    if user_object is None:
        send(conn, INCORRECT)                           # send INCORRECT if dont exist
    elif msg[1] != user_object.password:
        send(conn, INCORRECT)                           # send INCORRECT if username and password dont mach
    else:
        send(conn, NOTHING)                             # send nothing
        send(conn, CORRECT)                             # send CORRECT
        send(conn, PICKLE)                              # send pickle
        send_pickle(conn, session.query(Base.metadata.tables['users']).filter_by(username=msg[0]).first())  # send user object


def handle_chat(conn):
    user_length = conn.recv(HEADER).decode(FORMAT)      # as above
    if user_length:
        user_length = int(user_length)
        user = conn.recv(user_length).decode(FORMAT)

    friends = [("0", "---")]                            # declaration friends array
    for friend in session.query(Friends).filter(Friends.username1 == user):     # query all friend of user
        if friend.username2 in [x[1] for x in clients]:                         # if user friend is in clients (online)
            friends += [(friend.id, "online "+friend.username2)]
        else:
            friends += [(friend.id, "offline "+friend.username2)]
    send(conn, PICKLE)                                  # send PICKLE
    send_pickle(conn, friends)                          # send friends array

    user_to_length = conn.recv(HEADER).decode(FORMAT)   # as above
    if user_to_length:
        user_to_length = int(user_to_length)
        user_to = conn.recv(user_to_length).decode(FORMAT)

    return message_handel(conn, user_to, user)          # message_handel()


def message_handel(conn, user_to, user):
    # query all message to user
    messages_from = [(msg.id, msg.username_from, msg.username_to, msg.message, msg.date) for msg in
                     session.query(Messages) \
                         .filter((Messages.username_to == user) & (Messages.username_from == user_to)) \
                         .order_by(Messages.id.desc()).limit(6)]
    if messages_from:                                   # if there are some
        send(conn, PICKLE)                              # send PICKLE
        send_pickle(conn, messages_from)                # send all message to user as pickle
    else:                                               # if there is none
        messages_from = [(0, user_to, user, "There is no any messages", datetime.now())]
        send(conn, PICKLE)
        send_pickle(conn, messages_from)                # always the same

    # query all message from user and as above
    messages_to = [(msg.id, msg.username_from, msg.username_to, msg.message, msg.date) for msg in
                   session.query(Messages) \
                       .filter((Messages.username_to == user_to) & (Messages.username_from == user)) \
                       .order_by(Messages.id.desc()).limit(6)]
    if messages_to:
        send(conn, PICKLE)
        send_pickle(conn, messages_to)
    else:
        messages_to = [(0, user, user_to, "Nothing", datetime.now())]
        send(conn, PICKLE)
        send_pickle(conn, messages_to)

    # return all information to message_handel() or case if message from client is READY
    return user, user_to, messages_from, messages_to


def add_friend(conn):
    msg = []                                            # as above
    for i in range(2):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg.append(conn.recv(msg_length).decode(FORMAT))

    user_object = session.query(Friends).filter((Friends.username1 == msg[0]) & (Friends.username2 == msg[1])) \
        .order_by(Friends.id.desc()).first()            # query all friends
    if not user_object and msg[0] != msg[1]:            # if request is for user that is not friend, and for user self
        friends = Friends(username1=msg[0], username2=msg[1])   # add friend to database
        session.add(friends)
        session.commit()
        send(conn, NOTHING)
        send(conn, ADDED)
    else:
        send(conn, IS_FRIEND)


if __name__ == '__main__':
    print("Server is starting")
    start()  # run server
