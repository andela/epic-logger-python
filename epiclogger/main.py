import logging, traceback, os, json
from time import time

class EpicTransport(logging.Handler):
    """ Handler class for logging
    """
    def emit(self, record):
        # Check production or other
        env = self.__check_environment()
        if env != "prod":
            self.print_to_console(record)

        if ((env == "prod" or env == "staging") and record.levelname == "ERROR"):
            self.__send_to_bugsnag(record.msg)
            self.__send_to_stackdriver(record.msg)

    def __send_to_bugsnag(self, full_log):
        """ Send json to bugsnag
        """
        # Convert log to json
        # log = 
        print("Sending to bugsnag")

    def __send_to_stackdriver(self, full_log):
        """ Send json to stackdriver
        """
        print("Sending to stackdriver")

    def print_to_console(self, record):
        """ Print to stdout
        """
        # Colorize and print out
        print (record.levelname + " " + record.msg)

    def __check_environment(self):
        env = os.environ.get("PY_ENV")
        if env and env.lower() in ["prod", "staging", "test", "dev"]:
            return env
        return "dev"


class EpicLogger(logging.Logger):
    """ Logger library for Andela python microservices
    """
    def __init__(self):
        super(EpicLogger, self).__init__('epic_logger')
        handler = EpicTransport()
        self.addHandler(handler)
        try:
            self.service_name, self.service_version = os.environ.get("POD_NAME").split("-")
        except AttributeError:
            self.service_name, self.service_version = ["Unavailable", None]

    def error(self, message, metadata, exception, level='ERROR'):
        """ Override error behaviour to add necessary properties
        """
        if level.lower() not in ['error', 'critical']:
            level = 'ERROR'
        raw_traceback = traceback.format_exception(exception.__class__, exception, exception.__traceback__)
        stacktrace = ""
        for line in raw_traceback:
            stacktrace += line

        # Check if metadata is from grpc
        context = "None provided"
        if "userId" in metadata:
            context = {
                "httpRequest": {
                    "method": metadata.method,
                    "url": metadata.endpoint or metadata.eventType or "None provided"
                },
                "user": metadata.userId,
                "referrer": metadata.correlationId,
            }


        output_metadata = {
            "event_time" : time(),
            "service_context": {
                "service" : self.service_name,
                "service_version" : self.service_version
            },
            "level": level,
            "context" : context,
            "message" : message + "Traceback: \n" + stacktrace,
            "metadata": metadata
        }

        output = json.dumps(output_metadata)

        if level == 'ERROR':
            super(EpicLogger, self).error(output)
        else:
            super(EpicLogger, self).critical(output)

