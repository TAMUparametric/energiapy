"""Poishe, Money 
"""

# Associated Program Elements are:
#     Bound Parameters - SpdBound, ErnBound
#     Variables (Transacts) - Spend, Earn


from dataclasses import dataclass, fields

from .._attrs._bounds import _CshBounds
from .._base._defined import _Simple
from ._commodity import _Commodity


@dataclass
class Cash(_CshBounds, _Simple, _Commodity):
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

    def __post_init__(self):
        _Simple.__post_init__(self)
        _Commodity.__post_init__(self)

    @staticmethod
    def inputs():
        """Inputs"""
        return [f.name for f in fields(_CshBounds)]

    @property
    def transactions(self):
        """Transacts"""
        return self.taskmaster.report_transactions
