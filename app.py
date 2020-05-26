from flask import Flask, render_template, redirect, url_for, request
from connection import Connection
from flask_sqlalchemy  import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import time
from subprocess import call
import os
import sys

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
READY = "72656164795f5f7265616479"

forbidden = [REGISTRATION, CREATED, LOGIN, CORRECT, CHAT, NOTHING, SEND, FRIENDS,
             ADDED, DISCONNECT, INCORRECT, USER, EXIST, OK, IS_FRIEND, READY]

Connection = Connection()
Connection.connect()

# Configure application
app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
app.debug = True

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_client.db' # Database name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from wtform_fields import *


# Create local data base to store info about login users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)


# Configure login decorator
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def writePidFile():
        pid = str(os.getpid())
        f = open('app.pid', 'w')
        f.write(pid)
        f.close()

writePidFile()


@app.route('/', methods=['POST', 'GET'])
def index():
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        password = registration_form.password.data

        Connection.send(REGISTRATION)
        Connection.send(username)
        Connection.send(password)

        if Connection.recv() == CREATED:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('index.html', form=registration_form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        if Connection.recv() == CORRECT:
            user = User.query.filter_by(username=login_form.username.data).first()
            if user:
                Connection.recv()
                login_user(user)
            else:
                data = Connection.recv()
                new_user = User(username=data[1], password=data[2])
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
            return redirect(url_for('chat'))

    return render_template("login.html", form=login_form)


Ready_to_update = False


@app.route('/get_messages')
def get_messages():
    global Ready_to_update
    try:
        messages = []
        if Ready_to_update:
            Connection.send(READY)
            messages_from = Connection.recv()
            messages_to = Connection.recv()
            messages = messages_from + messages_to
            messages.sort(key=lambda x: x[4])
        return render_template('messages.html', name=current_user.username, messages=messages)
    except:
        print("There was something issue with loading messages")
        Ready_to_update = False
        Connection.send(DISCONNECT)
        time.sleep(1)
        call("./restart.sh", shell=True)


@app.route('/chat', methods=['POST', 'GET'])
@login_required
def chat():
    global Ready_to_update

    try:
        Ready_to_update = False

        Connection.send(CHAT)
        Connection.send(current_user.username)

        chat_form = ChatForm()
        chat_form.friend.choices = Connection.recv()
        chat_form.friend.default = chat_form.friend.choices[0]

        user_to_send = dict(chat_form.friend.choices).get(chat_form.friend.data)

        if user_to_send:
            user_to_send = user_to_send.split()[1]
            Connection.send(user_to_send)
            messages_from = Connection.recv()
            messages_to = Connection.recv()
        else:
            Connection.send(" ")
            messages_from = Connection.recv()
            messages_to = Connection.recv()

        messages = messages_from + messages_to
        messages.sort(key=lambda x:x[4])

        if request.method == 'POST':
            if request.form['action'] == 'Send':
                message = chat_form.text.data
                if message != "" and message not in forbidden:
                    if user_to_send:
                        Connection.send(message)

                chat_form.text.data = ""

            if request.form['action'] == 'Add new friend':
                return redirect(url_for('friends'))

        Ready_to_update = True

        return render_template('chat.html', form=chat_form, name=current_user.username, messages=messages)
    except:
        print("There was something issue with chat")
        Ready_to_update = False
        Connection.send(DISCONNECT)
        time.sleep(1)
        call("./restart.sh", shell=True)


@app.route('/friends', methods=['POST', 'GET'])
@login_required
def friends():
    friends_form = FriendsForm()

    if friends_form.validate_on_submit():
        if Connection.recv() == ADDED:
            return redirect(url_for('chat'))

    return render_template("friends.html", form=friends_form)


@app.route('/logout', methods=['GET'])
def logout():
    Connection.send(DISCONNECT)
    return "You are log out"


if __name__ == '__main__':
    app.run(debug=True)