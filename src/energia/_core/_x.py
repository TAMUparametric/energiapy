"""Inherited _Index class"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING

from ._hash import _Hash

if TYPE_CHECKING:
    from gana import I as Idx
    from gana.block.program import Prg
    from gana.sets.constraint import C

    from ..modeling.indices.domain import Domain
    from ..modeling.variables.aspect import Aspect
    from ..represent.model import Model


class _X(ABC, _Hash):
    """
    A component (`x`) that functions as an index in the mathematical program.

    :param label: An optional label for the component. Defaults to None.
    :type label: str, optional
    :param citations: Citation for the component. Defaults to None.
    :type citations: str, optional

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

    .. note:
        - `name` and `model` are set when the component
           is assigned as a Model attribute.
        - `constraints` and `domains` are populated as the program is built.
    """

    def __init__(
        self,
        label: str = "",
        citations: str = "",
    ):
        self.label = label
        self.citations = citations
        # the model
        self.model: Model | None = None
        # name is given by the model
        self.name: str = ""

        # constraint pnames associated with the component
        self.constraints: list[str] = []
        # domains associated with the component
        self.domains: list[Domain] = []
        # aspects associated with the component with domains
        self.aspects: dict[Aspect, list[Domain]] = {}

    @cached_property
    def program(self) -> Prg:
        """Mathematical program"""
        if self.model is None:
            raise ValueError(f"{type(self)} needs to be assign as Model attribute")
        return self.model.program

    @property
    def cons(self) -> list[C]:
        """Constraints"""
        # this gets the actual constraint objects from the program
        # based on the pname (attribute name) in the program
        return [getattr(self.program, c) for c in self.constraints]

    @property
    @abstractmethod
    def I(self) -> Idx:
        """gana index set"""

    def show(self, descriptive=False, category: str = ""):
        """Pretty print the component"""
        if category:
            for c in self.cons:
                if c.category and c.category == category:
                    c.show(descriptive)

        else:
            for c in self.cons:
                c.show(descriptive)
