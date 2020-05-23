from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from app import Connection


def validate_login(form, field):
    password = field.data
    username = form.username.data

    Connection.send("log")
    Connection.send(username)
    Connection.send(password)
    a = Connection.recv()
    if a == "incorrect":
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
        Connection.send("user")
        Connection.send(username.data)
        if Connection.recv() == "exists":
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