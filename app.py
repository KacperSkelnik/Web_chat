from flask import Flask, render_template, redirect, url_for, request
from connection import Connection
from flask_sqlalchemy  import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

DISCONNECT_MESSAGE = "!DISCONNECT"
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_client.db'
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


@app.route('/', methods=['POST', 'GET'])
def index():
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        password = registration_form.password.data

        Connection.send("reg")
        Connection.send(username)
        Connection.send(password)

        if Connection.recv() == "created":
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('index.html', form=registration_form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        if Connection.recv() == "correct":
            user = User.query.filter_by(username=login_form.username.data).first()
            if user:
                login_user(user)
            else:
                data = Connection.recv()
                new_user = User(username=data[1], password=data[2])
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
            return redirect(url_for('chat'))

    return render_template("login.html", form=login_form)


@app.route('/chat', methods=['POST', 'GET'])
@login_required
def chat():
    print("kakak")
    """
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
"""


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    Connection.send(DISCONNECT_MESSAGE)
    return "You are log out"


if __name__ == '__main__':
    app.run(debug=True)