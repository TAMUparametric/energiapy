"""Inherited _Name (reprs) class"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Name:
    """Inherited by components that only have a name
    These do not feature as indices in the model
    nor do they have modeling aspects

    For components with a:
        mathematical program use _Index
        mathematical program and input parameters (modeling aspects) use _Component

    Attributes:
        label (str): Label of the component, used for plotting. Defaults to None.
        name (str): Name of the object. Defaults to ''.

    Note:
        - name is set when the component is made a Model attribute.
    """

    label: str = None

    def __post_init__(self):
        self.name = ''

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
        cls.__repr__ = Name.__repr__
        cls.__hash__ = Name.__hash__
