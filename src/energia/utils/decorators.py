"""Decorators for functions"""

import logging
import time
from functools import wraps


def once(func):
    """Ensures the function is executed only once"""

    def wrapper(*args, **kwargs):
        if not hasattr(wrapper, "has_run"):
            wrapper.has_run = True
            return func(*args, **kwargs)

    return wrapper


def timer(logger: logging.Logger, msg=None, level=logging.INFO):
    """
    Logs execution time and optionally shows a full computation using function arguments and result.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            domain = func(*args, **kwargs)
            elapsed = time.time() - start

            logger.log(level, f"{msg} ⏱  {elapsed:.6f} s")
            return domaing

        return wrapper

    return decorator
