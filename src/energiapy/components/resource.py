"""Resource data class
"""

__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2023, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"

from dataclasses import dataclass
from warnings import warn
from enum import Enum, auto
from typing import Union, List


class VaryingResource(Enum):
    """
    Whether the demand or price are varying
    """
    DETERMINISTIC_DEMAND = auto()
    """
    Utilize deterministic demand data as parameters
    """
    DETERMINISTIC_PRICE = auto()
    """
    Utilize deterministic price data as parameters
    """
    DETERMINISTIC_AVAILABILITY = auto()
    """
    Utilize deterministic resource availability as parameters
    """
    DETERMINISTIC_REVENUE = auto()
    """
    Utilize deterministic resource revenues as parameters
    """
    UNCERTAIN_DEMAND = auto()
    """
    Generate uncertainty variables for demand
    """
    UNCERTAIN_PRICE = auto()
    """
    Generate uncertainty variables for price
    """
    UNCERTAIN_AVAILABILITY = auto()
    """
    Generate uncertainty variables for resource availability
    """
    UNCERTAIN_REVENUE = auto()
    """
    Generate uncertainty variables for resource revenue
    """
    CERTAIN_DEMAND = auto()
    """Use exact parameter for demand 
    """
    CERTAIN_PRICE = auto()
    """Use exact parameter for price
    """
    CERTAIN_AVAILABILITY = auto()
    """Use exact parameter for availability
    """
    CERTAIN_REVENUE = auto()
    """Use exact parameter for revenue
    """


@dataclass
class Resource:
    """
    Object with resource data

    Args:
        name (str): Resource ID, long descriptive names can be set with label.
        cons_max (float, optional): Maximum allowed resource consumption in each time period of the scheduling scale. Defaults to 0.
        loss (float, optional): Amount of resource lost in time period of scheduling scale if stored. Defaults to 0.
        revenue (float, optional): Amount earned from sale of resource [$/unit] in each time period of scheduling scale. Defaults to 0.
        price (float, optional): Purchase cost per unit of resource in each time period of scheduling scale [$/unit]. Defaults to 0.
        store_max (float, optional): Maximum allowed storage capacity increase in a year. Defaults to 0.
        store_min (float, optional): Minimum allowed storage capacity increase in a year. Defaults to 0.
        sell (bool, optional): True if resource can be discharged. Defaults to False.
        demand (bool, optional): True, if the process has to meet specific demand. If True, sell defaults to True. Defaults to False.
        basis (str, optional): Unit basis for the resource. Defaults to 'unit'.
        block (Union[str, list, dict], optional): Assign a block for categorization. Defaults to None.
        citation (str, optional): Add citations for data sources. Defaults to 'citation needed'.
        varying (bool, optional): If the cost of resource is varying/uncertain. Defaults to False.
        label (str, optional): Longer descriptive label if required. Defaults to ''.
        gwp (float, optional): Global Warming Potential per unit consumption of resource. Defaults to 0.


    Examples:
        For a resource that cannot be consumed from outside the system.

        >>> H2 = Resource(name='H2', basis='kg', label='Hydrogen', block='Resource')

        For a resource that can be consumed from outside the system, and has a varying purchase price.

        >>> CH4 = Resource(name='CH4', cons_max=1000, price=1, basis='kg', label='Natural gas', varying=  VaryingResource.deterministic_price)

        For a resource that is produced and needs to meet a fixed demand.

        >>> Power = Resource(name='Power', basis='MW', demand = True, label='Power generated', varying = VaryingResource.deterministic_demand)
    """

    name: str
    cons_max: float = 0
    loss: float = 0
    revenue: float = 0
    price: float = 0
    store_max: float = 0
    store_min: float = 0
    sell: bool = False
    demand: bool = False
    basis: str = 'unit'
    block: Union[str, list, dict] = ''
    citation: str = 'citation needed'
    varying: List[VaryingResource] = None
    label: str = ''
    gwp: float = 0

    def __post_init__(self):
        if self.demand is True:
            self.sell = True

        if self.varying is None:
            self.varying = []
            if self.cons_max > 0:
                self.varying = self.varying + \
                    [VaryingResource.CERTAIN_AVAILABILITY,
                        VaryingResource.CERTAIN_PRICE]
            if self.demand is True:
                self.varying = self.varying + \
                    [VaryingResource.CERTAIN_DEMAND]
            if self.revenue is True:
                self.varying = self.varying + \
                    [VaryingResource.CERTAIN_REVENUE]

        if not isinstance(self.varying, list):
            warn('Provide a list of VaryingResource enums')

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
