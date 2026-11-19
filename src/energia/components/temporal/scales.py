"""Temporal Scales."""


class TemporalScales:
    """
    A temporal scale for a model.

    :param discretizations: List of discretizations for the temporal scale.
    :type discretizations: list[int]
    :param names: Names of the discretizations. Defaults to [t<i>] for each discretization.
    :type names: list[str], optional

    .. admonition:: Example

        .. code-block:: python

            from energia import Model, TemporalScales

            m = Model()
            m.scales = TemporalScales([1, 365, 24], ["year", "day", "hour"])
            assert m.day.howmany(m.hour) == 24
            assert m.year.howmany(m.day) == 365
    """

    def __init__(self, discretizations: list[int], names: list[str] | None = None):
        """Store discretizations and use their sizes to generate names when names are omitted."""
        # self.discretization_list = list(accumulate(discretization_list, mul))
        self.discretizations = discretizations
        self.names = names if names else [f"t{i}" for i in discretizations]
