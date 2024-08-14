"""Impact Component
"""

from dataclasses import dataclass

from .._base._simple import _Simple


@dataclass
class _Impact(_Simple):
    """Impact Component"""

    def __post_init__(self):
        _Simple.__post_init__(self)
