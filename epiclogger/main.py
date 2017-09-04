import logging, sys, traceback, os
from datetime import datetime

class EpicTransport(logging.Handler):
    """ Handler class for logging
    """
    def emit(self, record):
        # Check production
        print (record.__dict__)
        pass

    def __send_to_bugsnag(self, json_log):
        """ Send json to bugsnag
        """
        pass

    def __send_to_stackdriver(self, json_log):
        """ Send json to stackdriver
        """
        pass

    def print_to_console(self, json_log):
        """ Print to stdout
        """
        pass



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
        # 1. Get traceback
        # 2. Get metadata, if context exists, get user and correlation id
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
            "event_time" : datetime.isoformat,
            "service_context": {
                "service" : self.service_name,
                "service_version" : self.service_version
            },
            "level": level,
            "context" : context,
            "message" : message + "Traceback: \n" + stacktrace,
            "metadata": metadata
        }

        print(output_metadata)
        # super(EpicLogger, self).error('Called super\'s error')

try:
    1+"jehgjkg"
except TypeError as type_error: 
    test = EpicLogger()
    print (sys.exc_info())
    test.error("Cannot add numbers",{},type_error, 'crit')
