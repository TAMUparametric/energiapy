"""Represent

Scenario - set of events we are trying to model 

Program - mathematical representation of the scenario 

Information - data sampled at some spatio temporal disposition 

System - component-based representation of the scenario
"""


class Represent:
    """A Scale - Temporal or Spatial

    Introduces a dimension to the scenario

    Attributes:
        name(str): name of the scale
    """

    def __init__(self, name: str = None):
        self.name = str(name)

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
