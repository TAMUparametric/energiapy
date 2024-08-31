"""Emission, released based on some activity or operation 
"""

from dataclasses import dataclass, fields

from .._attrs._bounds import _EmnBounds
from .._base._defined import _Simple
from ._commodity import _Commodity

# Associated Program Elements are:
#     Bound Parameters - EmnBound
#     Variables (Emissions) - Emit


@dataclass
class Emission(_EmnBounds, _Simple, _Commodity):
    """Emission are generated through:
            Commodity Use, Trade, Loss
            Operational Setup

    They are measured based on thier potential impact on the environment

    Attributes:
        emit (IsBnd): bound on Emission
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
        """Input attributes"""
        return [f.name for f in fields(_EmnBounds)]

    @property
    def emissions(self):
        """Emissions across the components"""
        return self.taskmaster.report_emissions
