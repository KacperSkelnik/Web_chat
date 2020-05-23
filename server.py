import socket
import threading
import pickle
from database import Base,User,Messages
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

# Configure database
engine = create_engine('sqlite:///users_server.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(bind=engine)

HEADER = 10
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

PORT = 5050
SERVER = "192.168.0.18"  # local IP
ADDR = (SERVER, PORT) # Address

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket and pick type
server.bind(ADDR) # bind socket to address


def start():
    server.listen()
    print(f"Server is listening on {SERVER}")
    #threads = []
    while True:
        conn, addr = server.accept()
        #threads.append(threading.Thread(target=handle_client, args=(conn, addr)).start())
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print("Active connectors: ", threading.active_count() - 1)


def handle_client(conn, addr):
    print(f"New connection : {addr}")
    user = None
    connected = True
    chat = False
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                print("Client disconnected")
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
                chat = True
            else:
                print(f"[{addr}] {user[0]} send {msg} to {user[1]}")
                new_message = Messages(username_to=user[1], username_from=user[0], message=msg)
                session.add(new_message)
                session.commit()

        #if user is not None:
        #    while chat:
        #        #print('lalal')
        #        #send(conn, "lalalal")
        #        time.sleep(5)


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

    friends = [("0", "---")] + [(friend.id, friend.username) for friend in session.query(User).all()]
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
        send_pickle(conn, [(0, user_to, user, "There is no any messages", date.today())])

    messages_to = [(msg.id, msg.username_from, msg.username_to, msg.message, msg.date) for msg in session.query(Messages) \
        .filter((Messages.username_to == user_to) & (Messages.username_from == user)) \
        .order_by(Messages.id.desc()).limit(6)]
    if messages_to:
        send(conn, "pickle")
        send_pickle(conn, messages_to)
    else:
        send(conn, "pickle")
        send_pickle(conn, [(0, user_to, user, "Nothing", date.today())])

    return user, user_to


if __name__ == '__main__':
    print("Server is starting")
    start()
