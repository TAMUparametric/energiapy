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
            # returns the result if successful, else False
            result = func(*args, **kwargs)
            elapsed = time.time() - start

            if result:

                if kind == 'balance-update':

                    msg = f"⚖   Updated Balance for {result.commodity} in ({result.space}, {result.time})"

                elif kind == 'balance-init':

                    msg = f"⚖   Initiated Balance for {result.commodity} in ({result.space}, {result.time})"

                elif kind == 'map':
                    msg = f"🧭  Mapped {result[0]} [{(result[1] - result[2])[0]}] : {result[1]} ⟺ {result[2]}"

                elif kind == 'bind':
                    if result[2] == "_ub":
                        rel = "≤"
                    elif result[2] == "_lb":
                        rel = "≥"
                    else:
                        rel = "="
                    msg = f"🔗  Bound [{rel}] {result[0]} in {result[1]}"

                elif kind == 'assume-capacity':
                    msg = f"💡  Assumed {result[0]} capacity unbounded in ({result[1]}, {result[2]})"

                elif kind == 'assume-operate':
                    msg = f"💡  Assumed {result[0]} operate bounded by capacity in ({result[1]}, {result[2]})"

                elif kind == 'assume-inventory':
                    msg = f"💡  Assumed {result[0]} inventory bounded by capacity in ({result[1]}, {result[2]})"

                else:
                    msg = f"⏱  Executed {func.__name__}"

                logger.log(
                    level,
                    f"{msg:<100} ⏱ {elapsed:.4f} s",
                )

        return wrapper

    return decorator
