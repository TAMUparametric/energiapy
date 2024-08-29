"""Process converts one Resource to another Resource
"""

from dataclasses import dataclass, field, fields

from ...attrs.balances import ProBalance
from ...attrs.bounds import OpnBounds, ProBounds, ResLocBounds
from ...attrs.exacts import ProExacts, ResExacts
from ...attrs.spatials import LocCollection
from ...parameters.balances.conversion import Conversion
from ._operational import _Operational


@dataclass
class Process(
    ProBalance,
    OpnBounds,
    ProBounds,
    ProExacts,
    ResLocBounds,
    ResExacts,
    LocCollection,
    _Operational,
):
    """Process converts one Resource to another Resource

    Attributes:
        capacity (IsBoundInput): bound on the capacity of the Operation
        land (IsExactInput): land use per Capacity
        material (IsExactInput): material use per Capacity
        capex (IsExactInput): capital expense per Capacity
        opex (IsExactInput): operational expense based on Operation
        emission (IsExactInput): emission due to construction per Capacity
        buy (IsBoundInput): bound on amount of Resource bought by Process
        sell (IsBoundInput): bound on amount of Resource sold by Process
        price_buy (IsExactInput): price to buy per unit basis
        price_sell (IsExactInput): price at which to sell per unit basis
        credit (IsExactInput): credit received per unit basis sold
        penalty (IsExactInput): penalty paid for not meeting lower bound of sell
        conversion (IsConvInput): conversion of Resource to other Resources
        produce (IsBoundInput): bounded by capacity of Process. Reported by Operate as well
        locations (List[IsLocation]): locations where the Process is located
        basis (str): basis of the component
        citation (dict): citation of the component
        block (str): block of the component
        introduce (str): index in scale when the component is introduced
        retire (str): index in scale when the component is retired
        label (str): label of the component


    """

    # Depreciated
    varying: str = field(default=None)
    prod_max: str = field(default=None)
    prod_min: str = field(default=None)

    def __post_init__(self):
        _Operational.__post_init__(self)

        # *----------------- Depreciation Warnings-----------------------------

        _name = getattr(self, 'name', None)

        _changed = {'prod_max': 'cap_max', 'prod_min': 'cap_min'}

        for i, j in _changed.items():
            if getattr(self, i):
                raise ValueError(f'{_name}: {i} is depreciated. Please use {j} instead')

    @property
    def base(self):
        """The base resource"""
        return self.conversion.base

    @property
    def sold(self):
        """The resources sold"""
        return self.conversion.sold

    @property
    def bought(self):
        """The resources bought"""
        return self.conversion.bought

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
    def _operate(self):
        """Returns attribute value that signifies operating bounds"""
        if self.produce:
            return self.produce
        else:
            return [1]

    @property
    def is_balanced(self):
        """The Process conversion is Conversion"""
        return self._balanced

    @staticmethod
    def inputs():
        """Input attributes"""
        return [
            f.name
            for f in fields(OpnBounds)
            + fields(ProBounds)
            + fields(ProExacts)
            + fields(ResExacts)
            + fields(ResLocBounds)
        ]

    @property
    def resources(self):
        """Resources in Conversion"""
        return self.conversion.involved

    def conversionize(self):
        """Makes the conversion"""

        if not self._balanced:
            self.conversion = Conversion(conversion=self.conversion, process=self)
            self._balanced = True
