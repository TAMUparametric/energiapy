"""Inherited Dimension class"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..represent.model import Model


@dataclass
class Dimension:
    """Inherited by components that are a representation of
    some dimension of the model.

    Attributes:
        model (Model): Model to which the representation belongs.
        name (str): Name of the model. Defaults to None.

    Note:
        - name is generated based on the Class and Model name
    """

    # model to which the dimension belongs
    model: Model

    def __post_init__(self):
        # There is only one instance of these, so they take their own name
        self.name = rf'{self.__class__.__name__}({self.model})'

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
        cls.__repr__ = Dimension.__repr__
        cls.__hash__ = Dimension.__hash__
