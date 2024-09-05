"""Defined Component that is simple
"""

from dataclasses import dataclass

from ._defined import _Defined


@dataclass
class _Simple(_Defined):
    """Simple Components inherit from this class
    They only have bounds
    These are Cash, Player, Emission, for now
    Again, do not let me tell you how to live your life
    Make more Simple Components if you feel the need
    More power to you
    """

    def __post_init__(self):
        _Defined.__post_init__(self)
