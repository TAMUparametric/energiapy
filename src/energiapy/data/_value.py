from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._core._aliases._is_element import IsIndex


@dataclass
class _Value(ABC):
    """Value is the input given to a Component

    Args:
        name (str): name of aspect
        index (IsIndex): index of the value
    """

    name: str = field(default=None)
    index: IsIndex = field(default=None)

    def __post_init__(self):
        for i in ['_varbound', '_spclimit', '_certainty', '_approach']:
            setattr(self, i, None)

        if self.index:
            for i, j in self.index.args.items():
                setattr(self, i, j)

        vb_, sl_ = '', ''
        if getattr(self, '_varbound', None):
            vb_ = getattr(self, '_varbound').namer()

        if getattr(self, '_spclimit', None):
            sl_ = getattr(self, '_spclimit').namer()

        self.name = f'{self.name}{vb_}{sl_}'

    @property
    @abstractmethod
    def value(self):
        """reports the value"""

    @property
    def _id(self):
        return f'{self.name}{getattr(self,"index","")}'

    def __len__(self):
        return len(self.index)
