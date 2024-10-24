"""Aliases for Defined Components
"""

from typing import TypeAlias

from ....analytical.player import Player
from ....components.commodity.cash import Cash
from ....components.commodity.emission import Emission
from ....components.commodity.land import Land
from ....components.commodity.resource import Resource
from ....components.operation.process import Process
from ....components.operation.storage import Storage
from ....components.operation.transit import Transit

# Analytical
IsAly: TypeAlias = Player

# Commodities
IsImp: TypeAlias = Emission
IsTrd: TypeAlias = Resource
IsUsd: TypeAlias = Land | Resource
IsAst: TypeAlias = Cash | Land
IsCmd: TypeAlias = Emission | Resource | Cash | Land

# Operational
IsOpn: TypeAlias = Process | Storage | Transit

# These have multiple instances
# constraints are generated based on the data provided to these components
IsDfn: TypeAlias = IsAly | IsCmd | IsOpn