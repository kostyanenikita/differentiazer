#!usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import argparse
import logging.config
import requests
import telebot
from hashlib import md5

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
        logger.info("checking url = {0} for chat_id = {1}".format(model.url, model.chat_id))

        m = md5()
        m.update(response.text.encode('utf-8'))
        if m.hexdigest() == model.hash:
            continue

        if model.hash is not None:
            logger.info("for chat_id = {0} url = {1} was changed".format(model.chat_id, model.url))
            bot.send_message(model.chat_id, "url = {0} was changed".format(model.url))

        model.hash = m.hexdigest()
        with db_transaction(session):
            session.add(model)

    logger.info('terminating...')
