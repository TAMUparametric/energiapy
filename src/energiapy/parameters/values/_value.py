"""Value of defined Parameters 
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...core._handy._dunders import _Reprs
from ...indices.bounds import SpcLmt, VarBnd

if TYPE_CHECKING:
    from ...core.aliases.is_block import IsDisposition
    from ...core.aliases.is_value import IsSpcLmt, IsVarBnd


@dataclass
class _Value(ABC, _Reprs):
    """Value is the input given to a Component

    Args:
        name (str): name of aspect
        disposition (IsDisposition): disposition of the value
        spclmt (SpcLmt): Whether the value is the start or end of the parametric variable space
        varbnd (VarBnd): Whether the value is exact, or an upper or lower bound
    """

    disposition: IsDisposition = field(default=None)
    varbnd: IsVarBnd = field(default=None)
    spclmt: IsSpcLmt = field(default=None)
    incdntl: bool = field(default=False)

    def __post_init__(self):

        if not self.varbnd:
            # if nothing is specified, then exact. So will make equality constraint
            self.varbnd = VarBnd.EQ

        if not self.spclmt:
            self.spclmt = SpcLmt.NOT

        for i in ['_certainty', '_approach']:
            setattr(self, i, None)

        if self.disposition:
            for i, j in self.disposition.args().items():
                setattr(self, i, j)
        # This is to check whether the Value types are
        # Constant - int, float
        # M - 'M' or 'm'
        if isinstance(self.value, (int, float, str)):
            self.name = str(self.id[self.disposition.sym])
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
        # We do not want the disposition in the symbolic names
        # but we want the disposition in the name
        # disposition makes the name unique
        # Values are always attached to parameters
        if isinstance(self.value, (int, float, str)):
            return self.id
        else:
            return self.id[self.disposition.sym]

    def __len__(self):
        if self.disposition:
            return len(self.disposition)
        else:
            return 1
