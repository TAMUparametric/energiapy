"""Defined Calculative Parameters 
"""

from dataclasses import dataclass

from ._parameter import _Parameter


@dataclass
class CmdUse(_Parameter):
    """Commodity Use"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class ResLoss(_Parameter):
    """Resource Loss"""

    def __post_init__(self):
        _Parameter.__post_init__(self)
