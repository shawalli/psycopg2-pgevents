import logging

_DEBUG_ENABLED = False


def set_debug(enabled: bool):
    """Enable or disable debug logs for the entire package.

    Parameters
    ----------
    enabled: bool
        Whether debug should be enabled or not.

    """
    global _DEBUG_ENABLED

    if not enabled:
        log('Disabling debug output...', logger='pyscopg2-pgevents')
        _DEBUG_ENABLED = False
    else:
        _DEBUG_ENABLED = True
        log('Enabling debug output...', logger='pyscopg2-pgevents')


def log(message, *args, category='info', logger='psycopg2'):
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
    logger: str
        Logger to which the message should be logged.

    """
    global _DEBUG_ENABLED

    logger = logging.getLogger(logger)

    if _DEBUG_ENABLED:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.CRITICAL + 1)

    log_fn = getattr(logger, category, None)
    if log_fn is None:
        raise ValueError('Invalid log category "{}"'.format(category))

    log_fn(message, *args)
