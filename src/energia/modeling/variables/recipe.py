"""Recipes to create Aspects"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Type

from .aspect import Aspect

if TYPE_CHECKING:
    from ..._core._component import _Component


@dataclass
class Recipe:
    """
    Recipe to create Aspects

    :param name: Name of the aspect
    :type name: str
    :param kind: Kind of aspect, e.g., Aspect, Control, etc.
    :type kind: Type[Aspect]
    :param primary_type: Primary type(s) of component the aspect can be applied to
    :type primary_type: tuple[Type[_Component]] | Type[_Component]
    :param label: Label for plotting. Defaults to "".
    :type label: str
    :param add: Add string for constraints. Defaults to "".
    :type add: str
    :param sub: Subtract string for constraints. Defaults to "".
    :type sub: str
    :param bound: Bound string for constraints. Defaults to "".
    :type bound: str
    :param ctrl: Control string for constraints. Defaults to "".
    :type ctrl: str
    :param ispos: If the aspect is positive. Defaults to True.
    :type ispos: bool
    :param nn: If the aspect is non-negative. Defaults to True.
    :type nn: bool
    :param latex: LaTeX representation. Defaults to "".
    :type latex: str

    :ivar args: Arguments for aspect creation.
    :vartype args: dict[str, Any]
    """

    name: str
    kind: Type[Aspect]
    primary_type: tuple[Type[_Component]] | Type[_Component]
    label: str = ""
    add: str = ""
    sub: str = ""
    bound: str = ""
    ctrl: str = ""
    ispos: bool = True
    nn: bool = True
    latex: str = ""

    def __post_init__(self):
        self.args = {
            k: v
            for k, v in asdict(self).items()
            if k not in ("name", "kind") and (isinstance(v, bool) or v)
        }

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
