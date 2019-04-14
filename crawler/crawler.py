#!usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import argparse
import logging.config
import requests
import telebot
from difflib import ndiff

from const import HEADERS, LOG_CONFIG
from models import UserURL, db_transaction, session

parser = argparse.ArgumentParser()
parser.add_argument('--token', dest='token', type=str, required=True)

args = parser.parse_args()

bot = telebot.TeleBot(args.token, threaded=False)

logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logger.info("starting...")

    models = session.query(UserURL).all()

    for model in models:
        response = requests.get(url=model.url, headers=HEADERS)

        if model.html is not None:
            diff = ndiff(
                model.html.splitlines(keepends=True),
                response.text.splitlines(keepends=True))
            diff = ''.join(filter(lambda x: x.startswith(('-', '+', '?')), diff))

            logger.info("for chat_id = {0} and url = {1} diff is ".format(model.chat_id, model.url) +
                        ('NOT empty' if diff else 'empty'))

            if diff:
                bot.send_message(model.chat_id, diff)

        model.html = response.text
        with db_transaction(session):
            session.add(model)

    logger.info('terminating...')
