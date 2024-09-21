"""Process converts one Resource to another Resource
"""

from dataclasses import dataclass, field

from ...elements.parameters.balances.conversion import Conversion
from ..spatial.location import Location
from ._operation import _Operation


@dataclass
class Process(
    _Operation,
):
    """Process converts one Resource to another Resource

    Attributes:
        capacity (IsBnd): bound on the capacity of the Operation
        produce (IsBnd): bounded by capacity of Process. Reported by Operate as well
        buy (IsBnd): bound on amount of Resource bought by Process
        sell (IsBnd): bound on amount of Resource sold by Process
        use (IsBnd): bound on amount of Land or Material used by Process
        setup_use (IsExt): Land or Material setup_use per unit capacity
        use_emission (IsExt): emission due to land or Material use
        capex (IsInc): capital expense per Capacitate
        opex (IsInc): operational expense based on Operation
        setup_emission (IsExt): emission due to construction activity
        buy_price (IsInc): price to buy per unit basis
        sell_price (IsInc): price at which to sell per unit basis
        credit (IsExt): credit received per unit basis sold
        penalty (IsExt): penalty paid for not meeting lower bound of sell
        conversion (IsCnv): conversion of Resource to other Resources
        locations (list[Location]): locations where the Process is located
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component

    """

    conversion: dict | Conversion = field(default_factory=dict)
    locations: list[Location] = field(default_factory=list)

    def __post_init__(self):
        _Operation.__post_init__(self)


    @staticmethod
    def _at():
        """Spatial attributes"""
        return 'locations'

    @property
    def operated(self):
        """The base Resource"""
        return self.conversion.operated

    @property
    def discharged(self):
        """The discharged Resources"""
        return self.conversion.discharged

    @property
    def consumed(self):
        """The consumed Resources"""
        return self.conversion.consumed

    @property
    def modes(self):
        """The modes of conversion"""
        return self.conversion.modes

    @property
    def x_conv(self):
        """The number of modes"""
        return self.conversion.n_modes

    @property
    def balance(self):
        """The balance of resources"""
        return self.conversion.balance

    @property
    def is_balanced(self):
        """The Process conversion is Conversion"""
        return self._balanced

    @property
    def resources(self):
        """Resources in Conversion"""
        return self.conversion.involved

    def conversionize(self):
        """Makes the conversion"""

        if not self._balanced:
            self.conversion = Conversion(conversion=self.conversion, process=self)
            self._balanced = True
