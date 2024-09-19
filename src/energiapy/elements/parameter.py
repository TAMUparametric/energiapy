"""A Paramter
"""

from dataclasses import dataclass, field
from typing import Self

from sympy import IndexedBase, Symbol

from .index import Index
from .m import M
from ..core._handy._dunders import _Reprs
from .expression import Exn
from .constraint import Cns


@dataclass
class Prm(_Reprs):
    """A parameter with some value/values

    Attributes:
        value (IsValue): The value of the parameter. Can be numeric, M, Theta
        index (Index): index of the Prm

    """

    value: int | float | list | bool
    index: Index = field(default=None)
    lb: bool = field(default=False)
    ub: bool = field(default=False)
    name: str = field(default='Prm')

    def __post_init__(self):

        if self.lb and self.ub:
            raise ValueError('Parameter cannot be both a lower and upper bound')

        if self.lb:
            tag = '^LB'

        if self.ub:
            tag = '^UB'

        # if no lower bound or upper bound is provided, the parameter is treated as a constant
        if not self.lb and not self.ub:
            self.ex = True
            tag = ''
        else:
            self.ex = False

        self.name = f'{self.name}{tag}'.capitalize()

        # if single value, put in list
        if not isinstance(self.value, list):
            self.value = [self.value]

        # declare big Ms and Thetas (multiparametric variables)
        for i, v in enumerate(self.value):
            if isinstance(v, bool) and v is True:
                self.value[i] = M(big=True)

    @property
    def sym(self) -> IndexedBase:
        """symbolic representation"""
        if self.index:
            return IndexedBase(self.name)[self.index.sym]
        else:
            return Symbol(self.name)

    def args(self):
        """Returns the non-value arguments of the Prm"""
        return {'index': self.index, 'lb': self.lb, 'ub': self.ub}

    def __len__(self):
        return len(self.value)

    def __neg__(self):

        return Prm([-i for i in self.value], **self.args())

    def __pos__(self):
        return Prm([+i for i in self.value], **self.args())

    def __abs__(self):
        return Prm([abs(i) for i in self.value], **self.args())

    def __invert__(self):
        return Prm([~i for i in self.value], **self.args())

    def __add__(self, other: Self):

        if isinstance(other, Prm):
            return Prm([i + j for i, j in zip(self.value, other.value)], **self.args())
        else:
            return Exn(one=self, two=other, rel='+')

    def __sub__(self, other: Self):
        if isinstance(other, Prm):
            return Prm([i - j for i, j in zip(self.value, other.value)], **self.args())
        else:
            return Exn(one=self, two=other, rel='-')

    def __mul__(self, other: Self):
        if isinstance(other, Prm):
            return Prm([i * j for i, j in zip(self.value, other.value)], **self.args())
        else:
            return Exn(one=self, two=other, rel='*')

    def __truediv__(self, other: Self):
        if isinstance(other, Prm):
            return Prm([i / j for i, j in zip(self.value, other.value)], **self.args())
        else:
            return Exn(one=self, two=other, rel='/')

    def __floordiv__(self, other: Self):

        return Prm([i // j for i, j in zip(self.value, other.value)], **self.args())

    def __mod__(self, other: Self):

        return Prm([i % j for i, j in zip(self.value, other.value)], **self.args())

    def __pow__(self, other: Self):

        return Prm([i**j for i, j in zip(self.value, other.value)], **self.args())

    def __eq__(self, other: Self):

        if isinstance(other, Prm):
            check = list({i == j for i, j in zip(self.value, other.value)})
            print(check)
            if len(check) == 1 and check[0] is True:
                return True
            else:
                return False

        else:
            return Cns(lhs=self, rhs=other, rel='eq')

    def __le__(self, other: Self):

        if isinstance(other, Prm):
            check = [i <= j for i, j in zip(self.value, other.value)]
            if all(check):
                return True
            else:
                return False

        else:
            return Cns(lhs=self, rhs=other, rel='leq')

    def __ge__(self, other: Self):
        if isinstance(other, Prm):
            return not self <= other
        else:
            return Cns(lhs=self, rhs=other, rel='geq')

    def __lt__(self, other: Self):

        if isinstance(other, Prm):
            check = [i < j for i, j in zip(self.value, other.value)]
            if all(check):
                return True
            else:
                return False

        else:
            return self <= other

    def __ne__(self, other: Self):
        if isinstance(other, Prm):
            return not self == other
        else:
            raise TypeError(
                f"unsupported operand type(s) for !=: 'Prm' and '{type(other)}'"
            )

    def __gt__(self, other: Self):
        if isinstance(other, Prm):
            return not self < other
        else:
            return self >= other
