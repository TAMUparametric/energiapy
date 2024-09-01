"""Constraint to calculate Variable. There is usually a parent Variable associated"""

from dataclasses import dataclass, field

from ...core.isalias.elms.isprm import IsPrm
from ...core.isalias.elms.isvar import IsVar
from ..disposition.bound import VarBnd
from ._constraint import _Constraint


@dataclass
class Calculate(_Constraint):
    """Calculates; transactions, emissions, etc."""

    varbnd: VarBnd = field(default=None)
    parent: IsVar = field(default=None)
    parameter: IsPrm = field(default=None)

    def __post_init__(self):
        _Constraint.__post_init__(self)

        # calculations always have an equality sign
        self.birth_equation(eq='==', par=self.parameter, prn=self.parent)
