from __future__ import annotations

from dataclasses import dataclass
from operator import is_
from typing import TYPE_CHECKING

from ..core.base import Base
from ..core.onset import EmtCol

if TYPE_CHECKING:
    from ..type.alias import IsAspect, IsAspectShared, IsComponent


@dataclass
class AspectShared(EmtCol, Base):
    aspect: IsAspect
    component: IsComponent
    aspects: IsAspectShared

    def __post_init__(self):

        self.name = f'{self.aspect.name.lower()}({self.component.name})'

        for i in ['parameters', 'variables', 'constraints']:
            setattr(
                self, i, [mod for comp in self.aspects for mod in getattr(comp, i) if is_(mod.declared_at, self.component)])
