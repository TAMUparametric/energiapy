"""Operational Mode attached to a Parameter"""

from dataclasses import dataclass, field


@dataclass
class Mode:
    """Represents a discrete choice to be taken within a
    spatiotemporal disposition.
    Modes can split you
    Mode of Operation, can be used for Conversion, Use, etc.

    Attributes:
        name (str, float, int]): The name of the mode, usually a number.
    """

    name: int | str
    of: int | str

    def __post_init__(self):

        self.name = str(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
