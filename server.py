import socket
import threading
import pickle
from database import Base,User,Messages
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure database
engine = create_engine('sqlite:///users_server.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(bind=engine)

HEADER = 64
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
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print("Active connectors: ", threading.active_count() - 1)


def handle_client(conn, addr):
    print(f"New connection : {addr}")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                print("Client disconnected")
                connected = False
            elif msg == "user":
                check_username(conn)
            elif msg == "reg":
                registration(conn)
            elif msg == "log":
                login(conn)
            else:
                handle_chat(conn)

            print(f"[{addr}] {msg}")
            #conn.send("Msg received".encode(FORMAT))

    conn.close()


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
    return 0


if __name__ == '__main__':
    print("Server is starting")
    start()
