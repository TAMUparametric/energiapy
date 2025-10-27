"""Event Logger"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from .._core._hash import _Hash

if TYPE_CHECKING:
    from ..components.commodities.commodity import Commodity
    from ..components.commodities.resource import Resource
    from ..components.operations.process import Process
    from ..components.operations.storage import Storage
    from ..components.operations.transport import Transport
    from ..components.spatial.linkage import Linkage
    from ..components.spatial.location import Location
    from ..components.temporal.modes import Modes
    from ..components.temporal.periods import Periods
    from ..modeling.indices.domain import Domain
    from ..modeling.variables.aspect import Aspect
    from ..modeling.variables.sample import Sample
    from ..represent.model import Model
  

class Sanjaya(_Hash):
    """Sanjaya Event Logger"""

    def __init__(self, model: Model):
        self.name = "Sanjaya"

        self.model = model

        # scope of the problem
        self.time = self.model.time
        self.space = self.model.space

        self.modes_dict = model.modes_dict
        self.convmatrix = model.convmatrix
    
        # * General Resource Balances
        self.balances: dict[
            Commodity,
            dict[Location | Linkage, dict[Periods, list[Aspect]]],
        ] = self.model.balances
        # Dictionary which tells you what aspects of what component
        # have been bound at what location and time

        # * Sample Dispositions
        self.dispositions: dict[
            Aspect,
            dict[
                Commodity | Process | Storage | Transport,
                dict[Location | Linkage, dict[Periods, list[Aspect]]],
            ],
        ] = self.model.dispositions

        # * Drawn Maps
        self.maps: dict[Aspect, dict[Domain, dict[str, list[Domain]]]] = self.model.maps
        self.maps_report: dict[Aspect, dict[Domain, dict[str, list[Domain]]]] = self.model.maps_report
        
        # * Generated Modes
        self.modes_dict: dict[Sample, Modes] = self.model.modes_dict

        # * Conversion Matrix
        self.convmatrix: dict[Process, dict[Resource, int | float | list]] = self.model.convmatrix

    def see(self, aspect: Aspect, domain: Domain)
        
        