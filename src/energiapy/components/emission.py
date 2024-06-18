from dataclasses import dataclass


@dataclass
class Emission:
    """
    Class 
    """

    name: str 

    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name

