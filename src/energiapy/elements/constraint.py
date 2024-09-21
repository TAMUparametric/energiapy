"""General Constraint Class
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from sympy import Rel
from ..core._handy._dunders import _Reprs
from .index import Idx

if TYPE_CHECKING:
    from .expression import Exn
    from .parameter import Prm
    from .variable import Vrb


@dataclass
class Cns(_Reprs):
    """Constraint gives the relationship between Parameters, Variables, or Expressions"""

    lhs: Exn | Prm | Vrb = field()
    rhs: Exn | Prm | Vrb = field()
    rel: str = field(default='eq')
    index: Idx = field(default=None)
    name: str = field(default='Cns')
