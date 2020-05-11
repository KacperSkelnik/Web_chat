from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy

from database import Base, User, Messages

# Configure application
app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
app.debug = True

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.before_first_request
def setup():
    #Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)


from wtform_fields import *


# Configure flask_login
login = LoginManager()
login.init_app(app)


@login.user_loader
def load_user(id):
    return db.session.query(User).get(int(id))


@app.route('/', methods=['POST', 'GET'])
def index():
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        password = registration_form.password.data

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('index.html', form=registration_form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_object = db.session.query(User).filter_by(username=login_form.username.data).first()
        login_user(user_object)
        return redirect(url_for('chat'))

    return render_template("login.html", form=login_form)


@app.route('/chat', methods=['POST', 'GET'])
@login_required
def chat():
    chat_form = ChatForm()
    messages_from = db.session.query(Messages).filter_by(username=current_user.username).order_by(Messages.id.desc()).limit(6)
    #messages_to = db.session.query(Messages).filter_by(username=current_user.username).order_by(Messages.id.desc()).limit(6)

    if chat_form.validate_on_submit():
        message = chat_form.text.data
        user_to_send = chat_form.user_to_send.data

        new_message = Messages(username=user_to_send, message=message)
        db.session.add(new_message)
        db.session.commit()

        chat_form.text.data = ""

    return render_template('chat.html', form=chat_form, messages=messages_from)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return "You are log out"


if __name__ == '__main__':
    app.run(debug=True)
