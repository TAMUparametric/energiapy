from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union
    from ..type.alias import IsComponent, IsOperation, IsSpatial

from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transport import Transit
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..type.alias import (IsAspect, IsCapBound, IsCashFlow, IsEmission,
                          IsEmissionCap, IsLandCap, IsLandUse, IsLife, IsLimit,
                          IsLoss)


class Input:
    """Input attribute of a Component

    Attributes:
        behavior (IsAspect): Aspect of the Input.
        component (IsComponent, Optional): Component to which the Input belongs. Defaults to None.
        operation (IsOperation, Optional): Operation to which Component Input is affiliated. Defaults to None.
        spatial (IsSpatial, Optional): Spatial to which Component Input is affiliated. Defaults to None.
        opn_strict (bool, Optional): If True, Input can only be defined at Operation. Defaults to False.
        spt_strict (bool, Optional): If True, Input can only be defined at Spatial. Defaults to False.
    """

    def __init__(self, component: IsComponent = None):
        self.component = component





class AspInp(Input):
    def __init__(self, behavior: IsAspect = None, operation: IsOperation = None,
                 spatial: IsSpatial = None, opn_strict: bool = False, spt_strict: bool = False):
        self.behavior = behavior
        self.operation = operation
        self.spatial = spatial
        self.opn_strict = opn_strict
        self.spt_strict = spt_strict
        super().__init__(component=component)


class DetInp(Input)


class Limit(AspectInput):
    behavior = IsLimit


class CapBound(AspectInput):
    behavior = IsCapBound


class CashFlow(AspectInput):
    behavior = IsCashFlow


class Emission(AspectInput):
    behavior = IsEmission


class EmissionCap(AspectInput):
    behavior = IsEmissionCap


class LandUse(AspectInput):
    behavior = IsLandUse


class Loss(AspectInput):
    behavior = IsLoss


class Life(AspectInput):
    behavior = IsLife


class LandCap(AspectInput):
    behavior = IsLandCap


class MatUse(Input):
    behavior = IsMatUse


class Conv(Input):
    behavior = IsConv


class Detail(Input):
    behavior = IsDetail
