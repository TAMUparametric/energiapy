"""Decorators for functions."""

import logging
import time
from functools import wraps


def once(func):
    """Ensures the function is executed only once."""

    def wrapper(*args, **kwargs):
        if not hasattr(wrapper, "has_run"):
            wrapper.has_run = True
            return func(*args, **kwargs)

    return wrapper


def timer(
    logger: logging.Logger,
    kind=None,
    level=logging.INFO,
):
    """Logs execution time and optionally shows a full computation using function arguments and result."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            # returns the result if successful, else False
            result = func(*args, **kwargs)
            elapsed = time.time() - start

            if result is not False:

                if kind == 'balance-update':

                    msg = f"⚖  Updated {result[0].commodity} balance with {result[1]}{result[0]}"

                elif kind == 'balance-init':

                    msg = f"⚖  Initiated {result.commodity} balance in ({result.space}, {result.time})"

                elif kind == 'map':
                    msg = f"🧭  Mapped {(result[1] - result[2])[0]} for {result[0]} {result[1]} ⟺ {result[2]}"

                elif kind == 'bind':
                    sample = result[0]
                    aspect = sample.aspect
                    domain = sample.domain
                    rel = result[1]

                    if rel == "ub":
                        rel = "≤"
                    elif rel == "lb":
                        rel = "≥"
                    else:
                        rel = "="

                    msg = f"🔗  Bound [{rel}] {domain.primary} {aspect} in ({domain.space}, {domain.time})"

                elif kind == 'assume-capacity':
                    msg = f"💡  Assumed {result[0]} capacity unbounded in ({result[1]}, {result[2]})"

                elif kind == 'assume-operate':
                    msg = f"💡  Assumed {result[0]} operate bounded by capacity in ({result[1]}, {result[2]})"

                elif kind == 'assume-inventory':
                    msg = f"💡  Assumed {result[0]} inventory bounded by capacity in ({result[1]}, {result[2]})"

                elif kind == 'locate':
                    msg = f"🌍  Located {result[0]} in {', '.join([str(s) for s in result[1]])}"

                elif kind == 'production':
                    msg = f"🏭  Operating streams introduced for {result[0]} in {', '.join([str(s) for s in result[1]])}"

                elif kind == 'construction':
                    msg = f"🏗  Construction streams introduced for {result[0]} in {', '.join([str(s) for s in result[1]])}"

                else:
                    msg = f"  Executed {func.__name__}"

                logger.log(
                    level,
                    f"{msg:<75} ⏱ {elapsed:.4f} s",
                )

        return wrapper

    return decorator
