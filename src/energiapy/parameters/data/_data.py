"""Value of defined Parameters 
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..._core._handy._dunders import _Reprs
from ..bounds import SpcLmt, VarBnd

if TYPE_CHECKING:
    from ..._core._aliases._is_block import IsDisposition


@dataclass
class _Data(ABC, _Reprs):
    """Value is the input given to a Component

    Args:
        name (str): name of aspect
        disposition (IsDisposition): disposition of the value
    """

    disposition: IsDisposition = field(default=None)
    varbnd: VarBnd = field(default=None)
    _spclmt: SpcLmt = field(default=None)
    incdntl: bool = field(default=False)

    def __post_init__(self):

        if not self.varbnd:
            self.varbnd = VarBnd.EXACT

        for i in ['_certainty', '_approach']:
            setattr(self, i, None)

        if self.disposition:
            for i, j in self.disposition.args().items():
                setattr(self, i, j)

        self.name = f'{self._id()}{self._name}'

    @property
    @abstractmethod
    def value(self):
        """reports the value"""

    @staticmethod
    @abstractmethod
    def collection():
        """reports what collection the component belongs to"""

    @staticmethod
    @abstractmethod
    def _id():
        """ID to add to name"""

    @property
    def _name(self) -> str:
        """gives the base name for the Data value

        Returns:
            str: some name
        """
        vb_, sl_, i_ = ('' for _ in range(3))
        if self.varbnd:
            vb_ = self.varbnd.namer()

        if self._spclmt:
            sl_ = self._spclmt.namer()

        if self.incdntl:
            i_ = '*i'

        return f'{self.disposition}{vb_}{sl_}{i_}'

    def __len__(self):
        if self.disposition:
            return len(self.disposition)
        else:
            return 1
