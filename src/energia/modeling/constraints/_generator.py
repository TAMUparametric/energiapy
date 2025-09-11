"""Energia Constraint Base Class"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core.name import Name

if TYPE_CHECKING:

    from gana.block.program import Prg

    from ...components.commodity.resource import Resource
    from ...components.operation.process import Process
    from ...components.operation.storage import Storage
    from ...components.operation.transport import Transport
    from ...components.spatial.linkage import Link
    from ...components.spatial.location import Location
    from ...components.temporal.period import Period
    from ...core.x import X
    from ...dimensions.decisiontree import DecisionTree
    from ...represent.model import Model
    from .bind import Bind
    from ..indices.domain import Domain
    from ..variables.aspect import Aspect
    from ..variables.state import State
    from ..variables.control import Control
    from ..variables.impact import Impact
    from ..variables.stream import Stream


@dataclass
class _Generator(Name):
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

    @property
    def name(self) -> str:
        """Name of the constraint"""
        return self.aspect.name

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
            dict[Location | Link, dict[Period]],
        ],
    ]:
        """Nested dictionary describing the disposition of each Aspect"""
        return self.model.dispositions

    @property
    def grb(
        self,
    ) -> dict[
        Resource | Process | Storage | Transport,
        dict[Location, dict[Period | Link, list[Bind]]],
    ]:
        """List of Bind at each disposition"""
        return self.model.grb

    @property
    def tree(self) -> DecisionTree:
        """Model Tree"""
        return self.model.tree
