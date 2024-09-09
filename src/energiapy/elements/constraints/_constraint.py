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
        root (IsCmp): Root Component for which information is being defined
        attr (str): Attribute of the Component
        varsym (str): Symbol of the Variable
        prmsym (str): Symbol of the Parameter
    """

    root: IsCmp = field(default=None)
    attr: str = field(default=None)
    varsym: str = field(default=None)
    prmsym: str = field(default=None)

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
