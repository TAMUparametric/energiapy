"""Temporal Scales"""


class TemporalScales:
    """
    A temporal scale for a model.

    :param discretizations: List of discretizations for the temporal scale.
    :type discretizations: list[int]
    :param names: Names of the discretizations. Defaults to [t<i>] for each discretization.
    :type names: list[str], optional
    """

    def __init__(self, discretizations: list[int], names: list[str] | None = None):

        # self.discretization_list = list(accumulate(discretization_list, mul))
        self.discretizations = discretizations
        self.names = names if names else [f"t{i}" for i in discretizations]
