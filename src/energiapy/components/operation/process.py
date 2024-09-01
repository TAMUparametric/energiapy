"""Process converts one Resource to another Resource
"""

from dataclasses import dataclass, fields

from ...elements.parameters.balances.conversion import Conversion
from .._attrs._balances import _ProBalance
from .._attrs._bounds import _OpnBounds, _ProBounds, _ResLocBounds
from .._attrs._exacts import _ProExacts, _ResExacts
from .._attrs._spatials import LocCollection
from ._operation import _Operation

# Associated Program Elements:
#   Bound Parameters - CapBound, OprBound
#   Exact Parameters - StpEmission, StpExpense, OprExpense, Usage
#   Balance Parameters - Conversion
#   Resource Parameters - BuyBound, SellBound, BuyPrice, SellPrice, Credit, Penalty
#   Variable (Transact) - TransactOpr, TransactStp
#   Variable (Emissions) - EmitStp, EmitUse
#   Variable (Operate) - Operate
#   Variable (Use) - Use
#   Variable (Rates) - Rate


@dataclass
class Process(
    _ProBalance,
    _OpnBounds,
    _ProBounds,
    _ProExacts,
    _ResLocBounds,
    _ResExacts,
    LocCollection,
    _Operation,
):
    """Process converts one Resource to another Resource

    Attributes:
        capacity (IsBnd): bound on the capacity of the Operation
        produce (IsBnd): bounded by capacity of Process. Reported by Operate as well
        land_use (IsExt): land use per Capacitate
        material_use (IsExt): material use per Capacitate
        capex (IsInc): capital expense per Capacitate
        opex (IsInc): operational expense based on Operation
        land_use_emission (IsExt): emission due to land use
        material_use_emission (IsExt): emission due to material use
        buy (IsBnd): bound on amount of Resource bought by Process
        sell (IsBnd): bound on amount of Resource sold by Process
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

    def __post_init__(self):
        _Operation.__post_init__(self)

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
            for f in fields(_OpnBounds)
            + fields(_ProBounds)
            + fields(_ProExacts)
            + fields(_ResExacts)
            + fields(_ResLocBounds)
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
