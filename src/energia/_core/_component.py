"""Inherited _Component class"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Optional

from gana import I

from ._x import _X

if TYPE_CHECKING:
    from ..components.measure.unit import Unit
    from ..components.spatial.location import Location
    from ..components.temporal.periods import Periods
    from ..dimensions.problem import Problem
    from ..dimensions.space import Space
    from ..dimensions.time import Time


@dataclass
class _Component(_X):
    """
    A component with a mathematical program (hence index in it) and
    input parameters (modeling aspects).

    :param basis: Unit basis of the component. Defaults to None.
    :type basis: Unit, optional
    :param label: Label for the component. Defaults to None.
    :type label: str, optional
    :param captions: Citation for the component. Defaults to None.
    :type captions: str | list[str] | dict[str, str | list[str]], optional

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

    :note:
        - `name`, `model` set when component assigned to Model attribute.
        - `constraints` and `domains` are populated as the program is built.
    """

    # every component has a basis unit
    basis: Optional[Unit] = None

    def __post_init__(self):

        # what differentiates a component from an index is that it has aspects
        # that we can control to adjust their states of existence
        _X.__post_init__(self)

    @property
    def problem(self) -> Problem:
        """Feasible Region"""
        # the decision tree gives the component access to
        # the aspects of all other components
        return self.model.problem

    @property
    def network(self) -> Location:
        """Circumscribing Loc (Spatial Scale)"""
        return self.model.network

    @property
    def horizon(self) -> Periods:
        """Circumscribing Periods (Temporal Scale)"""
        return self.model.horizon

    @property
    def time(self) -> Time:
        """Time"""
        return self.model.time

    @property
    def space(self) -> Space:
        """Space"""
        return self.model.space

    def __getattr__(self, name):

        if self.model:
            # no need to run a hasattr check
            # let it raise an attribute error if not found
            aspect = getattr(self.model, name)
            if callable(aspect):
                return aspect(self)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'",
        )

    @cached_property
    def I(self):
        """gana index set (I)"""
        _index = I(self.name, tag=self.label or '')
        setattr(self.program, self.name, _index)
        return _index
