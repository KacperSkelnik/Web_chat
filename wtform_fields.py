from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError

from database import *

def validate_login():
    raise ValidationError("Username or password is incorrect")


def validate_username():
    raise ValidationError("Username already exists.")

class RegistrationForm(FlaskForm):
    """ Registration form """
    username = StringField('username', validators=[InputRequired(message="Username required"), Length(min=2, max=25,
        message="Username must be between 2 and 25 characters")])
    password = PasswordField('password', validators=[InputRequired(message="Password required"), Length(min=2, max=25,
        message="Password must be between 2 and 25 characters")])
    confirm_pswd = PasswordField('confirm_pswd', validators=[InputRequired(message="Password required"),
        EqualTo('password', message="Passwords must match")])
    submit_btton = SubmitField("Create")


class LoginForm(FlaskForm):
    """ Login form """
    username = StringField('username', validators=[InputRequired(message="Username required")])
    password = PasswordField('password', validators=[InputRequired(message="Password required")])
    login_btton = SubmitField("Login")



class ChatForm(FlaskForm):
    """ Logout form """
    text = TextAreaField('message', render_kw={"rows": 3, "cols": 50})
    friend = SelectField('friend', coerce=int, validate_choice=False)