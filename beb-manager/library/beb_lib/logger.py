"""This module provides functions to work with logging"""

import logging
import os

LIBRARY_LOGGER_NAME = 'beb_lib_logger'


def get_logger():
    return logging.getLogger(LIBRARY_LOGGER_NAME)


def log_func(logger_name):
    logger = logging.getLogger(logger_name)

    def _log_func(func):
        def _log(self, *args, **kwargs):
            try:
                logger.info("Called function: {}".format(func.__name__))
                logger.debug("\n\tSelf type: {0}, \n\tArgs: {1}, \n\tKwargs: {2}".format(type(self), args, kwargs))
                result = func(self, *args, **kwargs)
                logger.debug("{0} returned: {1}".format(func.__name__, result))
                return result
            except Exception as e:
                logger.error(e)
                raise e
        return _log
    return _log_func


def init_logging(level, filename, log_format, log_datefmt):
    def check_and_create_logger_file(path):
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        try:
            open(path, 'r').close()
        except FileNotFoundError:
            open(path, 'w').close()

    check_and_create_logger_file(filename)

    formatter = logging.Formatter(log_format, log_datefmt)
    file_logging_handler = logging.FileHandler(filename)
    file_logging_handler.setLevel(level)
    file_logging_handler.setFormatter(formatter)

    logger = get_logger()
    logger.setLevel(logging.DEBUG)
    if logger.hasHandlers():
        logger.handlers.clear()

    if level is not None:
        logger.disabled = False
        logger.addHandler(file_logging_handler)
    else:
        logger.disabled = True

