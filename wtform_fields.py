from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError

from database import *
from app import db


def validate_login(form, field):
    password = field.data
    username = form.username.data

    user_object = db.session.query(User).filter_by(username=username).first()
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
        user_object = db.session.query(User).filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists.")


class LoginForm(FlaskForm):
    """ Login form """
    username = StringField('username', validators=[InputRequired(message="Username required")])
    password = PasswordField('password', validators=[InputRequired(message="Password required"), validate_login])
    login_btton = SubmitField("Login")

class ChatForm(FlaskForm):
    """ Logout form """
    #friends = [(friend.id, friend.username) for friend in db.session.query(User).all()]

    text = TextAreaField('message', render_kw={"rows": 3, "cols": 50})
    send_btton = SubmitField("Send")
    friend = SelectField('friend', coerce=int, validate_choice=False)