"""Value of defined Parameters 
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...core._handy._dunders import _Reprs
from ..disposition.bound import SpcLmt, VarBnd

if TYPE_CHECKING:
    from ..disposition.index import Index


@dataclass
class _Value(ABC, _Reprs):
    """Value is the input given to a Component

    Args:
        name (str): name of aspect
        index (Index): index of the value
        spclmt (SpcLmt): Whether the value is the start or end of the parametric variable space
        varbnd (VarBnd): Whether the value is exact, or an upper or lower bound
    """

    index: Index = field(default=None)
    varbnd: VarBnd = field(default=None)
    spclmt: SpcLmt = field(default=None)
    incdntl: bool = field(default=False)

    def __post_init__(self):

        if not self.varbnd:
            # if nothing is specified, then exact. So will make equality constraint
            self.varbnd = VarBnd.EQ

        if not self.spclmt:
            self.spclmt = SpcLmt.NOT

        for i in ['_certainty', '_approach']:
            setattr(self, i, None)

        if self.index:
            for i, j in self.index.args().items():
                setattr(self, i, j)
        # This is to check whether the Value types are
        # Constant - int, float
        # M - 'M' or 'm'
        if isinstance(self.value, (int, float, str)):
            self.name = str(self.id[self.index.sym])
        else:
            self.name = str(self.sym)

    @property
    @abstractmethod
    def value(self):
        """reports the value"""

    @property
    @abstractmethod
    def id(self):
        """reports the value"""

    @property
    def sym(self):
        """Symbol"""
        # See how name is set
        # We do not want the index in the symbolic names
        # but we want the index in the name
        # index makes the name unique
        # Values are always attached to parameters
        if isinstance(self.value, (int, float, str)):
            return self.id
        else:
            return self.id[self.index.sym]

    def __len__(self):
        if self.index:
            return len(self.index)
        else:
            return 1
