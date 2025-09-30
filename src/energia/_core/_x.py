"""Inherited _Index class"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from gana.sets.index import I

if TYPE_CHECKING:
    from gana.block.program import Prg
    from gana.sets.constraint import C

    from ..modeling.indices.domain import Domain
    from ..modeling.variables.aspect import Aspect
    from ..represent.model import Model


@dataclass
class _X:
    """
    A component (`x`) that functions as an index in the mathematical program.

    :param label: An optional label for the component. Defaults to None.
    :type label: str, optional
    :param captions: An optional citation or description for the component. Defaults to None.
    :type captions: str | list[str] | dict[str, str | list[str]], optional

    :ivar model: The model to which the component belongs.
    :vartype model: Model
    :ivar name: Set when the component is assigned as a Model attribute.
    :vartype name: str
    :ivar _indexed: True if an index set has been created.
    :vartype _indexed: bool
    :ivar constraints: List of constraints associated with the component.
    :vartype constraints: list[str]
    :ivar domains: List of domains associated with the component.
    :vartype domains: list[Domain]
    :ivar aspects: Aspects associated with the component with domains.
    :vartype aspects: dict[Aspect, list[Domain]]

    :note:
        - `name` and `model` are set when the component is assigned as a Model attribute.
        - `_indexed` is set the first time the model is indexed.
        - `constraints` and `domains` are populated as the program is built.
    """

    label: Optional[str] = None
    citations: Optional[str] = None

    def __post_init__(self):
        # the model
        self.model: Model = None
        # name is given by the model
        self.name: str = ''
        # is the component indexed?
        self._indexed: bool = False
        # constraint pnames associated with the component
        self.constraints: list[str] = []
        # domains associated with the component
        self.domains: list[Domain] = []
        # aspects associated with the component with domains
        self.aspects: dict[Aspect, list[Domain]] = {}

    @property
    def program(self) -> Prg:
        """Mathematical program"""
        return self.model.program

    @property
    def I(self) -> I:
        """gana index set (I)"""
        if not self._indexed:
            # and index element is created for each component
            # with the same name as the component
            # A SELF type set is created
            setattr(self.program, self.name, I(self.name, tag=self.label))
            self._indexed = True
        # if already indexed, return the index set from the program
        return getattr(self.program, self.name)

    @property
    def cons(self) -> list[C]:
        """Constraints"""
        # this gets the actual constraint objects from the program
        # based on the pname (attribute name) in the program
        return [getattr(self.program, c) for c in self.constraints]

    def show(self, descriptive=False):
        """Pretty print the component"""
        for c in self.cons:
            c.show(descriptive)

    # The reprs are set independently without inheriting _Name
    # which allows a distinction between _Name and _Index when assigned to Model

    # -----------------------------------------------------
    #                    Hashing
    # -----------------------------------------------------

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __init_subclass__(cls):
        # the hashing will be inherited by the subclasses
        cls.__repr__ = _X.__repr__
        cls.__hash__ = _X.__hash__
