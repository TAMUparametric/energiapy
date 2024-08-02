from dataclasses import dataclass

from .variable import Variable


@dataclass
class Acquired(Variable):
    """Acquire Land for Operation
    """
    
    
    @staticmethod
    def _commodity():
        return Land
    
    @staticmethod
    def _operations():
        return Process, Storage, Transit 
    
    @staticmethod
    def _spatial():
        return Location
    