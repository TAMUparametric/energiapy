"""Commodity Base Class"""

from __future__ import annotations

from collections.abc import Mapping
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
        self, basis: Unit | None = None, label: str = "", citations: str = "", **kwargs
    ):
        self.basis = basis
        _Component.__init__(self, label=label, citations=citations, **kwargs)

        # list of conversions associated with the commodity
        self.conversions: list[Conversion] = []

        # flag indicates whether the commodity is produced and expended insitu only
        self.insitu = False

    @property
    def balance(self) -> dict[Conversion | Self, int | float]:
        """Conversion"""
        # if no conversion is set, return 1.0
        if not self.conversions:
            return {self: 1.0}
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

    def __mul__(self, other: int | float) -> Conversion:
        # multiplying a number with a resources gives conversion
        # math operations with conversions form the balance in tasks
        return Conversion.from_balance({self: other})

    def __rmul__(self, other: int | float) -> Conversion:
        # reverse multiplication
        return self * other

    def __add__(self, other: Conversion | Commodity) -> Conversion:
        return Conversion.from_balance({self: 1, **other})

    def __neg__(self) -> Conversion:
        # just multiply by -1
        return self * -1

    def __sub__(self, other: Conversion | Self):

        if isinstance(other, Commodity):
            # if another resource is subtracted
            # give it the parameter -1
            return self + -1 * other

        def _negate(par):
            if isinstance(par, (int, float)):
                return -1 * par
            return [-i for i in par]

        if isinstance(other, Conversion):
            # if another conversion is subtracted, update the balance

            return Conversion.from_balance(
                {
                    self: 1,
                    **{res: _negate(par) for res, par in other.items()},
                }
            )

    def __truediv__(self, other: int | float):
        # treat division as multiplication by the inverse
        return self * (1 / other)

    def __eq__(self, other: Conversion | Self):
        if isinstance(other, Conversion):
            conv = self + other
            # set itself as base
            conv.resource = self
            return conv

        if isinstance(other, int | float):
            conv = Conversion(resource=self, hold=other)

            return conv

        return super().__eq__(other)

    def __getitem__(self, _):
        return 1

    def __iter__(self):
        return iter([self])

    def __len__(self):
        return 1
