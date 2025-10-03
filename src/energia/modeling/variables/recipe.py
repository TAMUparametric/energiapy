"""Recipes to create Aspects"""

from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Type, TYPE_CHECKING

from .aspect import Aspect

if TYPE_CHECKING:
    from ..._core._component import _Component


@dataclass
class Recipe:
    """Recipe to create Aspects"""

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
