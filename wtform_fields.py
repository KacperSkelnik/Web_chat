from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from app import Connection
from flask_login import current_user

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


def validate_login(form, field):
    password = field.data
    username = form.username.data

    Connection.send(LOGIN)
    Connection.send(username)
    Connection.send(password)
    a = Connection.recv()
    if a == INCORRECT:
        raise ValidationError("Username or password is incorrect")


class RegistrationForm(FlaskForm):
    """ Registration form """
    username = StringField('username', validators=[InputRequired(message="Username required"), Length(min=2, max=25,
        message="Username must be between 2 and 25 characters")])
    password = PasswordField('password', validators=[InputRequired(message="Password required"), Length(min=2, max=25,
        message="Password must be between 2 and 25 characters")])
    confirm_pswd = PasswordField('confirm_pswd', validators=[InputRequired(message="Password required"),
        EqualTo('password', message="Passwords must match")])
    submit_btton = SubmitField("Create")

    def validate_username(self, username):
        Connection.send(USER)
        Connection.send(username.data)
        if Connection.recv() == EXIST:
            raise ValidationError("Username already exists. Select a different username.")


class LoginForm(FlaskForm):
    """ Login form """
    username = StringField('username', validators=[InputRequired(message="Username required")])
    password = PasswordField('password', validators=[InputRequired(message="Password required"), validate_login])
    login_btton = SubmitField("Login")


class ChatForm(FlaskForm):
    """ Chat form """
    text = TextAreaField('message', render_kw={"rows": 3, "cols": 50})
    friend = SelectField(u'friend', coerce=int, validate_choice=False)


class FriendsForm(FlaskForm):
    """ Friend form """
    username = StringField('username', validators=[InputRequired(message="Username required")])
    submit_btton = SubmitField("invite")

    def validate_username(self, username):
        Connection.send(FRIENDS)
        Connection.send(username.data)
        if Connection.recv() == OK:
            raise ValidationError("Username dont exists. Try with different username.")
        else:
            pass

        Connection.send(current_user.username)
        Connection.send(username.data)

        if Connection.recv() == IS_FRIEND:
            raise ValidationError("User is already your friend")
        else:
            pass