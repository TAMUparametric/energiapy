"""For unbounded parameters
"""
from dataclasses import dataclass


@dataclass
class Big:
    """A really big number
    Unlike the money in my bank account
    """
    name: str
    bigm: bool = True
    
    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


BigM = Big('BigM')


@dataclass
class CouldBe:
    """Used when a parameter could be a variable
    depending on how the problem is modeled
    """
    name: str
    couldbevar: bool = True 
    
    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


CouldBeVar = CouldBe('CouldBeVar')