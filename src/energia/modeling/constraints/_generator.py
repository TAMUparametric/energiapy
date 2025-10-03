"""Energia Constraint Base Class"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING


if TYPE_CHECKING:

    from gana import Prg

    from ...components.commodity.resource import Resource
    from ...components.operation.process import Process
    from ...components.operation.storage import Storage
    from ...components.operation.transport import Transport
    from ...components.spatial.linkage import Linkage
    from ...components.spatial.location import Location
    from ...components.temporal.periods import Periods
    from ...dimensions.problem import Problem
    from ...represent.model import Model
    from ..indices.domain import Domain
    from ..variables.aspect import Aspect
    from .bind import Bind


@dataclass
class _Generator:
    """
    Base class for all Energia constraint generators.

    :param aspect: Aspect to which the constraint is applied.
    :type aspect: Aspect | None
    :param domain: Domain over which the aspect is defined.
    :type domain: Domain | None

    :ivar name: Name of the generator.
    :vartype name: str | None
    :ivar model: Model to which the generator belongs.
    :vartype model: Model | None
    :ivar program: Gana Program to which the generated constraint belongs.
    :vartype program: Prg | None
    """

    # this is the aspect for which the constraint is being defined
    aspect: Aspect
    # the domain is passed when the aspect is called using __call__()
    domain: Domain

    label: str = ""

    # @property
    # def name(self) -> str:
    #     """Name of the constraint"""
    #     return self.aspect.name

    @cached_property
    def model(self) -> Model:
        """Energia Model"""
        return self.aspect.model

    @cached_property
    def program(self) -> Prg:
        """Gana Program"""
        return self.model.program

    @cached_property
    def problem(self) -> Problem:
        """Model Tree"""
        return self.model.problem

    @property
    def domains(self) -> list[Domain]:
        """Returns the domains over which the aspect has been defined"""
        return self.aspect.domains

    @property
    def dispositions(self) -> dict[
        Aspect,
        dict[
            Resource | Process | Storage | Transport,
            dict[Location | Linkage, dict[Periods]],
        ],
    ]:
        """Nested dictionary describing the disposition of each Aspect"""
        return self.model.dispositions

    @property
    def grb(
        self,
    ) -> dict[
        Resource | Process | Storage | Transport,
        dict[Location, dict[Periods | Linkage, list[Bind]]],
    ]:
        """List of Bind at each disposition"""
        return self.model.grb

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __init_subclass__(cls):
        cls.__repr__ = _Generator.__repr__
        cls.__hash__ = _Generator.__hash__
