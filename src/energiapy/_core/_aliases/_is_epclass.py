from typing import Union

from ._is_component import IsComponent
from ._is_block import IsBlock

IsEpClass = Union[IsBlock, IsComponent]
