"""
energiapy.TemporalScale - Planning horizon of the problem. 
Also:
    classifies the problem type (design, scheduling, simultaneous)
    determines the scale type (multiscale, single scale)
"""

from dataclasses import dataclass
from itertools import product
from warnings import warn
from typing import List

from .comptype.problem import ProblemType
from .comptype.temporal_scale import ScaleType


@dataclass
class TemporalScale:
    """
    Defines the planning horizon of the problem. The scales for design decisions and scheduling (operational) decisions can be specified.
    A scale is a unique discretization of the temporal planning horizon.

    Based on the definition of the planning horizon. The problem is classified as: 
    (i) A design problem: Includes capacity sizing, facility location, process material mode selection. 
    (ii) A scheduling problem: Includes resource allocation, process operating mode selection. 
    (iii) A simultaneous design and scheduling problem: Does (i) and (ii)simultaneously.

    If the discretization_list has more than one discretization of the planning horizon mentioned, i.e len(discretization_list) > 1, then:
        Either a design or the scheduling scale needs to be mentioned. 

    The function scale_iter is used to generate a tuple of indices. The indices are set as attributes design_index, scheduling_index

    Args:
        discretization_list (list): list of discretization of temporal scale
        design_scale (int, optional): scale level for design decisions. Defaults to None.
        scheduling_scale (int, optional): scale level of scheduling (operational) decisions. Defaults to None.
        start_zero (int): which year the scale starts. Defaults to None.
        scale_factors_max (bool, optional): whether deterministic data factors need to be scaled to max. Defaults to True. Can be set to False or overidden in Factor.
        scale_factors_min_max (bool, optional): whether deterministic data factors need to be scaled min-max. Defaults to None. Can be overidden in Factor.
        scale_factors_standard (bool, optional): whether deterministic data factors need to be standard scaled. Defaults to None. Can be overidden in Factor.

    Examples:

        [1] For a design and scheduling problem where decisions are taken for every day of the week:

        >>> scales = TemporalScale(discretization_list = [7])

        or simply,

        >>> scales = TemporalScale([7])

        scales.design_index = scales.scheduling_index = [(0,), (1,), (2,), (3,), (4,), (5,), (6,)]

        You can also use scales.scale_iter(scale_level = n) to generate an index.

        [2] To define a strictly scheduling problem for a week:

        >>> scales = TemporalScale([7], scheduling_scale = 0)

        [3] If design and scheduling decisions are taken at temporally disparate levels.  

        >>> scales = TemporalScale(discretization_list = [1, 7])

        Here, design_scale defaults to 0, scheduling_scale defaults to 1.

        Checking the index set:

            scales.design_index = [(0,)]

            scales.scheduling_index = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6)]

        Thus the design scale consists of a single index (discretization) '0', and 
        the scheduling scale consists of 7 indices where each is a discretization of the design scale

        [4] In the following example scheduling decisions are taken hourly and design changes are made only once a week

        >>> scales = TemporalScale(discretization_list = [1, 7, 24])

        design_scale defaults to the highest level, i.e. 0. scheduling_scale defaults to the lowest level, i.e. 2.

        Notice that discretizations are done based on the preceding discretization. Thus, the scheduling_scale will have 1 x 7 x 24 = 168 indices.

        On a smaller example:

        >>> scales = TemporalScale(discretization_list = [1, 2, 2]) 

        design_scale defaults to the highest level, i.e. 0. scheduling_scale defaults to the lowest level, i.e. 2.

        The indices for the scheduling scale will be: 
        scales.scheduling_index = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1)]

        [5] The following example represents a planning horizon spanning 5 years, where

        design decisions are taken annually, scheduling (operational) decisions are taken every hour.

        >>> scales = TemporalScale([5, 8760], design_scale=0, scheduling_scale=1)

        This represents a planning horizon with 5 x 8750 = 43800 discretizations

        While two discretization levels, i.e. len(discretization_list) = 2, should suffice for most cases. 

        More discretizations are needed when:

        1. The scale of target demand is different than scheduling and design decisions.
                e.g. When capacity expansion decisions are taken annually, resource allocation is done at an hourly resolution, but demand targets are set for the day.

        >>> scales = TemporalScale([5, 365, 24], design_scale=0, scheduling_scale=2)

        This again, represents a planning horizon with 5 x 365 x 24 = 43800 discretizations. 

        However, scale level 1 (5 x 365 discretizations) can be set as the target_demand_scale while formulating the problem. 

        2. The scale levels for varying data factors, set later at the location level (see energiapy.Location object), are different than your scheduling and design scales
        These factors include:

            demand_factor_scale (int, optional): scale level for demand variance (resource). Defaults to 0
            price_factor_scale (int, optional): scale level for purchase cost variance(resource). Defaults to 0
            capacity_factor_scale (int, optional): scale level for capacity variance(process). Defaults to 0
            expenditure_factor_scale (int, optional): scale level for technology cost variance (process). Defaults to 0
            availability_factor_scale (int, optional): scale level for availability varriance (resource). Defaults to 0
            revenue_factor_scale (int, optional): scale level for revenue varriance (resource). Defaults to 0

        Further varying data factors can also be set for transport (see energiapy.Transport object).

        Take the example where capacity expansion decisions are taken annually, resource allocation is done at an hourly resolution
        but the price of purchasing a certain resource is only updated daily

        The list of indices and the lengths of the indices can be checked using scales.index_list and scales.index_n_list
        In this case, scales.index_n_list = [5, 1825, 43800]

        The price_factor_scale for the particular resource will be set 1 if it has 5 x 365 = 1825 data points.
    """

    discretization_list: list
    design_scale: int = None
    scheduling_scale: int = None
    start_zero: int = None
    scale_factors_max: bool = True
    scale_factors_min_max: bool = None
    scale_factors_standard: bool = None

    def __post_init__(self):
        """
        The Problem and Scale type are set here. 
        """

        self.scale_levels = len(self.discretization_list)
        self.scale = {
            i: list(range(self.discretization_list[i])) for i in range(self.scale_levels)}
        self.list = list(range(len(self.discretization_list)))
        self.name = str(self.list)

        if self.scale_levels > 1:
            self.scale_type = ScaleType.MULTI
        else:
            self.scale_type = ScaleType.SINGLE

        if self.scale_type == ScaleType.SINGLE:

            if (self.design_scale is None) and (self.scheduling_scale is None):
                warn(
                    'Scales set to 0. For strictly scheduling problems, explicitly mention only scheduling_scale = 0.')
                self.scheduling_scale = 0
                self.design_scale = 0

        else:
            if self.design_scale is None:
                self.design_scale = 0
                warn(
                    'The problem is multiscale. Both scales need to be specified. Defaulting design_scale to 0')
            if self.scheduling_scale is None:
                self.scheduling_scale = self.scale_levels - 1
                warn(
                    f'The problem is multiscale. Both scales need to be specified. Defaulting scheduling scale to {self.scale_levels - 1}')

        self.index_list = [self.scale_iter(i)
                           for i in range(self.scale_levels)]  # list with each scale index as a list of tuples

        # length of each scale index
        self.index_n_list = [len(i) for i in self.index_list]

        self.design_index = self.index_list[self.design_scale]

        self.scheduling_index = self.index_list[self.scheduling_scale]

        if self.design_scale is not None:
            if self.scheduling_scale is None:
                self.problem_type = ProblemType.DESIGN
            else:
                self.problem_type = ProblemType.DESIGN_AND_SCHEDULING
        else:
            self.problem_type = ProblemType.SCHEDULING

        if (self.scale_factors_standard is True) or (self.scale_factors_min_max is True):
            self.scale_factors_max = False

    # * -----------------------Class Methods-----------------------------------------
    @classmethod
    def classifications(cls) -> List[str]:
        """All TemporalScale classifications
        """
        return ScaleType.all()

    @classmethod
    def problem_classifications(cls) -> List[str]:
        """All Problem classifications
        """
        return ProblemType.all()

    # * -----------------------Functions---------------------------------------------

    def scale_iter(self, scale_level):
        """Generates a list of tuples as a representation of the scales

        Args:
            scale_level (int): The level of the scale for which to generate.

        Returns:
            List[tuple]: list of tuples with representing the scales
        """
        if scale_level is not None:
            return list(product(*[self.scale[i] for i in self.scale][:scale_level+1]))
        else:
            return None

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
