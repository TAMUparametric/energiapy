"""Calculates the value of a Variable based on the Parent Task
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from dataclasses import dataclass, field
from ._task import _Task
from ...elements.variables.exactvar import ExactVar
from ...elements.constraints.calculate import Calculate
from ...elements.parameters.exactprm import ExactPrm

if TYPE_CHECKING:
    from .bound import Bound


@dataclass
class Calculation(_Task):
    """Calculation Task
    Handles the attributes of components
    Defines strict behaviour

    Attributes:
        var (IsVar): Task Variable
    """

    parent: Bound = field(default=None)

    def __post_init__(self):
        _Task.__post_init__(self)
        self.name = f'Calculation|{self.name}|'

    @staticmethod
    def var():
        """Variable"""
        return ExactVar

    @staticmethod
    def prm():
        """Parameter"""
        return ExactPrm

    @staticmethod
    def cns():
        """Constraint"""
        return Calculate

    def varbirth_attrs(self):
        """Attributes of the Variable"""
        return {'symbol': self.varsym}
