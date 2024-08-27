"""Player is a class that represents a player in the Scenario
"""

from dataclasses import dataclass
from .._base._simple import _Simple
from ...attrs.bounds import PlyBounds


@dataclass
class Player(PlyBounds, _Simple):
    """A Player in the Scenario

    Attributes:
        has (IsBoundInput): how much of particular commodity the player has
        needs (IsBoundInput): how much of particular commodity the player needs
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component

    """

    def __post_init__(self):
        _Simple.__post_init__(self)