from typing import Union

from ._is_component import IsComponent
from ._is_model import IsModel

IsEpClass = Union[IsModel, IsComponent]
