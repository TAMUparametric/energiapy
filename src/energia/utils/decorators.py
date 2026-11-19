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
        return None

    return wrapper


def _timer_message(kind, result, function_name):
    """Describe the completed modeling operation in the timing log."""
    if kind == "balance-update":
        return f"⚖  Updated {result[0].commodity} balance with {result[1]}{result[0]}"
    if kind == "balance-init":
        return f"⚖  Initiated {result.commodity} balance in ({result.space}, {result.time})"
    if kind == "map":
        return f"🧭  Mapped {(result[1] - result[2])[0]} for {result[0]} {result[1]} ⟺ {result[2]}"
    if kind == "bind":
        sample, relation = result[0], result[1]
        rel = {"ub": "≤", "lb": "≥"}.get(relation, "=")
        domain = sample.domain
        return f"🔗  Bound [{rel}] {domain.primary} {sample.aspect} in ({domain.space}, {domain.time})"

    assumptions = {
        "assume-capacity": "capacity unbounded",
        "assume-operate": "operate bounded by capacity",
        "assume-inventory": "inventory bounded by capacity",
    }
    if kind in assumptions:
        return (
            f"💡  Assumed {result[0]} {assumptions[kind]} in ({result[1]}, {result[2]})"
        )

    locations = {
        "locate": "🌍  Located",
        "production": "🏭  Operating streams introduced for",
        "construction": "🏗  Construction streams introduced for",
    }
    if kind in locations:
        message = f"{locations[kind]} {result[0]} in {', '.join(map(str, result[1]))}"
    else:
        message = f"  Executed {function_name}"
    return message


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
                msg = _timer_message(kind, result, func.__name__)
                logger.log(
                    level,
                    f"{msg:<75} ⏱ {elapsed:.4f} s",
                )

        return wrapper

    return decorator
