"""Aspect describes the behavior of a component using model elements 
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..core.base import Base
from ..core.onset import EmtCol

if TYPE_CHECKING:
    from ..components.horizon import Horizon
    from ..type.alias import (IsComponent)

@dataclass
class Aspect(EmtCol, Base):
    component: IsComponent = field(default=None)

    def __post_init__(self):
        EmtCol.__post_init__(self)
        self.name = f'{self._name()}({self.component.name})'

    @property
    def _aspected(self):
        """This will be used to check if component attr
        is already defined as an inherited Aspect class
        """
        return True

    @classmethod
    def _name(cls):
        """Gives the name of the Aspect
        """
        return cls.__name__
