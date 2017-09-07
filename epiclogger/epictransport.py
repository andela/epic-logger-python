import os, json

import bugsnag

import logging
import colorlog

class EpicTransport(logging.Handler):
    """ Handler class for logging
    """
    def __init__(self):
        """ Set logger and formatter
        """
        self.env = self.__check_environment()
        self.logger = logging.getLogger('epic_logger')
        # Configure dev transport
        logging.root.setLevel(logging.DEBUG)
        # Change this to change log format
        LOG_FORMAT = "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
        epic_format = colorlog.ColoredFormatter(fmt=LOG_FORMAT, log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bold',
        })

        handler = logging.StreamHandler()
        handler.setFormatter(epic_format)

        # Add handler with epic format
        self.logger.addHandler(handler)

        if self.env == "prod":
            bugsnag_api_key = os.environ.get("BUGSNAG_API_KEY") or None
            project_root = os.environ.get("PROJECT_ROOT") or "noroot"
            bugsnag.configure(api_key=bugsnag_api_key,
                              project_root=project_root )

        super(EpicTransport, self).__init__()


    def emit(self, record):
        # Check production or other
        env = self.__check_environment()
        if self.env != "prod":
            self.print_to_console(record)

        if ((self.env == "prod" or self.env == "staging") and record.levelname == "ERROR"):
            self.__send_to_bugsnag(record.msg)
            self.__send_to_stackdriver(record.msg)

    def __send_to_bugsnag(self, payload):
        """ Send json to bugsnag
        """
        self.logger.info("Sending to bugsnag")
        # Send payload to bugsnag
        bs_handler = bugsnag.handlers.BugsnagHandler()
        # send only ERROR-level logs and above
        bs_handler.setLevel(logging.ERROR)
        prod_logger = logging.getLogger()
        prod_logger.addHandler(bs_handler)
        prod_logger.error(payload)

    def __send_to_stackdriver(self, full_log):
        """ Send json to stackdriver
        """
        self.logger.info("Sending to stackdriver")

    def print_to_console(self, record):
        """ Print to stdout
        """
        # Colorize and print out
        # Reorganize the json payload to remove unnecessary info
        message = record.msg
        if record.levelno > 30:
            raw_message = json.loads(record.msg)
            message = raw_message["message"] + str(raw_message["metadata"])

        self.logger.log(record.levelno, message)

    def __check_environment(self):
        """ Check app environment
        """
        env = os.environ.get("PY_ENV")
        if env and env.lower() in ["prod", "staging", "test", "dev"]:
            return env
        return "dev"
