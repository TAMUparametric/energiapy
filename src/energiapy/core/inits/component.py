from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...funcs.birth.task import birth_task
from ...funcs.birth.value import birth_value
from ...funcs.check.named import comp_ready
from .common import CmpCommon, ElmCollect

if TYPE_CHECKING:
    from ..components.temporal.horizon import Horizon
    from ..type.alias import IsInput


@dataclass
class CmpInit(CmpCommon, ElmCollect):
    """Common initial attributes of a component
    named, name, horizon, declared_at, ctypes
    """
    basis: str = field(default=None)
    label: str = field(default=None)
    citation: str = field(default=None)
    block: str = field(default=None)

    def __post_init__(self):

        ElmCollect.__post_init__(self)

        for i in ['_named', 'name', 'horizon']:
            setattr(self, i, None)
        self.ctypes = []
        
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if comp_ready(component=self, attr_input=value):
            birth_value(self, name, value)
            birth_task(self, name, value)
        
        


