"""Decorators for functions"""

import logging
import time
from contextlib import contextmanager


def once(func):
    """Ensures the function is executed only once"""

    def wrapper(*args, **kwargs):
        if not hasattr(wrapper, "has_run"):
            wrapper.has_run = True
            return func(*args, **kwargs)

    return wrapper


@contextmanager
def timer(logger: logging.Logger, msg: str, level: int = logging.INFO):
    """
    Context manager to log a message with elapsed time.

    Usage:
        with log_time(logger, "Doing something"):
            # code block
    """
    start = time.time()
    yield
    elapsed = time.time() - start
    logger.log(level, f"{msg} ⏳ {elapsed:.6f} seconds")
