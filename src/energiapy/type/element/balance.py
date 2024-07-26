from enum import Enum, auto


class Conv(Enum):
    """Conversion balance
    """
    CONVERSION = auto()
    @classmethod
    def all(cls) -> str:
        """all members of the Enum
        """
        return [i for i in cls]


class MatCons(Enum):
    MATERIAL_CONS = auto()
    """Material balance 
    """
    @classmethod
    def all(cls) -> str:
        """all members of the Enum
        """
        return [i for i in cls]
