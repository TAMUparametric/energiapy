from enum import Enum, auto


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
