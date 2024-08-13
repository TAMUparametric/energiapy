"""Custom Error Classes"""


class CacodcarError(ValueError):
    """This error could be because of some booboo I made"""

    def __init__(self, message):
        self.message = f'{message}\n This could be a developer error\n raise an issue on github if you think this is a bug\n or contact cacodcar@tamu.edu\n'

        super().__init__(self.message)
