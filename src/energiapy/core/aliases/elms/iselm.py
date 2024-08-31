"""Aliases for Program Elements 
"""

from ....elements.dispositions.index import Index
from .iscns import IsCns
from .isprm import IsPrm
from .isval import IsVal
from .isvar import IsVar

type IsElm = IsCns | IsPrm | IsVar | IsVal | Index
