"""Aliases for Components
"""

from .isdfn import IsAst, IsDfn
from .isscp import IsScp, IsSptTmp

# Lonely instances with only one instance
type IsUnq = IsScp | IsAst

# Any Component
type IsCmp = IsDfn | IsSptTmp

# Is a tuple of components
# which tells you the disposition of an element
type IsDsp = tuple[IsCmp]
