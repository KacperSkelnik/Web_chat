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
DISCONNECT_MESSAGE = "!DISCONNECT"

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # local IP
ADDR = (SERVER, PORT) # Address

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket and pick type
server.bind(ADDR) # bind socket to address

clients = []

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
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                print("Client disconnected")
                clients.remove((conn, user[0]))
                conn.close()
                connected = False
            elif msg == "user":
                check_username(conn)
            elif msg == "reg":
                registration(conn)
            elif msg == "log":
                login(conn)
            elif msg == "chat":
                user = handle_chat(conn)
                clients.append((conn, user[0])) if (conn, user[0]) not in clients else clients
            elif msg == "friend":
                check_username(conn)
                add_friend(conn)
            else:
                new_message = Messages(username_to=user[1], username_from=user[0], message=msg, date=datetime.now())
                session.add(new_message)
                session.commit()
        print(msg)

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
        send(conn, "exists")
    else:
        send(conn, "ok")


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
    send(conn, "created")


def login(conn):
    msg = []
    for i in range(2):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg.append(conn.recv(msg_length).decode(FORMAT))

    user_object = session.query(Base.metadata.tables['users']).filter_by(username=msg[0]).first()
    if user_object is None:
        send(conn, "incorrect")
    elif msg[1] != user_object.password:
        send(conn, "incorrect")
    else:
        send(conn, '')
        send(conn, "correct")
        send(conn, "pickle")
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
    send(conn, "pickle")
    send_pickle(conn, friends)

    user_to_length = conn.recv(HEADER).decode(FORMAT)
    if user_to_length:
        user_to_length = int(user_to_length)
        user_to = conn.recv(user_to_length).decode(FORMAT)

    messages_from = [(msg.id, msg.username_from, msg.username_to, msg.message, msg.date) for msg in session.query(Messages) \
        .filter((Messages.username_to == user) & (Messages.username_from == user_to)) \
        .order_by(Messages.id.desc()).limit(6)]
    if messages_from:
        send(conn, "pickle")
        send_pickle(conn, messages_from)
    else:
        send(conn, "pickle")
        send_pickle(conn, [(0, user_to, user, "There is no any messages", datetime.now())])

    messages_to = [(msg.id, msg.username_from, msg.username_to, msg.message, msg.date) for msg in session.query(Messages) \
        .filter((Messages.username_to == user_to) & (Messages.username_from == user)) \
        .order_by(Messages.id.desc()).limit(6)]
    if messages_to:
        send(conn, "pickle")
        send_pickle(conn, messages_to)
    else:
        send(conn, "pickle")
        send_pickle(conn, [(0, user, user_to, "Nothing", datetime.now())])

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
    if not user_object:
        friends = Friends(username1=msg[0], username2=msg[1])
        session.add(friends)
        session.commit()
        send(conn, "")
        send(conn, "added")
    else:
        send(conn, "is_friend")


if __name__ == '__main__':
    print("Server is starting")
    start()
