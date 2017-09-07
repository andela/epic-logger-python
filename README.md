# Epic logger python
Epic logger python is a python library that helps standardise logging.

## Testing
To test the logging, run:

`python epiclogger/test.py <env>`

`<env>` can be `dev`, `prod`, `staging` or `test`.

If testing production logging, add a bugsnag API key.
`python epiclogger/test.py prod <bugsnag_api_key>`
