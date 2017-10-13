import logging
import sys
import os
import bugsnag
import colorlog

from epic_logger.json_formatter import StackdriverJsonFormatter
from epic_logger.json_formatter import StackdriverErrorReportingJsonFormatter
from epic_logger.console_formatter import ConsoleFormatter


class _MaxLevelFilter(object):
    def __init__(self, highest_log_level):
        self._highest_log_level = highest_log_level
    def filter(self, log_record):
        return log_record.levelno <= self._highest_log_level

  # A handler for low level logs that should be sent to STDOUT
def info_handler():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.addFilter(_MaxLevelFilter(logging.WARNING))
    formatter = StackdriverJsonFormatter()
    handler.setFormatter(formatter)
    return handler

# A handler for high level logs that should be sent to STDERR
def error_handler():
    handler = logging.StreamHandler(sys.stderr)
    formatter = StackdriverErrorReportingJsonFormatter()
    handler.setFormatter(formatter)
    handler.setLevel(logging.ERROR)
    return handler

# A handler for sending errors to bugsnag
def bugsnag_handler():
    env = os.getenv("PY_ENV", "staging")
    if env == "prod":
        env = "production"
    client = bugsnag.Client(api_key=os.environ.get("BUGSNAG_API_KEY"), release_stag=env)
    handler = client.log_handler()
    handler.setLevel(logging.ERROR)
    return handler

def getProdLogger(name='epic_logger'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(info_handler())
    logger.addHandler(error_handler())
    logger.addHandler(bugsnag_handler())
    return logger

def getDevLogger(name='epic_logger'):
    handler = colorlog.StreamHandler()

    formatter = ConsoleFormatter(
        "%(log_color)s%(levelname)s%(reset)s[%(asctime)s] - %(filename)s:%(lineno)d  %(funcName)s() - %(log_color)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        },
        style='%'
    )

    handler.setFormatter(formatter)

    logger = colorlog.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger

def getLogger(name='epic_logger'):
    env = os.getenv("PY_ENV", "development")
    if env == "development" or env == "test":
        return getDevLogger(name)
    return getProdLogger(name)
