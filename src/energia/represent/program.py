"""Program"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from gana.block.program import Prg
from gana.sets.index import I

if TYPE_CHECKING:
    from .model import Model


@dataclass
class Program(Prg):
    """The mathematical program of the model
    Attributes:
        players (I): Players index set
        periods (I): Periods index set
        locations (I): Locations index set
        linkages (I): Linkages index set
        sources (I): Sources index set
        sinks (I): Sinks index set
        spaces (I): Spaces index set
        currencies (I): Currencies index set
        envs (I): Environments index set
        socs (I): Societies index set
        ecos (I): Ecosystems index set
        resources (I): Resources index set
        lands (I): Lands index set
        materials (I): Materials index set
        processes (I): Processes index set
        storages (I): Storages index set
        transits (I): Transits index set
        states (I): States index set
        controls (I): Decisions index set
        streams (I): Streams index set
        impacts (I): Consequences index set

    Note:
        - all the index sets are generated post initialization
    """

    def __post_init__(self):
        Prg.__post_init__(self)
        # Component Index Sets

        self.players = I(mutable=True)
        self.periods = I(mutable=True)
        self.locations = I(mutable=True)
        self.linkages = I(mutable=True)
        self.sources = I(mutable=True)
        self.sinks = I(mutable=True)
        self.spaces = I(mutable=True)
        self.currencies = I(mutable=True)
        self.envs = I(mutable=True)
        self.socs = I(mutable=True)
        self.ecos = I(mutable=True)
        self.resources = I(mutable=True)
        self.lands = I(mutable=True)
        self.materials = I(mutable=True)
        self.processes = I(mutable=True)
        self.storages = I(mutable=True)
        self.transits = I(mutable=True)
        self.states = I(mutable=True)
        self.controls = I(mutable=True)
        self.streams = I(mutable=True)
        self.impacts = I(mutable=True)
