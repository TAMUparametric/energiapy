"""Planning Horizon of the problem
"""

from dataclasses import dataclass, field
from itertools import product
from operator import imod, is_

from ...core._report._syst import _Scls
from ...core.isalias.cmps.isdfn import IsDfn
from ...core.nirop.errors import NoScaleMatchError
from .._base._scope import _Scope


@dataclass
class Horizon(_Scope, _Scls):
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
        scales (list[Scale]): list of Scale objects, generated post-initialization.
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

    discretizations: list = field(default_factory=list)
    # if nested the discretizes based on previous scale
    nested: bool = field(default=False)
    label_scales: list[str] = field(default=None)
    label: str = field(default=None)

    def __post_init__(self):
        _Scope.__post_init__(self)

        # insert 1 at the beginning, this is the horizon itself
        if isinstance(self.discretizations, dict):
            self._discretization_list = list(self.discretizations.values())
            self._discretization_list.insert(0, 1)
            self.name_scales = list(self.discretizations.keys())
            self.name_scales.insert(0, 'ph')

        elif isinstance(self.discretizations, list):
            self._discretization_list = list(self.discretizations)
            self._discretization_list.insert(0, 1)
            self.name_scales = [f't{i}' for i in range(len(self._discretization_list))]

        else:
            raise ValueError('Discretizations must be a list or a dictionary')

    @property
    def n_scales(self) -> int:
        """Returns number of scales"""
        return len(self._discretization_list)

    @property
    def indices(self):
        """Dictionary of indices"""
        return {i: i.index for i in self.scales}

    @property
    def n_indices(self):
        """list of number of indices"""
        return [len(i) for i in self.scales]

    @property
    def is_multiscale(self):
        """Returns True if problem has multiple scales"""
        # Note that the first scale is always the planning horizon
        if self.n_scales > 2:
            return True
        else:
            return False

    @property
    def is_nested(self):
        """Returns True if problem has nested scales"""
        if self.nested:
            return True
        else:
            return False

    @property
    def root(self):
        """Returns the root scale"""
        return self.scales[0]

    def make_index(self, position: int, nested: bool = True):
        """makes an index for Scale"""
        lists = [list(range(i)) for i in self._discretization_list]
        if nested:
            return list(product(*lists[: position + 1]))
        else:
            return [(0, i) for i in lists[position]]

    def match_scale(self, value, component: IsDfn = None, attr: str = None):
        """Returns the scale that matches the length

        Args:
            value: data value to match
            component: Component
            attr: attribute to match

        """
        if hasattr(value, '__len__'):
            if len(value) not in self.n_indices:
                raise NoScaleMatchError(value, component, attr)
            return self.scales[self.n_indices.index(len(value))]
        else:
            return self.scales[0]