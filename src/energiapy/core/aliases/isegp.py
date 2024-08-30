from typing import Union

from .isblk import IsBlock
from .iscmp import IsComponent

IsEpClass = Union[IsBlock, IsComponent]
