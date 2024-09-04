"""Transit moves Resources between Locations
"""

from dataclasses import dataclass, fields

from ...elements.parameters.balances.freight import Freight
from .._attrs._balances import _TrnBalance
from .._attrs._bounds import _OpnBounds, _TrnBounds
from .._attrs._exacts import _TrnExacts
from .._attrs._spatials import _LnkCollection
from ._birther import _Birther

# Associated Program Elements:
#   Bound Parameters - CapBound, OprBound
#   Exact Parameters - StpEmission, StpExpense, OprExpense, StpUse
#   Balance Parameters - Freight
#   Variable (Transact) - TransactOpr, TransactStp
#   Variable (Emissions) - EmitStp, EmitUse
#   Variable (Losses) - Lose
#   Variable (Operate) - Operate
#   Variable (Trade) - Ship
#   Variable (Use) - Use
#   Variable (Rates) - Rate


@dataclass
class _Transit(_OpnBounds, _TrnBounds, _TrnExacts):
    """These are attributes which are original to Transit"""


@dataclass
class Transit(
    _TrnBalance,
    _Transit,
    _LnkCollection,
    _Birther,
):
    """Transit moves Resources between Locations through a Linkage
    There could be a dependent Resource

    A ResourceTrn is generate internally as the stored Resource
    Loading and Unloading Processes are also generated internally
    Capacitate in this case is the amount of Resource that can be Transported
    Loading and Unloading capacities are the same as Transit Capacitate

    Attributes:
        capacity (IsBnd): bound on the capacity of the Operation
        transport (IsBnd): bound by Capacitate. Reported by operate as well.
        ship (IsBnd): bound on shipping a Resource
        use (IsBnd): bound on amount of Land or Material used by Process
        setup_use (IsExt): Land or Material setup_use per unit capacity
        use_emission (IsExt): emission due to land or Material use
        capex (IsInc): capital expense per Capacitate
        opex (IsInc): operational expense based on Operation
        setup_emission (IsExt): emission due to construction activity
        freight (IsBlc): balance of Resources carried by the Operation
        freight_loss: (IsExt): loss of resource during transportation
        linkages (list[IsLinkage]): linkages between which Transit exists
        speed (IsExt): speed of Transit
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component

    """

    def __post_init__(self):
        _Birther.__post_init__(self)

    @property
    def _operate(self):
        """Returns attribute value that signifies operating bounds"""
        if self.transport:
            return self.transport
        else:
            return [1]

    @property
    def balance(self):
        """Balance attribute"""
        return self.freight

    @staticmethod
    def inputs():
        """Input attributes"""
        return [f.name for f in fields(_Transit)]

    def freightize(self):
        """Makes the freight"""
        if not isinstance(self.freight, Freight):
            self.freight = Freight(freight=self.freight, transit=self)
            self._balanced = True
