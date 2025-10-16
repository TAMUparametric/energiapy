"""Unit"""

from operator import is_
from typing import Optional, Self

from ..._core._name import _Name


class Unit(_Name):
    """
    Unit of measure for a quantity provided as input to a component

    :param label: Label of the component, used for plotting. Defaults to None.
    :type label: str, optional
    :param basis: Basis of the unit, if defined based on another Unit. Defaults to None.
    :type basis: Unit, optional
    :param times: How many times the basis is contained in the unit. Defaults to None.
    :type times: int | float, optional

    :ivar name: Name of the object. Defaults to ''.
    :vartype name: str
    """

    def __init__(
        self,
        basis: Optional[Self] = None,
        times: Optional[int | float] = None,
        label: Optional[str] = None,
    ):
        # A basis can itself be measured using another basis
        self.basis = basis
        # How many times that basis is self?
        self.times = times

        _Name.__init__(self, label)

    def howmany(self, basis: Self):
        """
        How many times is this basis contained in the other basis

        :param basis: Basis to compare with.
        :type basis: Unit
        """
        # if other Unit is basis of self
        # return the times of self
        if is_(basis, self.basis):
            return self.times

        # if self is the basis of the other Unit
        # return the times of the other Unit
        elif is_(self, basis.basis):
            return basis.times

        # if both have a common basis
        # return the times of self divided by the times of the other Unit
        elif is_(self.basis, basis.basis):
            return self.times / basis.times

        # if no common basis is found
        # raise an error
        raise ValueError(
            f"{self} and {basis} do not have a common basis for comparison",
        )

    def __truediv__(self, other: float):
        # can only be divided by a number
        # if dividing by another Unit
        # return the times of self divided by the times of the other Unit
        if isinstance(other, Unit):
            return self.howmany(other)

        # if dividing by a number
        # create a new Unit
        elif isinstance(other, (int, float)):
            # is self has a basis Unit
            # define new Unit based on the basis of self
            if self.basis:
                b = Unit(
                    self.basis,
                    1 / (other * self.times),
                    f"{self.label}/{other*self.times}",
                )
            # if self has no basis Unit
            # define new Unit using self as basis
            else:
                b = Unit(self, 1 / other, f"{self.label}/{other}")
                self.basis = b
                self.times = other
            return b

    def __mul__(self, other: float):
        # can only be multiplied by a number
        if not isinstance(other, (int, float)):
            raise TypeError(f"Cannot multiply Unit by {type(other)}")

        # if multiplying by a number
        # create a new Unit

        # if self has a basis Unit
        # define new Unit based on the basis of self
        if self.basis:
            b = Unit(self.basis, other * self.times, f"{self.label}.{other*self.times}")
        # if self has no basis Unit
        # define new Unit using self as basis
        else:
            b = Unit(self, other, f"{self.label}.{other}")
            self.basis = b
            self.times = 1 / other
        return b

    def __rmul__(self, other: float):
        return self * other
