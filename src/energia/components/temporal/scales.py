"""Temporal Scales"""

# from itertools import accumulate
# from operator import mul


class TemporalScales:
    """A temporal scale for a model."""

    def __init__(self, discretizations: list[int], names: list[str] = None):

        # self.discretization_list = list(accumulate(discretization_list, mul))
        self.discretizations = discretizations
        self.names = names if names else [f't{i}' for i in discretizations]
