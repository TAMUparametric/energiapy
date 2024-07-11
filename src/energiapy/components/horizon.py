from dataclasses import dataclass
from itertools import product
from typing import List
from ..model.type.disposition import TemporalDisp
from .type.horizon import HorizonType
from .temporal_scale import TemporalScale


@dataclass
class Horizon:
    """
    Planning horizon of the problem. 
    Need to specify how many periods the parent scale t0 with 1 discretization is divided into.

    Attributes:
        discretizations (list): divides the horizon into n discretizations. Creates a TemporalScale for each discretization.
        nested (bool, optional): if nested the discretizes based on previous scale. Defaults to True.
        scaling_max (bool, optional): apply max scaling to DataSet. Defaults to None.
        scaling_min_max (bool, optional): apply min max scaling to DataSet. Defaults to None.
        scale_standard (bool, optional): apply standard scaling to DataSet. Defaults to None.
        name (str): name, defined when component is created.
        scales (List[TemporalScale]): list of TemporalScale objects, generated post-initialization.
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
        s.t0, s.t1 are TemporalScale objects with an index attributs. 
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
    # divides the horizon into n discretizations. Creates a TemporalScale
    discretizations: list
    # if nested the discretizes based on previous scale
    nested: bool = True
    # apply scaling
    scaling_max: bool = None
    scaling_min_max: bool = None
    scaling_standard: bool = None

    def __post_init__(self):

        self.name, self.scales = None, list()
        # insert 1 at the beginning, this is the horizon itself
        self.discretizations.insert(0, 1)

        if self.n_scales > 1:
            setattr(self, 'ctype', HorizonType.MULTI)
        else:
            setattr(self, 'ctype', HorizonType.SINGLE)

        for i in range(self.n_scales):
            self.scales.append(TemporalScale(name=TemporalDisp.all()[
                               i].name.lower(), index=self.make_index(postiion=i, nested=self.nested)))

        self.indices = {i: i.index for i in self.scales}

        self.n_indices = [i.n_index for i in self.scales]

    # * ---------Methods-----------------

    @staticmethod
    def ctypes() -> List[HorizonType]:
        """HorizonTypes"""
        return HorizonType.all()

    @staticmethod
    def cname() -> str:
        """Returns class name"""
        return 'Horizon'

    @property
    def n_scales(self) -> int:
        """Returns number of scales"""
        return len(self.discretizations)

    def make_index(self, postiion: int, nested: bool = True):
        """makes an index for TemporalScale"""
        if nested:
            lists = [list(range(i)) for i in self.discretizations]
            return list(product(*lists[:postiion+1]))
        else:
            if not self.discretizations == sorted(self.discretizations):
                raise ValueError(
                    'Discretizations need to be in ascending order')
            if not all(max(self.discretizations) % i == 0 for i in self.discretizations):
                raise ValueError(
                    'Discretizations need to be divisible by the most granular scale')
            lists = [(0, i) for i in range(max(self.discretizations))]
            return lists[::max(self.discretizations)//self.discretizations[postiion]]

    # * ---------Dunders-----------------

    def __repr__(self) -> str:
        return str(self.name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
