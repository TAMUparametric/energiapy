from enum import Enum, auto


class BalanceMixin:
    """Mixin for Balance Enums"""

    @staticmethod
    def iname() -> str:
        """Returns the name of the Enum"""
        return 'Balance'

    @classmethod
    def all(cls) -> str:
        """All members of the Enum"""
        return [i for i in cls]


class Conv(BalanceMixin, Enum):
    """Fixed conversion balance for resource in Process"""

    CONVERSION = auto()


class MatUse(BalanceMixin, Enum):
    """Fixed material balance for material in Operations"""

    MATERIAL_USE = auto()
