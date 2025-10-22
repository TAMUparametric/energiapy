"""Decision Tree"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from typing import TYPE_CHECKING, Literal

from .._core._dimension import _Dimension
from ..modeling.indices.domain import Domain
from ..modeling.variables.control import Control
from ..modeling.variables.states import Consequence, State, Stream

if TYPE_CHECKING:
    from ..modeling.variables.aspect import Aspect
    from .space import Space
    from .time import Time


@dataclass
class Problem(_Dimension):
    """
    Aspect (Decision) Tree.

    All the aspects are attached to this object.

    :param model: Model to which the representation belongs.
    :type model: Model

    :ivar name: Name of the dimension, generated based on the class and model name.
    :vartype name: str
    :ivar controls: List of controls. Defaults to empty list.
    :vartype controls: list[Decision]
    :ivar streams: List of streams. Defaults to empty list.
    :vartype streams: list[Stream]
    :ivar consequences: List of consequences. Defaults to empty list.
    :vartype consequences: list[Impact]
    :ivar players: List of players. Defaults to empty list.
    :vartype players: list[Player]

    .. note::
        - name is generated based on Model name
        - controls, streams, consequences, and players are populated as model is defined
    """

    def __post_init__(self):

        self.states: list[State] = []
        self.controls: list[Control] = []
        self.streams: list[Stream] = []
        self.consequences: list[Consequence] = []
        _Dimension.__post_init__(self)

    @cached_property
    def time(self) -> Time:
        """Time"""
        return self.model.time

    @cached_property
    def space(self) -> Space:
        """Space"""
        return self.model.space

    @property
    def aspects(self) -> list[Consequence | Stream | Control | State]:
        """All Decisions"""
        return self.states + self.controls + self.streams + self.consequences

    @property
    def domains(self) -> list[Domain]:
        """All Domains"""
        return list(set(chain.from_iterable(d.domains for d in self.aspects)))

    def get(
        self,
        keys: Literal[
            "aspects",
            "states",
            "controls",
            "streams",
            "consequences",
            "domains",
        ] = "aspects",
        values: Literal[
            "aspects",
            "states",
            "controls",
            "streams",
            "consequences",
            "domains",
        ] = "domains",
    ) -> dict[Aspect | Domain, list[Aspect | Domain]]:
        """Get a dictionary of the tree with a particular structure

        :param keys: Keys to use for the dictionary. Defaults to 'aspects'.
        :type keys: Literal[ 'aspects', 'states', 'controls', 'streams', 'consequences', 'domains' ], optional
        :param values: Values to use for the dictionary. Defaults to 'domains'.
        :type values: Literal[ 'aspects', 'states', 'controls', 'streams', 'consequences', 'domains' ], optional

        :returns: dictionary with particular structure
        :rtype: dict[Aspect | Domain, list[Aspect | Domain]]

        :raises ValueError: If keys is not one of the allowed values
        """
        # This function will essentially return a dictionary
        # with any choice of keys and values
        # can come very handy
        if keys in ["aspects", "states", "controls", "streams", "consequences"]:
            keysset: list[Aspect] = getattr(self, keys)

            if values == "domains":
                return {d: [dom.tup for dom in d.domains] for d in keysset if d.domains}
            else:
                return {d: getattr(d, values) for d in keysset if getattr(d, values)}

        if keys in ["domains"]:
            dict_ = {d: [] for d in self.domains}

            for dom in self.domains:
                for val in self.get(keys=values, values=keys):
                    if dom in self.get(keys=values, values=keys)[val]:
                        dict_[dom].append(val)
            return {k.tup: v for k, v in dict_.items() if v}

        raise ValueError(
            "keys must be one of aspects, states, controls, streams, consequences, domains",
        )
