"""Material used by Operations
"""

from dataclasses import dataclass

from ._used import _Used

# Associated Program Elements:
#   BoundParameters - UseBound
#   Operational Parameters - Usage
#   Variables (Use) - Use
#   Variables (Emissions) - EmitUse
#   Variables (Transactions) - TransactUse


@dataclass
class Material(_Used):
    """Material used to set up Operations

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
        _Used.__post_init__(self)

    @property
    def uses(self):
        """Material Uses across the Scenario"""
        return self.taskmaster.report_uses
