from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import time

Base = declarative_base()


class User(UserMixin, Base):
    """ User database """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=False, nullable=False)
    password = Column(String(), nullable=False)


class Messages(Base):
    """ Messages database"""

    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    username_from = Column(String(25), unique=False, nullable=False)
    username_to = Column(String(25), unique=False, nullable=False)
    message = Column(String(250), unique=False, nullable=False)
    date = Column(DateTime)


class Friends(UserMixin, Base):
    """ Friends database """

    __tablename__ = "friends"
    id = Column(Integer, primary_key=True)
    username1 = Column(String(25), unique=False, nullable=False)
    username2 = Column(String(25), unique=False, nullable=False)
