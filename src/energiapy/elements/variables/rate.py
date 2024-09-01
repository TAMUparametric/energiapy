"""Rate Task
"""

from dataclasses import dataclass

from sympy import IndexedBase

from ..disposition.structure import make_structures
from ._variable import _ExactVar


@dataclass
class Rate(_ExactVar):
    """Rate"""
