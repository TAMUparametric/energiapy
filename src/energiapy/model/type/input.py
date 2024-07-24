from enum import Enum

from .aspect import CashFlow, Emission, Land, Life, Limit, Loss, CapBound
from .balance import Conv, MatCons
from .detail import Detail


class Input(Enum):
    """What kind of behaviour does the parameter describe
    All of these have subclasses
    These are predetermined by me, Rahul Kakodkar. 
    The BDFO of energiapy
    """
    LIMIT = Limit
    """Helps create boundaries for the problem 
    by setting a min/max or Exact limit for flow of Resource.
    """
    CASHFLOW = CashFlow
    """Expenditure/Revenue.
    """
    LAND = Land
    """Describes land use and such
    """
    EMISSION = Emission
    """Is an emission.
    """
    LIFE = Life
    """Describes earliest introduction, retirement, lifetime and such
    """
    LOSS = Loss
    """Amount lost during storage or transport
    """
    CAPBOUND = CapBound
    """How much of the capacity can be accessed
    """
    DETAIL = Detail
    """Provides some detail regarding Component
    """
    CONVERSION = Conv
    """
    """
    MATERIAL_CONS = MatCons

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum
        """
        return 'Input'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum
        """
        return [i.value for i in cls]

    @classmethod
    def matches(cls) -> dict:
        d_ = {i: [j.name.lower() for j in i.all()] for i in cls.all()}
        return {k: getattr(i, k.upper()) for i, j in d_.items() for k in j}

    @classmethod
    def inputs(cls) -> list:
        return list(cls.matches())

    @classmethod
    def match(cls, value: str):
        if value in cls.matches():
            return cls.matches()[value]
        else:
            return 'Monkey killing, monkey killing monkey over pieces of the ground. Silly monkeys give them thumbs they make a club to beat their brother down. How theyve survived so misguided is a mystery, Repugnant is a creature who would squander the ability to lift an eye to heaven, conscious of his fleeting time here'
