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


def timer(logger: logging.Logger, kind=None, level=logging.INFO):
    """
    Logs execution time and optionally shows a full computation using function arguments and result.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            # returns the domain if successful
            domain = func(*args, **kwargs)
            elapsed = time.time() - start

            if domain:

                if kind == 'balance-update':

                    msg = f"Updating Balance for {domain.commodity} in ({domain.space}, {domain.time})"

                elif kind == 'balance-init':

                    msg = f"Initiating Balance for {domain.commodity} in ({domain.space}, {domain.time})"
                else:
                    msg = f"Executing {func.__name__}"

                logger.log(
                    level,
                    f"{msg}  ⏱  {elapsed:.6f} s",
                )

        return wrapper

    return decorator
