"""Aliases for Components
"""

from typing import TypeAlias

from .isdfn import IsAst, IsDfn
from .isscp import IsScp, IsSptTmp

# Lonely instances with only one instance
IsUnq: TypeAlias = IsScp | IsAst

# Any Component
IsCmp: TypeAlias = IsDfn | IsSptTmp

# Is a tuple of components
# which tells you the disposition of an element
IsDsp: TypeAlias = tuple[IsCmp]
