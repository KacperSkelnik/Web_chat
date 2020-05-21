from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from flask_sqlalchemy import SQLAlchemy
from connection import Connection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DISCONNECT_MESSAGE = "!DISCONNECT"
Connection = Connection()
Connection.connect()
Connection.send("hello")

# Configure application
app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
app.debug = True

# Configure database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
engine = create_engine('sqlite:///users_server.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

@app.before_first_request
def setup():
    #Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


from wtform_fields import *


# Configure flask_login
login = LoginManager()
login.init_app(app)


@login.user_loader
def load_user(id):
    return session.query(User).get(int(id))


@app.route('/', methods=['POST', 'GET'])
def index():
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        password = registration_form.password.data

        Connection.send("reg")
        Connection.send(username)
        Connection.send(password)

        if Connection.recv() == "exists":
            validate_username()
        elif Connection.recv() == "created":
            return redirect(url_for('login'))

    return render_template('index.html', form=registration_form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data

        Connection.send("log")
        Connection.send(username)
        Connection.send(password)

        if Connection.recv() == "incorrect":
            validate_login()
        elif Connection.recv() == "correct":
            login_user(username)
            return redirect(url_for('chat'))

        #user_object = session.query(User).filter_by(username=login_form.username.data).first()

    return render_template("login.html", form=login_form)


@app.route('/chat', methods=['POST', 'GET'])
@login_required
def chat():
    chat_form = ChatForm()
    chat_form.friend.choices = [(friend.id, friend.username) for friend in session.query(User).all()]
    user_to_send = dict(chat_form.friend.choices).get(chat_form.friend.data)

    messages_from = session.query(Messages)\
        .filter((Messages.username_to == current_user.username) & (Messages.username_from == user_to_send))\
        .order_by(Messages.id.desc()).limit(6)

    messages_to = session.query(Messages)\
        .filter((Messages.username_to == user_to_send) & (Messages.username_from == current_user.username))\
        .order_by(Messages.id.desc()).limit(6)

    if chat_form.validate_on_submit():
        if request.form['action'] == 'Send':
            message = chat_form.text.data
            user_to_send = dict(chat_form.friend.choices).get(chat_form.friend.data)

            new_message = Messages(username_to=user_to_send, username_from=current_user.username,message=message)
            session.add(new_message)
            session.commit()

            chat_form.text.data = ""
        if request.form['action'] == 'Select':
            return render_template('chat.html', form=chat_form, messages_to=messages_to,
                                   messages_from=messages_from, name=current_user.username)

    #print(chat_form.errors)

    return render_template('chat.html', form=chat_form, messages_to=messages_to,
                           messages_from=messages_from, name=current_user.username)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    Connection.send(DISCONNECT_MESSAGE)
    return "You are log out"


if __name__ == '__main__':
    app.run(debug=True)