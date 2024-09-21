"""Aliases for Program Elements 
"""

from typing import TypeAlias

from ....elements.index import Idx
from .iscns import IsCns
from .isprm import IsPrm
from .isval import IsVal
from .isvar import IsVar

IsElm: TypeAlias = IsCns | IsPrm | IsVar | IsVal | Idx
