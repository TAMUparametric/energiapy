"""DataSet is a deterministic data given to account for temporal variability in parameter.
Created when input is a DataFrame
"""
from __future__ import annotations

from dataclasses import dataclass, field
from operator import is_

from pandas import DataFrame
from sympy import IndexedBase

from ..disposition.bound import VarBnd
from ._value import _Value


from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..disposition.index import Index



@dataclass
class Parameter(_Value):
    """Variable data set"""

    value: int| float | list[float] | tuple[list]| tuple[tuple] | tuple[float] | tuple[tuple[list[float]]]= field(default=None)
    index: Index = field(default=None)

    def __post_init__(self):
        self.get_scale()



    def check_scale(self):

        if isinstance(self.value, tuple):
            if len(self.value) != 2:
                raise ValueError("Parameter domain needs a lower and upper bound\nprovide tuple of size 2"):
            for v in self.value:
                return self.check_scale(v)
        
        else: 
            if isinstance(self.value, (int, float)):
                self.value = [self.value]

            if isinstance(self.value, list):
                # value is a list of values
                if len(self.index.scl) != len(self.value):
                    raise ValueError("Scale length does not match the value length")
                
                for v in self.value:
                    return self.check_scale(v)
            
            



        if self.index:
            for i, j in self.index.args().items():
                setattr(self, i, j)
        # This is to check whether the Value types are
        # Constant - int, float
        # M - 'M' or 'm'
        if isinstance(self.value, (int, float, str)):
            self.name = str(self.id[self.index.sym])
        else:
            self.name = str(self.sym)

    @property
    def sym(self):
        """Symbol"""
        # See how name is set
        # We do not want the index in the symbolic names
        # but we want the index in the name
        # index makes the name unique
        # Values are always attached to parameters
        if isinstance(self.value, (int, float, str)):
            return self.id
        else:
            return self.id[self.index.sym]

    def __len__(self):
        if self.index:
            return len(self.index)
        else:
            return 1

    @property
    def id(self):
        """Symbol"""
        return IndexedBase(f'DtSt{self.varbnd.value}{self.spclmt.value}')

    # DataSet are compared on the basis of what bound they are
    def __lt__(self, other):
        if isinstance(other, (int, float)) and is_(self.varbnd, VarBnd.UB):
            return False
        elif isinstance(other, DataSet) and is_(other.varbnd, VarBnd.LB):
            return False
        else:
            return True

    def __gt__(self, other):
        if isinstance(other, (int, float)) and is_(self.varbnd, VarBnd.UB):
            return True
        elif isinstance(other, DataSet) and is_(other.varbnd, VarBnd.LB):
            return True
        else:
            return False
