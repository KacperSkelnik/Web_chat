from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError

from database import *


def validate_login(form, field):
    password = field.data
    username = form.username.data

    user_object = User.query.filter_by(username=username).first()
    if user_object is None:
        raise ValidationError("Username or password is incorrect")
    elif password != user_object.password:
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
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists.")


class LoginForm(FlaskForm):
    """ Login form """
    username = StringField('username', validators=[InputRequired(message="Username required")])
    password = PasswordField('password', validators=[InputRequired(message="Password required"), validate_login])
    login_btton = SubmitField("Login")

class ChatForm(FlaskForm):
    """ Logout form """
    text = TextAreaField('Message', render_kw={"rows": 10, "cols": 50})
    logout_btton = SubmitField("Logout")