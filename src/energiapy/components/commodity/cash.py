"""Poishe, Money 
"""

from dataclasses import dataclass, fields

from .._base._simple import _Simple
from ...attrs.bounds import CshBounds
from ._commodity import _Commodity


@dataclass
class Cash(CshBounds, _Simple, _Commodity):
    """Cash is an Asset
    The amount spent or earned at some spatiotemporal dispoqition can be bound

    Attributes:
        spend (IsBoundInput): bound on amount spent
        earn (IsBoundInput): bound on amount earned
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    def __post_init__(self):
        _Simple.__post_init__(self)
        _Commodity.__post_init__(self)

    @staticmethod
    def bounds():
        """Attrs that quantify the bounds of the component"""
        return fields(CshBounds)

    @property
    def expenses(self):
        """Expenses"""
        return self.attr.coll_expenses
