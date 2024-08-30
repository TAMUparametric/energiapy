from typing import Union

from .isblk import IsBlock
from .iscmp import IsCmp

IsEpClass = Union[IsBlock, IsCmp]
