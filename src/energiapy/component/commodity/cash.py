"""Poishe, Money 
"""

# Associated Program Elements are:
#     Bound Parameters - SpdBound, ErnBound
#     Variables (Transacts) - Spend, Earn


from dataclasses import dataclass, fields, field
from typing import Self
from ._commodity import _Commodity


@dataclass
class Cash(_Commodity):
    """Cash is an Asset
    The amount spent or earned at some spatiotemporal dispoqition can be bound

    Attributes:
        spend (IsBnd): bound on spending Cash
        earn (IsBnd): bound on earning Cash
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    spend: dict = field(default=None)
    earn: dict = field(default=None)
    ex: dict[Self, float] = field(default=None)

    def __post_init__(self):
        _Commodity.__post_init__(self)

    @staticmethod
    def inputs():
        """Inputs"""
        return [f.name for f in fields(_Transact)]

    @property
    def transacts(self):
        """Transacts"""
        return self.taskmaster.report_transact
