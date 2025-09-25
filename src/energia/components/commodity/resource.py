"""Resource are:
1. converted by Processes
2. stored by Storage
3. transported by Transits
4. lost by Storage and Transits
"""

from dataclasses import dataclass
from ._commodity import _Commodity
from ...modeling.variables.default import Free, Inventory, Produce, Trade, Utilize


@dataclass
class Resource(_Commodity, Trade, Produce, Utilize, Free, Inventory):
    """A resource, can be a material, chemical, energy, etc.

    Args:
        label (str): Label of the resource, used for plotting. Defaults to None.
        name (str): Name of the resource, used for indexing. Defaults to None.
        basis (Unit): Unit basis of the resource. Defaults to None.

    Attributes:
        conversions (list[Conv]): List of conversions associated with the resource. Defaults to [].
        stored (Resource): Auxiliary resource in its stored form.
        base (Resource): Base resource, if any in conversion


    """

    def __post_init__(self):
        _Commodity.__post_init__(self)

        # base resource, if any in conversion
        self.inv_of: Resource = None

        # resource in its stored form
        self.in_inv: list[Resource] = []

        # flag indicates whether the resource is produced and expended insitu only
        self.insitu = False

    @property
    def demand(self):
        """Demand"""
        return self.release

    @property
    def price(self):
        """Cost of consume"""
        return self.consume[self.model.default_currency().spend]
