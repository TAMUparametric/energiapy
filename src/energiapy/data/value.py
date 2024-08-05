from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...core.inits.common import InpCommon
from .bounds import SpcLmt, VarBnd

if TYPE_CHECKING:
    from ..type.alias import IsCommodity, IsIndex, IsOperation, IsSpatial


@dataclass
class Value(InpCommon):
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
    def _id(self):
        return f'{self.name}{getattr(self,"index","")}'

    def __len__(self):
        return len(self.index)
