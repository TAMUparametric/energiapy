"""Horizon is the planning period of the problem
"""

from dataclasses import dataclass, field
from itertools import product
from operator import imod, is_, is_not

from ...types.component.horizon import HorizonType
from ...types.element.disposition import TemporalDisp
from .._initialize._component import _ScopeComponent
from .scale import Scale


@dataclass
class Horizon(_ScopeComponent):
    """
    Planning horizon of the problem.
    Need to specify how many periods the parent scale t0 with 1 discretization is divided into.

    Input:
        discretizations (list): divides the horizon into n discretizations. Creates a Scale for each discretization.
        nested (bool, optional): if nested the discretizes based on previous scale. Defaults to True.
        scaling_max (bool, optional): apply max scaling to DataSet. Defaults to None.
        scaling_min_max (bool, optional): apply min max scaling to DataSet. Defaults to None.
        scale_standard (bool, optional): apply standard scaling to DataSet. Defaults to None.
        name (str): name, defined when component is created.
        scales (List[Scale]): list of Scale objects, generated post-initialization.
        n_scales (int): number of scales, generated post-initialization.
        indices (dict): dictionary of indices, generated post-initialization.
        n_indices (list): list of number of indices, generated post-initialization.

    Examples:

        Import required components:
        >>> from energiapy.components import Scenario, Horizon

        A system must be created first:
        >>> s = Scenario(name='pse')

        The planning horizon of the problem can be declared as follows:
        >>> s.h = Horizon(discretizations=[4])

        This creates two scales, t0 and t1, with 1 and 4 discretizations respectively.
        >>> s.h.scales
        [t0, t1]
        s.t0, s.t1 are Scale objects with an index attributs.
        t0 always represents the entire planning horizon, and tn represents the nth scale of the horizon.

        Consider the example where you want to consider 2 years, with 4 quarters each year.

        If nested is True, which is the default:
        >>> s.h = Horizon(discretizations=[2, 4])
        >>> s.t0.index,
        [(0,)]
        >>> s.t1.index
        [(0, 0), (0, 1)]
        >>> s.t2.index
        [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 0, 3), (0, 1, 0), (0, 1, 1), (0, 1, 2), (0, 1, 3)]

        If nested is False:
        The total number of discretizations for each scale must be provided in ascending order,
        and must be divisible by the most granular scals.
        >>> s.h = Horizon(discretizations=[2, 8], nested=False)
        >>> s.t0.index,
        [(0,0)]
        >>> s.t1.index
        [(0, 0), (0, 4)]
        >>> s.t2.index
        [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)]

        so for a 365 days and 24 hours, the following can be done:
        either
        >>> s.h = Horizon(discretizations=[365, 24])
        or
        >>> s.h = Horizon(discretizations=[365, 8760], nested=False)

    """

    # divides the horizon into n discretizations. Creates a Scale
    discretizations: list = field(default_factory=list)
    # if nested the discretizes based on previous scale
    nested: bool = field(default=True)

    def __post_init__(self):
        _ScopeComponent.__post_init__(self)
        self.scales = []

        # # insert 1 at the beginning, this is the horizon itself
        self.discretizations.insert(0, 1)

        self.ctypes.append(
            HorizonType.MULTISCALE if self.n_scales > 1 else HorizonType.SINGLESCALE
        )
        self.ctypes.append(HorizonType.NESTED if self.nested else HorizonType.UNNESTED)

        for i in range(self.n_scales):
            self.add(
                Scale(
                    name=TemporalDisp.all()[i].name.lower(),
                    index=self.make_index(position=i, nested=self.nested),
                )
            )

        self.indices = {i: i.index for i in self.scales}

        self.n_indices = [i.n_index for i in self.scales]

    def make_index(self, position: int, nested: bool = True):
        """makes an index for Scale"""
        if nested:
            lists = [list(range(i)) for i in self.discretizations]
            return list(product(*lists[: position + 1]))
        else:
            if is_not(self.discretizations, sorted(self.discretizations)):
                raise ValueError('Discretizations need to be in ascending order')
            if not all(
                is_(imod(max(self.discretizations), i), 0) for i in self.discretizations
            ):
                raise ValueError(
                    'Discretizations need to be divisible by the most granular scale'
                )
            lists = [(0, i) for i in range(max(self.discretizations))]
            return lists[:: max(self.discretizations) // self.discretizations[position]]

    @property
    def n_scales(self) -> int:
        """Returns number of scales"""
        return len(self.discretizations)

    @property
    def collection(self):
        """The collection in scenario"""
        return 'horizon'
