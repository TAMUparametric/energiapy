from typing import Union

from ._is_block import IsBlock
from ._is_component import IsComponent

IsEpClass = Union[IsBlock, IsComponent]
