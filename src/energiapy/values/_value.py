from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._core._aliases._is_block import IsDisposition


@dataclass
class _Value(ABC):
    """Value is the input given to a Component

    Args:
        name (str): name of aspect
        disposition (IsDisposition): disposition of the value
    """

    name: str = field(default=None)
    disposition: IsDisposition = field(default=None)

    def __post_init__(self):
        for i in ['_varbound', '_spclimit', '_certainty', '_approach']:
            setattr(self, i, None)

        if self.disposition:
            for i, j in self.disposition.args().items():
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
        return f'{self.name}{self.disposition}'

    def __len__(self):
        return len(self.disposition)
