import unittest
import logging
import json
import sys
import traceback
from io import StringIO

try:
    import xmlrunner
except ImportError:
    pass

sys.path.append('epic_logger')
from epic_logger.json_formatter import StackdriverJsonFormatter
from epic_logger.json_formatter import StackdriverErrorReportingJsonFormatter
import datetime


class TestJsonLogger(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger('logging-test')
        self.logger.setLevel(logging.DEBUG)
        self.buffer = StringIO()

        self.logHandler = logging.StreamHandler(self.buffer)
        self.logger.addHandler(self.logHandler)

    def testDefaultFormat(self):
        fr = StackdriverJsonFormatter()
        self.logHandler.setFormatter(fr)

        msg = "testing logging format"
        self.logger.info(msg)
        log_json = json.loads(self.buffer.getvalue())

        self.assertEqual(log_json["message"], msg)

    def testDefaultJsonKeys(self):
        info_output_keys = [
            'time',
            'message',
            'severity',
        ]

        fr = StackdriverJsonFormatter()
        self.logHandler.setFormatter(fr)

        msg = "testing logging format"
        self.logger.info(msg)
        log_msg = self.buffer.getvalue()
        log_json = json.loads(log_msg)

        for key in info_output_keys:
            if key in log_json:
                self.assertTrue(True)
    
    def testContextGiven(self):
        class Contextitem(object):
            def __init__(self, key="author_name", value="okonkwo"):
                self.key = key
                self.value = value

        class Context(object):
            def invocation_metadata(self):
                return (Contextitem(), Contextitem(key='correlation_id', value='some-nice-id'))
        
        info_output_keys = [
            'time',
            'message',
            'severity',
            'user',
            'correlationId'
        ]

        fr = StackdriverJsonFormatter()
        self.logHandler.setFormatter(fr)

        msg = "testing logging format"
        self.logger.info(msg, extra={'ctx': Context()})
        log_msg = self.buffer.getvalue()
        log_json = json.loads(log_msg)

        for key in info_output_keys:
            if key in log_json:
                self.assertTrue(True)
        self.assertEqual(log_json["user"], "okonkwo")
        self.assertEqual(log_json["correlationId"], "some-nice-id")

    def testLogADict(self):
        fr = StackdriverJsonFormatter()
        self.logHandler.setFormatter(fr)

        msg = {"text": "testing logging", "num": 1, 5: "9",
               "nested": {"more": "data"}}
        self.logger.info(msg)
        logJson = json.loads(self.buffer.getvalue())
        self.assertEqual(logJson.get("text"), msg["text"])
        self.assertEqual(logJson.get("num"), msg["num"])
        self.assertEqual(logJson.get("5"), msg[5])
        self.assertEqual(logJson.get("nested"), msg["nested"])
        self.assertEqual(logJson["message"], None)

    def testLogExtra(self):
        fr = StackdriverJsonFormatter()
        self.logHandler.setFormatter(fr)

        extra = {"text": "testing logging", "num": 1, 5: "9",
                 "nested": {"more": "data"}}
        self.logger.info("hello", extra=extra)
        log_json = json.loads(self.buffer.getvalue())
        self.assertEqual(log_json.get("text"), extra["text"])
        self.assertEqual(log_json.get("num"), extra["num"])
        self.assertEqual(log_json.get("5"), extra[5])
        self.assertEqual(log_json.get("nested"), extra["nested"])
        self.assertEqual(log_json["message"], "hello")

    def testExcInfo(self):
        fr = StackdriverJsonFormatter()
        self.logHandler.setFormatter(fr)
        try:
            raise Exception('test')
        except Exception:

            self.logger.exception("hello")

            expected_value = traceback.format_exc()
            # Formatter removes trailing new line
            if expected_value.endswith('\n'):
                expected_value = expected_value[:-1]

        log_json = json.loads(self.buffer.getvalue())

        self.assertEqual(log_json.get("message"), "hello\n  " + expected_value)

    def testErrorReportngKeys(self):
        class Contextitem(object):
            def __init__(self, key="author_name", value="okonkwo"):
                self.key = key
                self.value = value

        class Context(object):
            def invocation_metadata(self):
                return (Contextitem(), Contextitem(key='correlation_id', value='some-nice-id'))
        
        error_output_keys = [
            'time',
            'message',
            'severity',
            'eventTme',
            'serviceContext',
            'context'
        ]

        fr = StackdriverErrorReportingJsonFormatter()
        self.logHandler.setFormatter(fr)

        msg = "testing logging format"
        self.logger.info(msg, extra={'ctx': Context()})
        log_msg = self.buffer.getvalue()
        log_json = json.loads(log_msg)

        for key in error_output_keys:
            if key in log_json:
                self.assertTrue(True)
        self.assertEqual(log_json["context"]["user"], "okonkwo")
        self.assertEqual(log_json["context"]["httpRequest"]["url"], "testErrorReportngKeys")

if __name__ == '__main__':
    if len(sys.argv[1:]) > 0:
        if sys.argv[1] == 'xml':
            testSuite = unittest.TestLoader().loadTestsFromTestCase(
                TestJsonLogger)
            xmlrunner.XMLTestRunner(output='reports').run(testSuite)
    else:
        unittest.main()