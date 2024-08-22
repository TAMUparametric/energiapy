"""Value of defined Parameters 
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..._core._handy._dunders import _Reprs
from ...disposition.bounds import SpcLmt, VarBnd

if TYPE_CHECKING:
    from ..._core._aliases._is_block import IsDisposition


@dataclass
class _Value(ABC, _Reprs):
    """Value is the input given to a Component

    Args:
        name (str): name of aspect
        disposition (IsDisposition): disposition of the value
        _spclmt (SpcLmt): Whether the value is the start or end of the parametric variable space
        varbnd (VarBnd): Whether the value is exact, or an upper or lower bound
    """

    disposition: IsDisposition = field(default=None)
    varbnd: VarBnd = field(default=None)
    _spclmt: SpcLmt = field(default=None)
    incdntl: bool = field(default=False)

    def __post_init__(self):

        if not self.varbnd:
            # if nothing is specified, then exact. So will make equality constraint
            self.varbnd = VarBnd.EQ

        for i in ['_certainty', '_approach']:
            setattr(self, i, None)

        if self.disposition:
            for i, j in self.disposition.args().items():
                setattr(self, i, j)

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
        if isinstance(self.value, (int, float)):
            # This is only applicable for constants, that return the value as the symbol
            return self.id
        else:
            return self.id[self.disposition.sym]

    @property
    def _bnds(self) -> str:
        """gives the base name for the Data value

        Returns:
            str: some name
        """
        vb_, sl_= ('' for _ in range(2))
        # Variable bound
        if self.varbnd == VarBnd.LB:
            vb_ = '[LB]'
        elif self.varbnd == VarBnd.UB:
            vb_ = '[UB]'

        # Theta space limit
        if self._spclmt == SpcLmt.START:
            sl_ = '[s]'
        elif self._spclmt == SpcLmt.END:
            sl_ = '[e]'

        return f'{vb_}{sl_}'

    def __len__(self):
        if self.disposition:
            return len(self.disposition)
        else:
            return 1
