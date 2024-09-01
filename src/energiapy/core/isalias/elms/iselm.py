"""Aliases for Program Elements 
"""

from typing import TypeAlias

from ....elements.disposition.index import Index
from .iscns import IsCns
from .isprm import IsPrm
from .isval import IsVal
from .isvar import IsVar

IsElm: TypeAlias = IsCns | IsPrm | IsVar | IsVal | Index
