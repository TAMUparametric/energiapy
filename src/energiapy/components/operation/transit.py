"""Transit moves Resources between Locations
"""

from dataclasses import dataclass, field

from ...elements.parameters.balances.freight import Freight
from ..spatial.linkage import Linkage
from ._birther import _Birther


@dataclass
class Transit(
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

    freight: dict | Freight = field(default_factory=dict)
    linkages: list[Linkage] = field(default_factory=list)

    def __post_init__(self):
        _Birther.__post_init__(self)
        self.setup_in = self.setup_out = self.setup

    @property
    def balance(self):
        """Balance attribute"""
        return self.freight

    @staticmethod
    def _at():
        """Spatial attributes"""
        return 'linkages'

    def freightize(self):
        """Makes the freight"""
        if not isinstance(self.balance, Freight):
            self.freight = Freight(freight=self.freight, transit=self)
            self._balanced = True
