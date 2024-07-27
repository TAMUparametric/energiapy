from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..core.base import Dunders, Magics
from .index import Index

if TYPE_CHECKING:
    from ..type.alias import IsAspect, IsComponent, IsDeclaredAt, IsTemporal


@dataclass(kw_only=True)
class Variable(Dunders, Magics):
    aspect: IsAspect
    component: IsComponent
    declared_at: IsDeclaredAt
    temporal: IsTemporal

    def __post_init__(self):

        self.index = Index(component=self.component,
                           declared_at=self.declared_at, temporal=self.temporal)
        self.name = f'{self.aspect.vname()}{self.index.name}'
