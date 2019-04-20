# -*- coding: utf-8 -*-
from __future__ import absolute_import

import colorlog

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru',
    'Accept-Encoding': 'br, gzip, deflate',
    'Connection': 'keep-alive',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/61.0.3163.100 Safari/537.36',
}

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {
            '()': colorlog.ColoredFormatter,
            'format': "%(log_color)s%(bold)s%(asctime)s %(levelname)-8s%(message)s",
            'datefmt': "%y/%m/%d %H:%M:%S",
            'reset': True,
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red',
            },
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 5,
            'formatter': 'colored',
            'filename': 'default.log',
            'level': 'INFO',
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': [
                'default',
            ],
        },
    },
}
