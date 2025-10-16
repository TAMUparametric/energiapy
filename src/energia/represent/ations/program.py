"""Program"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from gana.block.program import Prg
from gana.sets.index import I

if TYPE_CHECKING:
    from ..model import Model


@dataclass
class Program(Prg):
    """The mathematical program of the model

    :ivar players: Players index set
    :vartype players: I
    :ivar periods: Periods index set
    :vartype periods: I
    :ivar locations: Locations index set
    :vartype locations: I
    :ivar linkages: Linkages index set
    :vartype linkages: I
    :ivar sources: Sources index set
    :vartype sources: I
    :ivar sinks: Sinks index set
    :vartype sinks: I
    :ivar spaces: Spaces index set
    :vartype spaces: I
    :ivar currencies: Currencies index set
    :vartype currencies: I
    :ivar envs: Environments index set
    :vartype envs: I
    :ivar socs: Societies index set
    :vartype socs: I
    :ivar ecos: Ecosystems index set
    :vartype ecos: I
    :ivar resources: Resources index set
    :vartype resources: I
    :ivar lands: Lands index set
    :vartype lands: I
    :ivar materials: Materials index set
    :vartype materials: I
    :ivar processes: Processes index set
    :vartype processes: I
    :ivar storages: Storages index set
    :vartype storages: I
    :ivar transits: Transits index set
    :vartype transits: I
    :ivar states: States index set
    :vartype states: I
    :ivar controls: Decisions index set
    :vartype controls: I
    :ivar streams: Streams index set
    :vartype streams: I
    :ivar impacts: Consequences index set
    :vartype impacts: I

    .. note::
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
