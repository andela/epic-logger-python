import os, sys

from main import EpicLogger

def test_prod_log():
    os.environ["PY_ENV"] = "prod"
    test_log()

def test_dev_log():
    os.environ["PY_ENV"] = "dev"
    test_log()

def test_log():
    try:
        1+"jehgjkg"
    except TypeError as type_error: 
        test = EpicLogger()
        test.info("Here's some info")
        test.warn("And a warning")
        test.debug("Debug")

        # Test error
        test.error("Adding strings and integers is not clever", {"extra":"info"}, type_error)

        # Test critical
        test.error("Cannot add numbers",{ "This": "is extra info" },type_error, 'critical')

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "prod":
        test_prod_log()
    else:
        test_dev_log()
