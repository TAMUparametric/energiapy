"""There are user defined components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

# from ..._core._nirop._error import CacodcarError
from ._component import _Component
from ._consistent import _Consistent
from ..._core._handy._collections import _Values, _Elements


class _DefCol(_Values, _Elements):
    """Defined Collection"""


@dataclass
class _Defined(_Component, _Consistent, _DefCol, ABC):
    """Common initial attributes of components"""

    basis: str = field(default='unit')
    citation: dict = field(default=None)  # TODO - for each attribute make dict
    block: str = field(default=None)
    introduce: str = field(default=None)
    retire: str = field(default=None)
    label: str = field(default=None)

    def __post_init__(self):
        _Component.__post_init__(self)

        self.ctypes = []
        self._consistent = False

        # attrs_task = set(list(taskmaster[self.collection()]))
        # attrs_fields = set([i.name for i in fields(self)])
        # if not attrs_task <= attrs_fields:
        #     print('defined tasks:', attrs_task)
        #     print('component fields:', attrs_fields)
        #     raise CacodcarError(f'{self}: attributes not in fields')

    @staticmethod
    @abstractmethod
    def bounds():
        """Attrs that quantify the bounds of the Component"""

    @classmethod
    @abstractmethod
    def inputs(cls):
        """Attrs"""

    @classmethod
    @abstractmethod
    def _cnst_csh(cls):
        """Adds Cash when making consistent"""

    @classmethod
    @abstractmethod
    def _cnst_lnd(cls):
        """Adds Land when making consistent"""

    @classmethod
    @abstractmethod
    def _cnst_nstd(cls):
        """Is a nested input to be made consistent"""

    @classmethod
    @abstractmethod
    def _cnst_nstd_csh(cls):
        """Is a nested input to be made consistent with Cash"""

    def eqns(self):
        """Prints all equations in the program"""
        for constraint in self.constraints:
            print(constraint.equation)

    def make_consistent(self):
        """Makes the data inputs consistent IsSptTmpDict"""
        for attr in self.inputs():
            value = getattr(self, attr)

            if value is not None:

                if attr in self.bounds():
                    setattr(self, attr, self.make_spttmpdict(value, attr))

                if attr in self._cnst_csh():
                    setattr(
                        self,
                        attr,
                        {self.system.cash: self.make_spttmpdict(value, attr)},
                    )

                if attr in self._cnst_lnd():
                    setattr(
                        self,
                        attr,
                        {self.system.land: self.make_spttmpdict(value, attr)},
                    )

                if attr in self._cnst_nstd():
                    setattr(
                        self,
                        attr,
                        {i: self.make_spttmpdict(j, attr) for i, j in value.items()},
                    )

                if attr in self._cnst_nstd_csh():
                    setattr(
                        self,
                        attr,
                        {
                            i: {self.system.cash: self.make_spttmpdict(j, attr)}
                            for i, j in value.items()
                        },
                    )

        self._consistent = True
