"""Currency"""

from dataclasses import dataclass

from operator import is_
from typing import Self

# from ..operation.task import Task
# from ...modeling.variables.default import Transact

# from ..impact.categories import Eco
from ._commodity import _Commodity


@dataclass
class Currency(_Commodity):  # , Transact):
    """Same as Economic Impact (Eco)

    :param label: Label of the commodity, used for plotting. Defaults to None.
    :type label: str, optional
    :param name: Name of the commodity, used for indexing. Defaults to None.
    :type name: str, optional
    :param basis: Unit basis of the commodity. Defaults to None.
    :type basis: Unit, optional


    :ivar model: The model to which the component belongs.
    :vartype model: Model
    :ivar name: Set when the component is assigned as a Model attribute.
    :vartype name: str
    :ivar _indexed: True if an index set has been created.
    :vartype _indexed: bool
    :ivar constraints: List of constraints associated with the component.
    :vartype constraints: list[str]
    :ivar domains: List of domains associated with the component.
    :vartype domains: list[Domain]
    :ivar aspects: Aspects associated with the component with domains.
    :vartype aspects: dict[Aspect, list[Domain]]
    :ivar conversions: List of conversions associated with the commodity. Defaults to [].
    :vartype conversions: list[Conversion]
    :ivar insitu: If the commodity only exists insitu, i.e., does not scale any domains
    :vartype insitu: bool, optional
    """

    def __post_init__(self):
        _Commodity.__post_init__(self)

    def howmany(self, cash: Self):
        """Exchange rate basically"""

        if is_(cash, self):
            return 1
        if cash in self.conversion:
            return self.conversion[cash]
        # find a common currency
        if list(self.conversion)[0] == list(cash.conversion)[0]:
            return (
                self.conversion[list(self.conversion)[0]]
                / cash.conversion[list(cash.conversion)[0]]
            )
        raise ValueError(f'{cash} does not have an exchange rate set {self.name}')
