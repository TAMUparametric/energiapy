"""Inherited _Name (reprs) class"""

from __future__ import annotations

from dataclasses import dataclass

from typing import Optional


@dataclass
class _Name:
    """
    Inherited by components that only have a name.

    These do not feature as indices in the model
    nor do they have modeling aspects.

    For components with a:
        - mathematical program, use `X`
        - mathematical program and input parameters (modeling aspects), use `Component`

    :param label: Label of the component, used for plotting. Defaults to None.
    :type label: str, optional

    :ivar name: Name of the object. Defaults to ''.
    :vartype name: str

    :note:
        - `name` is set when the component is made a Model attribute.
    """

    label: Optional[str] = None

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
        cls.__repr__ = _Name.__repr__
        cls.__hash__ = _Name.__hash__
