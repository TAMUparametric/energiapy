from enum import Enum, auto
from typing import List


class ProblemType(Enum):
    """Problem type
    """
    DESIGN = auto()
    """Only design decisions are taken 
    """
    SCHEDULING = auto()
    """Only scheduling decisions are taken 
    """
    DESIGN_AND_SCHEDULING = auto()
    """Design and scheduling decisions are taken simultaneously 
    """

    @classmethod
    def all(cls) -> List[str]:
        """All Problem classifications
        """
        return [i.name for i in cls]
