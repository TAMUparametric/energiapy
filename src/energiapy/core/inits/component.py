# from __future__ import annotations

from dataclasses import dataclass, field

from ...elements.index import Index
from ...funcs.birth.value import birth_value
# from ...funcs.birth.task import birth_task
# from ...funcs.birth.value import birth_value
from ...funcs.check.component import is_named
from .common import CmpCommon, ElmCollect
from .detail import DtlInit

# from typing import TYPE_CHECKING


# if TYPE_CHECKING:
#     from ..type.alias import IsInput, IsTask


@dataclass
class CmpInit(CmpCommon, ElmCollect, DtlInit):
    """Common initial attributes of a component
    named, name, horizon, declared_at, ctypes
    """
    basis: str = field(default=None)
    label: str = field(default=None)

    def __post_init__(self):

        ElmCollect.__post_init__(self)

        for i in ['_named', '_horizon', 'name', ]:
            setattr(self, i, None)
        for i in ['tasks', 'ctypes']:
            setattr(self, i, [])

    def __setattr__(self, name, value):

        if is_named(component=self, attr_input=value):
            print(name, value, 'yes')
            
        super().__setattr__(name, value)
