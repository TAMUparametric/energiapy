from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._core._handy._dunders import _Reprs
from ._bounds import _SpcLmt, _VarBnd

if TYPE_CHECKING:
    from .._core._aliases._is_block import IsDisposition


@dataclass
class _Value(ABC, _Reprs):
    """Value is the input given to a Component

    Args:
        name (str): name of aspect
        disposition (IsDisposition): disposition of the value
    """

    disposition: IsDisposition = field(default=None)
    _varbnd: _VarBnd = field(default=None)
    _spclmt: _SpcLmt = field(default=None)

    def __post_init__(self):
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
        vb_, sl_ = '', ''
        if self._varbnd:
            vb_ = self._varbnd.namer()

        if self._spclmt:
            sl_ = self._spclmt.namer()

        return f'{self.disposition}{vb_}{sl_}'

    def __len__(self):
        return len(self.disposition)
