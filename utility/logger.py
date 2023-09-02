import logging
import logging.handlers
from pathlib import Path

from utility.constants import Constants

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]

fileLoc = Constants.LOG_FILE_NAME.value

logging.basicConfig(format="%(process)d-%(levelname)s-%(message)s")


def get_logger(name):
    LOGGER = logging.getLogger(name)

    log_level = "DEBUG"
    if log_level == "DEBUG":
        LOGGER.setLevel(logging.DEBUG)
    elif log_level == "INFO":
        LOGGER.setLevel(logging.INFO)
    elif log_level == "ERROR":
        LOGGER.setLevel(logging.ERROR)
    else:
        LOGGER.setLevel(logging.INFO)

    handler_file = logging.handlers.RotatingFileHandler(
        fileLoc,
        mode="a",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding=None,
        delay=0,
    )

    log_formatter = logging.Formatter(
        "%(asctime)s -- %(levelname)s -- %(name)s -- %(funcName)s -- (%(lineno)d) -- %(message)s"
    )

    handler_file.setFormatter(log_formatter)

    if log_level == "DEBUG":
        handler_file.setLevel(logging.DEBUG)
    elif log_level == "INFO":
        handler_file.setLevel(logging.INFO)
    elif log_level == "ERROR":
        handler_file.setLevel(logging.ERROR)
    else:
        handler_file.setLevel(logging.INFO)
    LOGGER.addHandler(handler_file)
    return LOGGER
