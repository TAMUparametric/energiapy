from dataclasses import dataclass
# from typing import TYPE_CHECKING, Dict, List, Tuple, Union

# from ..model.specialparams.conversion import Conversion
# from .resource import Resource
# from ..model.specialparams.dataset import DataSet
# from ..model.specialparams.theta import Theta
# from ..model.specialparams.unbound import BigM
# from ..model.type.input import Input
from ..component import Component

# if TYPE_CHECKING:
#     from pandas import DataFrame
#     from .horizon import Horizon
#     from .material import Material
#     from ..type.alias import


@dataclass
class Storage(Component):
    pass
# store: Resource
#     capacity: IsLimit
#     land_use: IsLand = field(default=None)
#     material_cons: IsMatCons = field(default=None)
