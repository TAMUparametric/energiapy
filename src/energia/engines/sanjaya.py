"""Event Logger"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from .._core._hash import _Hash

if TYPE_CHECKING:
    from ..components import (Aspect, Commodity, Domain, Linkage, Location,
                              Modes, Periods, Process, Resource, Sample,
                              Storage, Transport)
    from ..represent.model import Model

class Sanjaya:
    """Sanjaya Event Logger"""

    def __init__(self, model: Model):
        self.time = model.time
        self.space = model.space
        self.model = model

        # * General Resource Balances
        self.balances: dict[
            Commodity,
            dict[Location | Linkage, dict[Periods, list[Aspect]]],
        ] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        # Dictionary which tells you what aspects of what component
        # have been bound at what location and time

        # * Sample Dispositions
        self.dispositions: dict[
            Aspect,
            dict[
                Commodity | Process | Storage | Transport,
                dict[Location | Linkage, dict[Periods, list[Aspect]]],
            ],
        ] = {}

        # * Drawn Maps
        self.maps: dict[Aspect, dict[Domain, dict[str, list[Domain]]]] = {}
        self.maps_report: dict[Aspect, dict[Domain, dict[str, list[Domain]]]] = {}

        # * Generated Modes
        self.modes_dict: dict[Sample, Modes] = {}

        # * Conversion Matrix
        self.convmatrix: dict[Process, dict[Resource, int | float | list]] = {}

    def see(self, aspect: Aspect, domain: Domain, )