"""Player acts based on information 
"""

# Associated Program Elements are:
#     Bound Parameters - Has, Needs
#     Variables (Actions) - Gives, Takes


from dataclasses import dataclass, fields

from .._attrs._bounds import _PlyBounds
from .._base._defined import _Defined


@dataclass
class Player(_PlyBounds, _Defined):
    """Player represents a decision maker in the Scenario

    A Player has ownership of some Commodities which they give
    They can also gain ownership of some Commodities which they take

    Attributes:
        has (IsBnd): what a Player has
        needs (IsBnd): what a Player needs
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    def __post_init__(self):
        _Defined.__post_init__(self)

    @staticmethod
    def inputs():
        """Inputs"""
        return [f.name for f in fields(_PlyBounds)]
