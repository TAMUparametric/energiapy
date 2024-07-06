"""For unbounded parameters
"""
from dataclasses import dataclass
from .type.special import SpecialParameter

@dataclass(frozen=True)
class Big:
    """A really big number
    Unlike the money in my bank account
    """
    name: str
    special = SpecialParameter.BIGM
    
    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


BigM = Big('BigM')

@dataclass(frozen=True)
class Small:
    """Small like my expectations
    """
    name: str
    special = SpecialParameter.BIGM

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


SmallM = Small('smallm')


