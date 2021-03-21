import logging
from logging.handlers import TimedRotatingFileHandler
import verboselogs

from mate.utils.version import get_version
from mate.motors import set_motor, stop_all_motors


class State(object):
    """State of interactive session including the test definitions, generated tests, test results."""

    def __init__(self):
        self.tests = None
        self.results = None


state = State()

VERSION = (0, 7, 0, "alpha", 0)
__version__ = get_version(VERSION)

# Singleton/ClassVariableSingleton.py
class LoggerSetup(object):
    __instance = None

    def __new__(cls):
        if LoggerSetup.__instance is None:
            LoggerSetup.__instance = object.__new__(cls)
            LoggerSetup.__instance.state = False
        return LoggerSetup.__instance


logger = logging.getLogger("mate")


def setup_logger(debug):
    """Set the level of logging and update log message format."""
    is_logger_setup = LoggerSetup()
    if is_logger_setup.state:
        return
    is_logger_setup.state = True
    if debug:
        format = (
            "{asctime}.{msecs:03.0f} {levelname:8s} [{filename:20s}:{lineno:04d}] "
            "[{module:15s}:{funcName:15s}] {message:80s}"
        )
        level = logging.DEBUG
    else:
        format = "{asctime}.{msecs:03.0f} {levelname:8s} {message:80s}"
        level = logging.INFO

    for handler in logger.handlers:
        logger.removeHandler(handler)
    logging.basicConfig(
        format=format, datefmt="%Y-%m-%d %H:%M:%S", level=level, style="{"
    )
    logger.debug("Setting up logger ....")
