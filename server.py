import socket
import threading
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from database import Base

# Configure application
server = Flask(__name__)
server.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
server.debug = True

# Configure database
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_server.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)


@server.before_first_request
def setup():
    # Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)


HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

PORT = 5050
SERVER = "192.168.0.18"  # local IP
ADDR = (SERVER, PORT) # Address

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket and pick type
server.bind(ADDR) # bind socket to address


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

            print(f"[{addr}] {msg}")
            conn.send("Msg received".encode(FORMAT))

    conn.close()


def start():
    server.listen()
    print(f"Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print("Active connectors: ", threading.active_count() - 1)



if __name__ == '__main__':
    print("Server is starting")
    start()
    server.run(debug=True)
