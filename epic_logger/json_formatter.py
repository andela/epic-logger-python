import logging
import sys
import os
from pythonjsonlogger import jsonlogger
from datetime import datetime

class StackdriverJsonFormatter(jsonlogger.JsonFormatter, object):
    def __init__(self, fmt="%(levelname) %(message) %(funcName) %(name)", style='%', *args, **kwargs):
        jsonlogger.JsonFormatter.__init__(self, fmt=fmt, *args, **kwargs)

    def process_log_record(self, log_record):
        """
        """
        log_record['severity'] = log_record['levelname']
        del log_record['levelname']

        log_record['moduleName'] = log_record["name"]
        del log_record["name"]

        log_record['time'] = datetime.utcnow().isoformat()
        if 'exc_info' in log_record:
            log_record['message'] = log_record['message'] + '\n  ' + log_record['exc_info']
            del log_record['exc_info']

        if 'ctx' in log_record:
            metadata = log_record['ctx'].invocation_metadata()
            del log_record['ctx']
            for item in metadata:
                if item.key == 'author_name':
                    log_record['user'] = item.value
                elif item.key == 'correlation_id':
                    log_record['correlationId'] = item.value
        for key, value in log_record.items():
            if hasattr(value, '__dict__'):
                log_record[key] = value.__dict__

        return super(StackdriverJsonFormatter, self).process_log_record(log_record)

class StackdriverErrorReportingJsonFormatter(StackdriverJsonFormatter, object):
    def __init__(self, fmt="%(levelname) %(message) %(funcName) %(name)", style='%', *args, **kwargs):
        StackdriverJsonFormatter.__init__(self, fmt=fmt, *args, **kwargs)

    def process_log_record(self, log_record):
        sd_formatter = super(StackdriverErrorReportingJsonFormatter, self)
        pod_array = os.getenv('POD_NAME', 'my-service-123-456').split('-')
        version = pod_array[-2]
        service_array = pod_array[:len(pod_array) -2]
        service = '-'.join(service_array)
        log_record = sd_formatter.process_log_record(log_record)
        log_record['eventTime'] = log_record['time']
        log_record['serviceContext'] = {'service': service, 'version': version}
        http_request = {'method': 'POST', 'url': log_record['funcName']}
        del log_record['funcName']
        log_record['context'] = {'httpRequest': http_request}
        if 'user' in log_record:
            log_record['context']['user'] = log_record['user']
            del log_record['user']
        return log_record
