"""General Constraint Class
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from sympy import Rel
from ..core._handy._dunders import _Reprs
from .disposition.index import Index

if TYPE_CHECKING:
    from .exn import Exn
    from .prm import Prm
    from .vrb import Vrb


@dataclass
class Cns(_Reprs):
    """Constraint gives the relationship between Parameters, Variables, or Expressions"""

    lhs: Exn | Prm | Vrb = field()
    rhs: Exn | Prm | Vrb = field()
    rel: str = field(default='eq')
    index: Index = field(default=None)
    name: str = field(default='Cns')
