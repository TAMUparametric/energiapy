from enum import Enum, auto


class Detail(Enum):
    """Provides some detail regarding Component"""

    BASIS = auto()
    """Base units 
    """
    BLOCK = auto()
    """Block to which the Component belongs
    """
    LABEL = auto()
    """Used as tag while generating plots
    """
    CITATION = auto()
    """Provide any citations if needed 
    """

    @staticmethod
    def tname() -> str:
        """Returns the name of the Enum"""
        return 'Detail'

    @classmethod
    def all(cls) -> str:
        """all members of the Enum"""
        return [i for i in cls]
