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
            self.varbnd = VarBnd.EXACT

        for i in ['_certainty', '_approach']:
            setattr(self, i, None)

        if self.disposition:
            for i, j in self.disposition.args().items():
                setattr(self, i, j)

        self.name = f'{self.vid}{self.disposition}'

    @property
    @abstractmethod
    def value(self):
        """reports the value"""

    @staticmethod
    @abstractmethod
    def _id():
        """ID to add to name"""

    @property
    def vid(self):
        """ID to add to name"""
        return self._id() + self._bnds

    @property
    def _bnds(self) -> str:
        """gives the base name for the Data value

        Returns:
            str: some name
        """
        vb_, sl_, i_ = ('' for _ in range(3))

        # Variable bound
        if self.varbnd == VarBnd.LOWER:
            vb_ = '[LB]'
        elif self.varbnd == VarBnd.UPPER:
            vb_ = '[UB]'

        # Theta space limit
        if self._spclmt == SpcLmt.START:
            sl_ = '[s]'
        elif self._spclmt == SpcLmt.END:
            sl_ = '[e]'

        # Incidental
        if self.incdntl:
            i_ = '[i]'

        return f'{vb_}{sl_}{i_}'

    def __len__(self):
        if self.disposition:
            return len(self.disposition)
        else:
            return 1