from setuptools import setup

setup(name='epic_logger',
  version='1.0.0',
  description='The funniest joke in the world',
  url='https://github.com/andela/epic-logger-python',
  author='Ikem Okonkwo',
  author_email='ikem.okonkwo@andela.com',
  license='MIT',
  packages=['epic_logger'],
  install_requires=[
    'python-json-logger',
    'bugsnag',
    'colorlog',
  ],
  zip_safe=False)