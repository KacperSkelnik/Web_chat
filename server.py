import socket
import threading
import pickle
from database import Base, User, Messages, Friends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configure database
engine = create_engine('sqlite:///users_server.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(bind=engine)

HEADER = 10
FORMAT = 'utf-8'

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # local IP
ADDR = (SERVER, PORT) # Address

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket and pick type
server.bind(ADDR)

clients = []

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
READY = "72656164795f5f7265616479"


def start():
    server.listen()
    print(f"Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print("Active connectors: ", threading.active_count() - 1)

    for a, b in clients:
        if a == conn:
            clients.remove((a, b))


def handle_client(conn, addr):
    print(f"New connection : {addr}")
    user = None
    connected = True
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT:
                    print("Client disconnected")
                    clients.remove((conn, user[0]))
                    conn.close()
                    connected = False
                elif msg == USER:
                    check_username(conn)
                elif msg == REGISTRATION:
                    registration(conn)
                elif msg == LOGIN:
                    login(conn)
                elif msg == CHAT:
                    user = handle_chat(conn)
                    clients.append((conn, user[0])) if (conn, user[0]) not in clients else clients
                elif msg == FRIENDS:
                    add_friend(conn)
                elif msg == READY:
                    if user:
                        message_handel(conn, user[1], user[0])
                else:
                    new_message = Messages(username_to=user[1], username_from=user[0], message=msg, date=datetime.now())
                    session.add(new_message)
                    session.commit()
        except Exception:
            pass


def send(conn, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)


def send_pickle(conn, obj):
    message = pickle.dumps(obj)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)


def check_username(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)

    user_object = session.query(Base.metadata.tables['users']).filter_by(username=msg).first()
    if user_object:
        send(conn, EXIST)
    else:
        send(conn, OK)


def registration(conn):
    msg = []
    for i in range(2):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg.append(conn.recv(msg_length).decode(FORMAT))

    user = User(username=msg[0], password=msg[1])
    session.add(user)
    session.commit()
    send(conn, CREATED)


def login(conn):
    msg = []
    for i in range(2):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg.append(conn.recv(msg_length).decode(FORMAT))

    user_object = session.query(Base.metadata.tables['users']).filter_by(username=msg[0]).first()
    if user_object is None:
        send(conn, INCORRECT)
    elif msg[1] != user_object.password:
        send(conn, INCORRECT)
    else:
        send(conn, NOTHING)
        send(conn, CORRECT)
        send(conn, PICKLE)
        send_pickle(conn, session.query(Base.metadata.tables['users']).filter_by(username=msg[0]).first())


def handle_chat(conn):
    user_length = conn.recv(HEADER).decode(FORMAT)
    if user_length:
        user_length = int(user_length)
        user = conn.recv(user_length).decode(FORMAT)

    friends = [("0", "---")]
    for friend in session.query(Friends).filter(Friends.username1 == user):
        if friend.username2 in [x[1] for x in clients]:
            friends += [(friend.id, "online "+friend.username2)]
        else:
            friends += [(friend.id, "offline "+friend.username2)]
    send(conn, PICKLE)
    send_pickle(conn, friends)

    user_to_length = conn.recv(HEADER).decode(FORMAT)
    if user_to_length:
        user_to_length = int(user_to_length)
        user_to = conn.recv(user_to_length).decode(FORMAT)

    return message_handel(conn, user_to, user)


def message_handel(conn, user_to, user):
    messages_from = [(msg.id, msg.username_from, msg.username_to, msg.message, msg.date) for msg in
                     session.query(Messages) \
                         .filter((Messages.username_to == user) & (Messages.username_from == user_to)) \
                         .order_by(Messages.id.desc()).limit(6)]
    if messages_from:
        send(conn, PICKLE)
        send_pickle(conn, messages_from)
    else:
        messages_from = [(0, user_to, user, "There is no any messages", datetime.now())]
        send(conn, PICKLE)
        send_pickle(conn, messages_from)

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

    return user, user_to, messages_from, messages_to


def add_friend(conn):
    msg = []
    for i in range(2):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg.append(conn.recv(msg_length).decode(FORMAT))

    user_object = session.query(Friends).filter((Friends.username1 == msg[0]) & (Friends.username2 == msg[1])) \
        .order_by(Friends.id.desc()).first()
    if not user_object and msg[0] != msg[1]:
        friends = Friends(username1=msg[0], username2=msg[1])
        session.add(friends)
        session.commit()
        send(conn, NOTHING)
        send(conn, ADDED)
    else:
        send(conn, IS_FRIEND)


if __name__ == '__main__':
    print("Server is starting")
    start()
