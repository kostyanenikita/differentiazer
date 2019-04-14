#!usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import argparse
import logging.config
import telebot
import uuid
from functools import wraps
from inspect import getfullargspec

from const import LOG_CONFIG
from models import User, UserToken, UserURL, db_transaction, session
from tools import is_url

parser = argparse.ArgumentParser()
parser.add_argument('--token', dest='token', type=str, required=True)

args = parser.parse_args()

bot = telebot.TeleBot(args.token, threaded=False)

logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)


def required(access=None, argc=None):
    def outer_wrapper(func):
        idx = getfullargspec(func).args.index('message')

        @wraps(func)
        def wrapper(*args, **kwargs):
            message = args[idx]

            if access is not None:
                model = session.query(User.access).filter(User.chat_id == message.chat.id).first()
                if model is None or model.access not in access:
                    bot.send_message(message.chat.id, 'no access')
                    logger.warning("unauthorized request by user_id = {0}".format(message.chat.id))
                    return

            if argc is not None:
                if len(message.text.split()) < argc:
                    bot.send_message(message.chat.id, 'wrong args')
                    return

            return func(*args, **kwargs)
        return wrapper
    return outer_wrapper


@bot.message_handler(commands=['ping'])
def ping(message):
    bot.send_message(message.chat.id, 'alive')


@bot.message_handler(commands=['generate_token'])
@required(access=['admin'])
def generate_token(message):
    token = str(uuid.uuid4())
    with db_transaction(session):
        session.add(UserToken(chat_id=message.chat.id, token=token))

    bot.send_message(message.chat.id, token)


@bot.message_handler(commands=['add'])
@required(access=['user', 'admin'], argc=2)
def add(message):
    args = message.text.split()

    if not is_url(args[1]):
        bot.send_message(message.chat.id, 'url is invalid')
        return

    with db_transaction(session):
        session.add(UserURL(chat_id=message.chat.id, url=args[1]))

    bot.send_message(message.chat.id, 'successful')
    logger.info("for chat_id = {0} added url = {1}".format(message.chat.id, args[1]))


@bot.message_handler(commands=['delete'])
@required(access=['user', 'admin'], argc=2)
def delete(message):
    args = message.text.split()

    model = session.query(UserURL).filter(UserURL.url == args[1]).first()
    if model is None:
        bot.send_message(message.chat.id, 'no such url')
        return

    with db_transaction(session):
        session.delete(model)

    bot.send_message(message.chat.id, 'successful')
    logger.info("for chat_id = {0} deleted url = {1}".format(message.chat.id, args[1]))


@bot.message_handler(commands=['url_list'])
@required(access=['user', 'admin'])
def url_list(message):
    models = session.query(UserURL).filter(UserURL.chat_id == message.chat.id).all()
    models = ["{0}. {1}".format(i + 1, model.url) for i, model in enumerate(models)]
    models = '\n'.join(models) or 'no urls'

    bot.send_message(message.chat.id, models)
    logger.info("url list request was performed by chat_id = {0}".format(message.chat.id))


@bot.message_handler(commands=['user_list'])
@required(access=['admin'])
def user_list(message):
    models = session.query(User).all()
    models = ["{0}. @{1} | {2} {3} | {4}".format(i + 1, model.username, model.first_name, model.second_name,
              model.access) for i, model in enumerate(models)]
    models = '\n'.join(models) or 'no users'

    bot.send_message(message.chat.id, models)
    logger.info("user list request was performed by chat_id = {0}".format(message.chat.id))


@bot.message_handler(commands=['register'])
@required(argc=2)
def register(message):
    args = message.text.split()

    model = session.query(User).filter(User.chat_id == message.chat.id).first()
    if model is not None:
        bot.send_message(message.chat.id, 'already registered')
        return

    model = session.query(UserToken).filter(UserToken.token == args[1]).first()
    if model is None:
        bot.send_message(message.chat.id, 'no such token')
        return

    with db_transaction(session):
        session.delete(model)
        session.add(User(chat_id=message.chat.id))

    bot.send_message(message.chat.id, 'successful')
    logger.info("new user was registered with chat_id = {0}".format(message.chat.id))


if __name__ == '__main__':
    bot.polling(none_stop=True)
