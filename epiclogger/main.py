import logging, traceback, os, json
from time import time

from epictransport import EpicTransport

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
            "message" : message + "\n" + stacktrace,
            "metadata": metadata
        }

        output = json.dumps(output_metadata)

        if level == 'ERROR':
            super(EpicLogger, self).error(output)
        else:
            super(EpicLogger, self).critical(output)
