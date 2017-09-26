import sys
from epic_logger import getLogger
from datetime import datetime

class Person(object):
    def __init__(self):
        self.name = 'codesword'
        self.github = 'github.com/codesword'

    def __str__(self):
        return self.name +  ' + ' + self.github

class Contextitem(object):
    def __init__(self, key="author_name", value="okonkwo"):
        self.key = key
        self.value = value

class Context(object):
    def invocation_metadata(self):
        return (Contextitem(), Contextitem(key='correlation_id', value='some id'))

context = Context()
def run_user_code(log):
    log.info('info message', extra={'person': Person()})
    log.debug('debug message', extra={ 'ttls': { 'core': 'ikem'}, 'ctx': Context()})
    log.warning('warning message', extra={ 'sse': ['adebayo', 'james', 'thuita'] })
    try:
        i = 1/0
    except:
        print("Exception in user code:")
        print('-'*60)
        log.error('error message', exc_info=True, extra={ 'user': 'ikem' , 'my_time': datetime.utcnow().isoformat()})
        log.critical('critical message', exc_info=True, extra={ 'user': 'ikem' , 'my_time': datetime.utcnow().isoformat()})
        print('-'*60)

run_user_code(logger)