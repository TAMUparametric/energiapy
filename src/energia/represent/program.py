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

    model: Model = None

    def __post_init__(self):
        Prg.__post_init__(self)

        # Component Index Sets
        self.name = f"Program({self.model})"

    def __getattr__(self, item):

        if item in self.model.dimension_map:
            index = I(mutable=True)
            setattr(self, item, index)
            return index
        raise AttributeError(
            f"{self} has no '{item}'",
        )
