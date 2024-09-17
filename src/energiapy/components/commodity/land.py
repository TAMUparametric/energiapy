"""Land used by Operations
"""

from dataclasses import dataclass, fields

from .._attrs._bounds import _Use
from .._attrs._exacts import _UseEmit, _UseTransact
from ._commodity import _Commodity


@dataclass
class Land(_Use, _UseTransact, _UseEmit, _Commodity):
    """Land derived from Operation Capacitate
    Use can cost Cash and emit Emissions

    Attributes:
        use (IsBnd): bound for use at some spatiotemporal disposition
        use_cost (IsExt): cost per a unit basis at some spatiotemporal disposition
        use_emission (IsExt): emission per unit basis of use
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component
    """

    def __post_init__(self):
        _Commodity.__post_init__(self)
        # This collects parameters for land use declared at other components

    @staticmethod
    def inputs():
        """Inputs"""
        return [f.name for f in fields(_Use) + fields(_UseTransact) + fields(_UseEmit)]

    @property
    def uses(self):
        """Land Uses across the Scenario"""
        return self.taskmaster.report_use
