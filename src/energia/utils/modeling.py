"""Utilities for modeling"""


def retry(func, attempts: int = 2, exceptions=(Exception,)):
    """
    Retry a function a number of times if it raises specified exceptions.

    :param func: The function to retry.
    :type func: callable
    :param attempts: Number of attempts.
    :type attempts: int
    :param exceptions: Exceptions to catch and retry on.
    :type exceptions: tuple[Exception]

    :return: The result of the function if successful.
    """
    last_exception = None
    for _ in range(attempts):
        try:
            return func()
        except exceptions as e:
            last_exception = e
    raise last_exception
