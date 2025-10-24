"""Resource are:
1. converted by Processes
2. stored by Storage
3. transported by Transits
4. lost by Storage and Transits
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from energia.components.commodities._commodity import _Commodity
from energia.components.impact.categories import Environ

if TYPE_CHECKING:
    from ...modeling.constraints.calculate import Calculate
    from ..measure.unit import Unit


class Resource(_Commodity):
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

    def __init__(
        self,
        basis: Unit | None = None,
        label: str = "",
        citations: str = "",
        **kwargs,
    ):
        _Commodity.__init__(
            self, basis=basis, label=label, citations=citations, **kwargs
        )

        # base resource, if any in conversion
        self.inv_of: Resource | None = None

    @property
    def gwp(self) -> Calculate:
        """Global Warming Potential"""
        if not hasattr(self.model, "GWP"):
            self.model.GWP = Environ(label="Global Warming Potential (kg CO2)")

        return self.consume[self.model.GWP.emit]

    @property
    def htp(self) -> Calculate:
        """Human Toxicity Potential"""
        if not hasattr(self.model, "HTP"):
            self.model.HTP = Environ(label="Human Toxicity Potential (kg 1,4-DB eq.)")

        return self.consume[self.model.HTP.emit]

    @property
    def price(self) -> Calculate:
        """Cost of consume"""
        return self.consume[self.model._cash().spend]

    def __init_subclass__(cls):
        # the hashing will be inherited by the subclasses
        cls.__repr__ = Resource.__repr__
        cls.__hash__ = Resource.__hash__
