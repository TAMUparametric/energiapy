"""Inherited Dimension class"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .._core._hash import _Hash

if TYPE_CHECKING:
    from ..represent.model import Model


@dataclass
class _Dimension(_Hash):
    """
    Inherited by components that are a representation of
    some dimension of the model.

    :param model: Model to which the representation belongs.
    :type model: Model

    :ivar name: Name of the dimension, auto generated
    :vartype name: str

    .. note:
        - `name` is generated based on the class and model name.
    """

    # model to which the dimension belongs
    model: Model

    def __post_init__(self):
        # There is only one instance of these
        # so they take their own name
        self.name = rf"{self.__class__.__name__}({self.model})"

    