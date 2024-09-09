"""Task, for Component attributes
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

from ...core._handy._dunders import _Dunders
from ...core._handy._printers import _EasyPrint
from ...core.isalias.cmps.iscmp import IsCmp

if TYPE_CHECKING:
    from ...elements.constraints.rules._rule import _Rule
    from ...elements.parameters._parameter import _Parameter
    from ...elements.variables._variable import _Variable


@dataclass
class _Constraint(_Dunders, _EasyPrint, ABC):
    """Constraints define strict behavior
    between variables and parameters

    Attributes:
        var (IsVar): Task Variable
    """

    root: IsCmp = field(default=None)
    attr: str = field(default=None)

    @property
    def varsym(self):
        """Variable Symbol"""
        return self._varsym

    @varsym.setter
    def varsym(self, value):
        self._varsym = value

    @property
    def prmsym(self):
        """Parameter Symbol"""
        return self._parsym

    @prmsym.setter
    def prmsym(self, value):
        self._parsym = value

    @property
    def name(self):
        """Name"""
        return f'{self.cname()}|{self.attr}|'

    @staticmethod
    @abstractmethod
    def var() -> _Variable:
        """Variable"""

    @staticmethod
    @abstractmethod
    def prm() -> _Parameter:
        """Parameter"""

    @staticmethod
    @abstractmethod
    def rule() -> _Rule:
        """Constraint Rule"""

    @property
    @abstractmethod
    def varbirth_attrs(self) -> dict:
        """Attributes of the Variable"""
