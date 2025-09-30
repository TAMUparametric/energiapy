"""Resource are:
1. converted by Processes
2. stored by Storage
3. transported by Transits
4. lost by Storage and Transits
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from energia.components.impact.categories import Environ
from energia.components.commodity._commodity import _Commodity
from energia.modeling.variables.default import Free, Inventory, Produce, Trade, Utilize

if TYPE_CHECKING:
    from ...modeling.constraints.calculate import Calculate


@dataclass
class Resource(_Commodity, Trade, Produce, Utilize, Free, Inventory):
    """
    A resource, can be a material, chemical, energy, etc.

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

        # base resource, if any in conversion
        self.inv_of: Resource = None

        # resource in its stored form
        self.in_inv: list[Resource] = []

    @property
    def gwp(self) -> Calculate:
        """Global Warming Potential"""
        if not hasattr(self.model, "GWP"):
            self.model.GWP = Environ(label='Global Warming Potential (kg CO2)')

        return self.consume[self.model.GWP.emit]

    @property
    def htp(self) -> Calculate:
        """Human Toxicity Potential"""
        if not hasattr(self.model, "HTP"):
            self.model.HTP = Environ(label='Human Toxicity Potential (kg 1,4-DB eq.)')

        return self.consume[self.model.HTP.emit]

    @property
    def demand(self) -> Calculate:
        """Demand (alias for the Aspect release)"""
        return self.release

    @property
    def price(self) -> Calculate:
        """Cost of consume"""
        return self.consume[self.model.default_currency().spend]
