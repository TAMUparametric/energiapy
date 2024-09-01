"""Base for any Traded Component
"""

from dataclasses import dataclass, fields

from .._attrs._bounds import _UsdBounds
from .._attrs._exacts import _UsdExacts
from ._traded import _Traded


@dataclass
class _Used(_UsdBounds, _UsdExacts, _Traded):
    """Applies only for Land and Material
    For now, do not subsume my limitations
    Do whatever you can or want to with energiapy

    Attributes:
        use (IsBnd): bound for use at some spatiotemporal disposition
        cost (IsExt): cost per a unit basis at some spatiotemporal disposition
        emission (IsExt): emission per unit basis of use
    """

    def __post_init__(self):
        _Traded.__post_init__(self)

    @staticmethod
    def inputs():
        """Input attributes"""
        return [f.name for f in fields(_UsdBounds) + fields(_UsdExacts)]
