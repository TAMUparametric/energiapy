"""Reporting Variable"""

from .aspect import Aspect


class Report:
    """A variable that reports the value of a state or impact"""

    aspect: Aspect

    def __post_init__(self):
        self.name = f"x_{self.aspect}"

        self.model = self.aspect.model

        self.program = self.model.program

        self.problem = self.model.problem

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
