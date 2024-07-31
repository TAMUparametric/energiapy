from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from .bound import VarBnd, SpcLmt

from ..core.base import Dunders

if TYPE_CHECKING:
    from ..type.alias import (IsCommodity, IsDerived, IsOperation,
                              IsSpatial, IsIndex)


@dataclass
class Value(Dunders):
    """Value is the input given to a Component

    Args:
        name (str): name of aspect
        varbound (Bound): variable bound [UPPER, LOWER, EXACT, FREE, PARAMETRIC]
        spclimit (Bound): limit of parameteric space [START, END]
        value (IsInput): input value
        index (IsIndex): index of the value
        derived (IsDerived, optional): Derived Commodity. Defaults to None.
        commodity (IsCommmodity, optional): Commodity. Defaults to None.
        operation (IsOperation, optional): Operation. Defaults to None.
        spatial (IsSpatial, optional): Spatial. Defaults to None.
    """
    name: str = field(default=None)
    varbound: VarBnd = field(default=None)
    spclimit: SpcLmt = field(default=None)
    index: IsIndex = field(default=None)
    derived: IsDerived = field(default=None)
    commodity: IsCommodity = field(default=None)
    operation: IsOperation = field(default=None)
    spatial: IsSpatial = field(default=None)

    @property
    def _id(self):
        return f'{self.name}{self.varbound.namer()}{self.index.name}'

    def __len__(self):
        return len(self.index)
