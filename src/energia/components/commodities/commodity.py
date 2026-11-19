"""Commodity Base Class."""

from __future__ import annotations

from collections.abc import Mapping
from copy import copy
from typing import TYPE_CHECKING, Self

from ..._core._component import _Component
from ...modeling.parameters.conversion import Conversion

if TYPE_CHECKING:
    from ..measure.unit import Unit


class Commodity(_Component, Mapping):
    """
    A commodity, can be a material, chemical, energy, etc.

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
        """Record the unit basis and initialize the commodity's conversion history."""
        self.basis = basis
        _Component.__init__(self, label=label, citations=citations, **kwargs)

        # list of conversions associated with the commodity
        self.conversions: list[Conversion] = []

        # flag indicates whether the commodity is produced and expended insitu only
        self.insitu = False

    @property
    def balance(self) -> dict[Conversion | Self, int | float]:
        """Conversion."""
        # if no conversion is set, return 1.0
        if not self.conversions:
            return {self: 1.0}
        return None
        # if there is a conversion, return its parameter in all tasks its
        # associated with
        # TODO: mute when ready to set conversions on commodity
        # return {task: task.balance[self] for task in self.conversions}

    # TODO: mute when ready to set conversions on commodity
    # def __setattr__(self, name, value):

    #     if isinstance(value, Conversion):
    #         # update conversions
    #         self.conversions.append(value)

    #     super().__setattr__(name, value)

    def __mul__(self, other: float | list[float]) -> Conversion:
        """Create a conversion term with a scalar or per-period coefficient."""
        return Conversion.from_balance({self: copy(other)})

    def __rmul__(self, other: float | list[float]) -> Conversion:
        """Create a conversion term with the coefficient on the left."""
        return self * other

    def __add__(self, other: Conversion | Commodity) -> Conversion:
        """Add the other terms to one unit of this commodity."""
        return (self * 1) + other

    def __neg__(self) -> Conversion:
        """Create a conversion term with a coefficient of minus one."""
        return self * -1

    def __sub__(self, other: Conversion | Commodity) -> Conversion:
        """
        Subtract the other terms from one unit of this commodity.

        .. admonition:: Example

            .. code-block:: python

                from energia import Model, Resource

                m = Model()
                m.heat, m.gas = Resource(), Resource()
                balance = m.heat - 2 * m.gas
                assert balance[m.heat] == 1
                assert balance[m.gas] == -2
        """
        return (self * 1) - other

    def __truediv__(self, other: int | float):
        """Build a conversion with coefficient one divided by the divisor."""
        # treat division as multiplication by the inverse
        return self * (1 / other)

    def __eq__(self, other: Conversion | Self):
        """Use the commodity as the basis of a conversion or attach a numeric coefficient."""
        if isinstance(other, Conversion):
            conv = Conversion.from_balance({self: 1, **other})
            # set itself as base
            conv.resource = self
            return conv

        if isinstance(other, int | float):
            return Conversion(resource=self, hold=other)

        return super().__eq__(other)

    def __getitem__(self, _):
        """Return the unit coefficient used when the commodity is treated as a mapping."""
        return 1

    def __iter__(self):
        """Yield the commodity as the single key of its unit balance."""
        return iter([self])

    def __len__(self):
        """Return one, the number of entries in a single-commodity balance."""
        return 1
