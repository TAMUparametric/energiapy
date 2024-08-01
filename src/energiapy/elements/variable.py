from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..core.inits.common import ElmCommon

from .index import Index

if TYPE_CHECKING:
    from ..type.alias import IsValue


@dataclass
class Variable(ElmCommon):
    value: IsValue

    def __post_init__(self):

        self.index = Index(component=self.component,
                           declared_at=self.declared_at, temporal=self.temporal)
        self.name = f'{self.aspect.vname()}{self.index.name}'
