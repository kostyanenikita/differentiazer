# -*- coding: utf-8 -*-
from __future__ import absolute_import

from sqlalchemy import Column, Integer, Text, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from functools import wraps

Base = declarative_base(create_engine('sqlite:///db'))

Session = sessionmaker()
session = Session()


@contextmanager
def db_transaction(session):
    try:
        yield
    except:
        session.rollback()
        raise
    else:
        session.commit()


def in_db_transaction(session):
    def outer_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with db_transaction(session):
                return func(*args, **kwargs)
        return wrapper
    return outer_wrapper


class User(Base):
    __tablename__ = 'User'

    chat_id = Column(Integer, primary_key=True)
    access = Column(Integer, primary_key=True, default='user')
    first_name = Column(Text)
    second_name = Column(Text)
    username = Column(Text)


class UserURL(Base):
    __tablename__ = 'UserURL'

    chat_id = Column(Integer, primary_key=True)
    url = Column(Text, primary_key=True)
    html = Column(Text)
    difference = Column(Text)


class UserToken(Base):
    __tablename__ = 'UserToken'

    chat_id = Column(Integer, primary_key=True)
    token = Column(Text, primary_key=True)
