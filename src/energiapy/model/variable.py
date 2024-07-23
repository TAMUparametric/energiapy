from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .index import Index

if TYPE_CHECKING:
    from .type.aliases import IsAspect, IsComponent, IsDeclaredAt, IsTemporal


@dataclass
class Variable:
    aspect: IsAspect
    component: IsComponent
    declared_at: IsDeclaredAt
    temporal: IsTemporal
    
    def __post_init__(self):

        self.index = Index(component=self.component,
                           declared_at=self.declared_at, temporal=self.temporal)
        self.name = f'{self.aspect.vnamer()}{self.index.name}'

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
