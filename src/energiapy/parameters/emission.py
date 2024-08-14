"""Defined Emission Parameters 
"""

from dataclasses import dataclass

from ._parameter import _Parameter


@dataclass
class EmitBnd(_Parameter):
    """Bound on Emission"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class ResEmitBuy(_Parameter):
    """Resource Emission Buy"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class ResEmitSell(_Parameter):
    """Resource Emission Sell"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class ResEmitLoss(_Parameter):
    """Resource Emission Loss"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class CmdEmitUse(_Parameter):
    """Commodity Emission Use"""

    def __post_init__(self):
        _Parameter.__post_init__(self)


@dataclass
class OpnEmit(_Parameter):
    """Emission due to setting up operation"""

    def __post_init__(self):
        _Parameter.__post_init__(self)
