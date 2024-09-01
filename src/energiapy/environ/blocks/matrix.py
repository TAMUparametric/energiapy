"""Matrix representation of the Program Model
"""

from dataclasses import dataclass, field

from ._block import _Block


@dataclass
class Matrix(_Block):
    """Matrix representation of the Program Model

    Attributes:
        name (str): Name, takes from Scenario

    """


    def __post_init__(self):
        _Block.__post_init__(self)
