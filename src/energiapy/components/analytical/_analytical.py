"""Base for Analytical Components
"""

from dataclasses import dataclass
from .._base._simple import _Simple

@dataclass
class _Analytical(_Simple):
    """Analytical Component"""

    def __post_init__(self):
        _Simple.__post_init__(self)
