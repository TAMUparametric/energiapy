"""Resource are:
1. converted by Processes
2. stored by Storage
3. transported by Transits
4. lost by Storage and Transits
"""

from dataclasses import dataclass
from typing import Self

from ...core.component import Component
from ...modeling.parameters.conversion import Conversion
from ...modeling.variables.default import (
    Free,
    Produce,
    Trade,
    Utilize,
    Inventory,
)


@dataclass
class Resource(Component, Trade, Produce, Utilize, Free, Inventory):
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
        # resources are components
        Component.__post_init__(self)

        # base resource, if any in conversion
        self.inv_of: Resource = None

        # resource in its stored form
        self.in_inv: list[Resource] = []

        # list of conversions associated with the resource
        self.conversions: list[Conversion] = []

        # flag indicates whether the resource is produced and expended insitu only
        self.insitu = False

    @property
    def conversion(self) -> dict[Conversion, int | float]:
        """Conversion"""
        # if no conversion is set, return 1.0
        if not self.conversions:
            return {self: 1.0}
        # if there is a conversion, return its parameter in all tasks its
        # associated with
        return {task: task.conversion[self] for task in self.conversions}

    def __setattr__(self, name, value):

        if isinstance(value, Conversion):
            # update conversions
            self.conversions.append(value)

        super().__setattr__(name, value)

    def __mul__(self, other: int | float) -> Conversion:
        # multiplying a number with a resources gives conversion
        # math operations with conversions form the balance in tasks
        conv = Conversion()
        conv.conversion = {self: other}
        return conv

    def __rmul__(self, other: int | float) -> Conversion:
        # reverse multiplication
        return self * other

    def __add__(self, other: Conversion) -> Conversion:
        conv = Conversion()
        if isinstance(other, Resource):
            # if another resource is added, give it the parameter 1
            conv.conversion = {self: 1, other: 1}
            return conv

        # if added with another conversion, updated the balance
        conv.conversion = {self: 1, **other.conversion}
        return conv

    def __neg__(self) -> Conversion:
        # just multiply by -1
        return self * -1

    def __sub__(self, other: Conversion | Self):
        if isinstance(other, Resource):
            # if another resource is subtracted
            # give it the parameter -1
            return self + -1 * other
        if isinstance(other, Conversion):
            # if another conversion is subtracted, update the balance
            conv = Conversion()

            conv.conversion = {
                self: 1,
                **{res: -1 * par if isinstance(par, (int, float)) else [-i for i in par] for res, par in other.conversion.items()},
            }
            return conv

    def __truediv__(self, other: int | float):
        # treat division as multiplication by the inverse
        return self * (1 / other)
