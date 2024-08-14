"""Variables for Actions taken by Players
"""

from dataclasses import dataclass

from ._variable import _Variable


@dataclass
class Gives(_Variable):
    """Has is the ownership of a Player"""

    def __post_init__(self):
        _Variable.__post_init__(self)


@dataclass
class Takes(_Variable):
    """Needs is the requirement of a Player"""

    def __post_init__(self):
        _Variable.__post_init__(self)
