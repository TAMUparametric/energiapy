"""Rate input attributes for Components
"""

from dataclasses import dataclass, field, fields

from ...core.isalias.inps.isinp import IsExt


@dataclass
class _SetupRate:
    """Rate of Construction of Operation"""


@dataclass
class _OperateRate:
    """Rate of Operation of Operation"""



class _RateAttrs:
    """Exact input attributes for Components"""

    @staticmethod
    def rates():
        """Rates"""
        return [f.name for f in fields(_SetupRate) + fields(_OperateRate)]
