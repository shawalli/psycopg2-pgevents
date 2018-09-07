"""This module provides functionality for debug logging within the package."""
__all__ = ['log', 'set_debug']

from contextlib import contextmanager
from typing import Generator
import logging
import sys

_DEBUG_ENABLED = False

_LOGGER_NAME = 'pgevents.debug'


def set_debug(enabled: bool):
    """Enable or disable debug logs for the entire package.

    Parameters
    ----------
    enabled: bool
        Whether debug should be enabled or not.

    """
    global _DEBUG_ENABLED

    if not enabled:
        log('Disabling debug output...', logger_name=_LOGGER_NAME)
        _DEBUG_ENABLED = False
    else:
        _DEBUG_ENABLED = True
        log('Enabling debug output...', logger_name=_LOGGER_NAME)


@contextmanager
def _create_logger(name: str, level: int) -> Generator[logging.Logger, None, None]:
    """Create a context-based logger.
    Parameters
    ----------
    name: str
        Name of logger to use when logging.
    level: int
        Logging level, one of logging's levels (e.g. INFO, ERROR, etc.).

    Returns
    -------
    logging.Logger
        Named logger that may be used for logging.
    """
    # Get logger
    logger = logging.getLogger(name)

    # Set logger level
    old_level = logger.level
    logger.setLevel(level)

    # Setup handler and add to logger
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)-5s [%(name)s]: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    yield logger

    # Reset logger level
    logger.setLevel(old_level)

    # Remove handler from logger
    logger.removeHandler(handler)
    handler.close()


def log(message: str, *args: str, category: str='info', logger_name: str='pgevents'):
    """Log a message to the given logger.

    If debug has not been enabled, this method will not log a message.

    Parameters
    ----------
    message: str
        Message, with or without formatters, to print.
    args: Any
        Arguments to use with the message. args must either be a series of
        arguments that match up with anonymous formatters
        (i.e. "%<FORMAT-CHARACTER>") in the format string, or a dictionary
        with key-value pairs that match up with named formatters
        (i.e. "%(key)s") in the format string.
    logger_name: str
        Name of logger to which the message should be logged.

    """
    global _DEBUG_ENABLED

    if _DEBUG_ENABLED:
        level = logging.INFO
    else:
        level = logging.CRITICAL + 1

    with _create_logger(logger_name, level) as logger:
        log_fn = getattr(logger, category, None)
        if log_fn is None:
            raise ValueError('Invalid log category "{}"'.format(category))

        log_fn(message, *args)
