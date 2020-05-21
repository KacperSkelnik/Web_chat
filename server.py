import socket
import threading
from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from database import Base,User,Messages
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Configure application
server = Flask(__name__)
server.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
server.debug = True

# Configure database
# server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_server.db'
# server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(server)
engine = create_engine('sqlite:///users_server.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(bind=engine)

    
    


HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

PORT = 5050
SERVER = "192.168.0.248"  # local IP
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
            elif msg == "reg":
                registration(conn)
            elif msg == "log":
                login(conn)

            print(f"[{addr}] {msg}")
            conn.send("Msg received".encode(FORMAT))

    conn.close()

def registration(conn):
    msg = []
    for i in range(2):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg.append(conn.recv(msg_length).decode(FORMAT))

    if session.query(Base.metadata.tables['users']).filter_by(username=msg[0]).first():
        conn.send("exists".encode(FORMAT))
    else:
        user = User(username=msg[0], password=msg[1])
        session.add(user)
        session.commit()
        conn.send("created".encode(FORMAT))


def login(conn):
    msg = []
    for i in range(2):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg.append(conn.recv(msg_length).decode(FORMAT))

    user_object = session.query(Base.metadata.tables['users']).filter_by(username=msg[0]).first()
    if user_object is None:
        conn.send("incorrect".encode(FORMAT))
    elif msg[1] != user_object.password:
        conn.send("incorrect".encode(FORMAT))
    else:
        conn.send("correct".encode(FORMAT))



if __name__ == '__main__':
    print("Server is starting")
    start()
    server.run(debug=True)
