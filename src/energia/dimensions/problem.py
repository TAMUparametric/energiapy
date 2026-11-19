"""Decision Tree."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from typing import TYPE_CHECKING, Literal

from .._core._dimension import _Dimension
from ..modeling.indices.domain import Domain
from ..modeling.variables.control import Control

if TYPE_CHECKING:
    from ..modeling.variables.aspect import Aspect
    from ..modeling.variables.states import Consequence, State, Stream
    from .space import Space
    from .time import Time


_ASPECT_COLLECTIONS = ("aspects", "states", "controls", "streams", "consequences")


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
        """Initialize the state, control, stream, and consequence collections."""
        self.states: list[State] = []
        self.controls: list[Control] = []
        self.streams: list[Stream] = []
        self.consequences: list[Consequence] = []
        _Dimension.__post_init__(self)

    @cached_property
    def time(self) -> Time:
        """Time."""
        return self.model.time

    @cached_property
    def space(self) -> Space:
        """Space."""
        return self.model.space

    @property
    def aspects(self) -> list[Consequence | Stream | Control | State]:
        """All Decisions."""
        return self.states + self.controls + self.streams + self.consequences

    @property
    def domains(self) -> list[Domain]:
        """All Domains."""
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
    ) -> dict[Aspect | Domain, list[Aspect | Domain | tuple]]:
        """
        Query the relationships between aspects and their registered domains.

        With an aspect collection as keys and ``values="domains"``, each aspect
        maps to a list of index tuples. With ``keys="domains"``, use a sample's
        ``domain`` to look up the aspects registered for that selection. If both
        arguments are ``"domains"``, each registered domain maps to itself in a list.

        :param keys: Keys to use for the dictionary. Defaults to 'aspects'.
        :type keys: Literal[ 'aspects', 'states', 'controls', 'streams', 'consequences', 'domains' ], optional
        :param values: Values to use for the dictionary. Defaults to 'domains'.
        :type values: Literal[ 'aspects', 'states', 'controls', 'streams', 'consequences', 'domains' ], optional

        :returns: dictionary with particular structure
        :rtype: dict[Aspect | Domain, list[Aspect | Domain | tuple]]

        :raises ValueError: If keys is not one of the allowed values
        """
        # This function will essentially return a dictionary
        # with any choice of keys and values
        # can come very handy
        if keys in _ASPECT_COLLECTIONS:
            keysset: list[Aspect] = getattr(self, keys)

            if values == "domains":
                return {d: [dom.tup for dom in d.domains] for d in keysset if d.domains}
            return {d: getattr(d, values) for d in keysset if getattr(d, values)}

        if keys == "domains":
            return self._values_by_domain(values)

        message = "keys must be one of aspects, states, controls, streams, consequences, domains"
        raise ValueError(message)

    def _values_by_domain(self, values):
        """Group the selected problem values by domain."""
        if values == "domains":
            return {domain: [domain] for domain in self.domains}
        if values not in _ASPECT_COLLECTIONS:
            message = "values must be one of aspects, states, controls, streams, consequences, domains"
            raise ValueError(message)

        by_domain: dict[Domain, list[Aspect]] = {}
        for aspect in getattr(self, values):
            for domain in dict.fromkeys(aspect.domains):
                by_domain.setdefault(domain, []).append(aspect)
        return by_domain
