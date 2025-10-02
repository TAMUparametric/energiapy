"""Energia Constraint Base Class"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..._core._name import _Name

if TYPE_CHECKING:

    from gana.block.program import Prg

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
    from ..variables.control import Control
    from ..variables.impact import Impact
    from ..variables.state import State
    from ..variables.stream import Stream
    from .bind import Bind


@dataclass
class _Generator(_Name):
    """Base class for all Energia constraint generators

    Args:
        aspect (Aspect. optional): Aspect to which the constraint is applied
        domain (Domain. optional): Domain over which the aspect is defined

    Attributes:
        name (str, optional): Name.
        model (Model, optional): Model to which the generator belongs.
        program (Prg, optional): Gana Program to which the generated constraint belongs.


    """

    # this is the aspect for which the constraint is being defined
    aspect: State | Control | Impact | Stream = None
    # the domain is passed when the aspect is called using __call__()
    domain: Domain = None

    # @property
    # def name(self) -> str:
    #     """Name of the constraint"""
    #     return self.aspect.name

    @property
    def model(self) -> Model:
        """Energia Model"""
        return self.aspect.model

    @property
    def program(self) -> Prg:
        """Gana Program"""
        return self.model.program

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

    @property
    def problem(self) -> Problem:
        """Model Tree"""
        return self.model.problem
