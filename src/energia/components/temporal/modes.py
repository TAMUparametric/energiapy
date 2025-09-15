"""Operational Mode attached to a Parameter"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from gana.sets.index import I
from ...core.x import X

if TYPE_CHECKING:
    from ...modeling.indices.domain import Domain
    from ...modeling.variables.aspect import Aspect
    from ...modeling.constraints.bind import Bind
    from ...represent.model import Model
    from gana.block.program import Prg


@dataclass
class Modes(X):
    """Represents a discrete choice to be taken within a
    spatiotemporal disposition.
    Modes can split you
    Mode of Operation, can be used for Conversion, Use, etc.

    Attributes:
        name (str, float, int]): The name of the mode, usually a number.
    """

    n_modes: int = 1
    bind: Bind = None

    def __post_init__(self):
        X.__post_init__(self)

        self.name = f'modes({self.bind})'

    @property
    def I(self) -> I:
        """Index set of modes"""
        if not self._indexed:
            # and index element is created for each component
            # with the same name as the component
            # A SELF type set is created
            setattr(
                self.program,
                self.name,
                I(size=self.n_modes, tag=f'Modes of {self.bind.aspect}'),
            )
            self._indexed = True
        # if already indexed, return the index set from the program
        return getattr(self.program, self.name)
