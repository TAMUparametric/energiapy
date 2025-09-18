"""Decision Tree"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from ..components.game.player import Player
from ..core.dimension import Dimension
from ..modeling.indices.domain import Domain
from ..modeling.variables.control import Control
from ..modeling.variables.impact import Impact
from ..modeling.variables.state import State
from ..modeling.variables.stream import Stream

if TYPE_CHECKING:
    from ..components.operation.process import Process
    from ..components.operation.storage import Storage
    from ..components.operation.transport import Transport
    from ..components.spatial.linkage import Linkage
    from ..components.spatial.location import Location
    from ..components.temporal.period import Period
    from ..modeling.variables.aspect import Aspect
    from .space import Space
    from .time import Time


@dataclass
class DecisionTree(Dimension):
    """Aspect (Decision) Tree

    All the aspects are attached to this object

    Attributes:
        model (Model): Model to which the Feasible Region belongs.
        name (str): Name of the Feasible Region. Defaults to None.
        controls (list[Decision]): List of controls. Defaults to empty list.
        streams (list[Stream]): List of streams. Defaults to empty list.
        impacts (list[Impact]): List of consequences. Defaults to empty list.
        players (list[Player]): List of players. Defaults to empty list.

    Note:
        - name is generated based on Model name
        - controls, streams, impacts, and players are populated as model is defined
    """

    def __post_init__(self):

        Dimension.__post_init__(self)
        self.states: list[State] = []
        self.controls: list[Control] = []
        self.streams: list[Stream] = []
        self.impacts: list[Impact] = []
        self.players: list[Player] = []


    @property
    def time(self) -> Time:
        """Time"""
        return self.model.time

    @property
    def space(self) -> Space:
        """Space"""
        return self.model.space

    @property
    def aspects(self) -> list[Impact | Stream | Control | State]:
        """All Decisions"""
        return self.states + self.controls + self.streams + self.impacts

    @property
    def domains(self) -> list[Domain]:
        """All Domains"""
        return list(set(sum([d.domains for d in self.aspects], [])))

    def get(
        self,
        keys: Literal[
            'aspects', 'states', 'controls', 'streams', 'impacts', 'domains'
        ] = 'aspects',
        values: Literal[
            'aspects', 'states', 'controls', 'streams', 'impacts', 'domains'
        ] = 'domains',
    ) -> dict[Aspect | Domain, list[Aspect | Domain]]:
        """Get a dictionary of the treewith a particular structure

        Args:
            keys (Literal[ 'aspects', 'states', 'controls', 'streams', 'impacts', 'domains' ], optional): Defaults to 'aspects'.
            values (Literal[ 'aspects', 'states', 'controls', 'streams', 'impacts', 'domains' ], optional): Defaults to 'domains'.

        Returns:
            dict[Aspect | Domain, list[Aspect | Domain]]: dictionary with particular structure
        """
        # This function will essentially return a dictionary
        # with any choice of keys and values
        # can come very handy
        if keys in ['aspects', 'states', 'controls', 'streams', 'impacts']:
            keysset: list[Aspect] = getattr(self, keys)

            if values == 'domains':
                return {d: [dom.tup for dom in d.domains] for d in keysset if d.domains}
            else:
                return {d: getattr(d, values) for d in keysset if getattr(d, values)}

        if keys in ['domains']:
            dict_ = {d: [] for d in self.domains}

            for dom in self.domains:
                for val in self.get(keys=values, values=keys):
                    if dom in self.get(keys=values, values=keys)[val]:
                        dict_[dom].append(val)
            dict_ = {k.tup: v for k, v in dict_.items() if v}
            return dict_

        raise ValueError(
            'keys must be one of aspects, states, controls, streams, impacts, domains'
        )

    # @property
    # def capacity_bound(self) -> list[Domain]:
    #     """Finds the spaces and times in which the an operation is bound"""

    #     _capacity_bound = {
    #         domain.operation: []
    #         for domain in self.model.capacity.domains + self.model.invcapacity.domains
    #     }
    #     for domain in self.model.capacity.domains + self.model.invcapacity.domains:
    #         _capacity_bound[domain.operation].append((domain.space, domain.time))

    #     return _capacity_bound

    # @property
    # def operate_bound(self) -> list[Domain]:
    #     """Finds the spaces and times in which the an operation is bound"""

    #     _operate_bound = {domain.operation: [] for domain in self.model.operate.domains}
    #     for domain in self.model.operate.domains:
    #         _operate_bound[domain.operation].append((domain.space, domain.time))

    #     return _operate_bound

    # @property
    # def inventory_bound(self) -> list[Domain]:
    #     """Finds the spaces and times in which the an storage inventory is bound"""

    #     _inventory_bound = {
    #         domain.resource: [] for domain in self.model.inventory.domains
    #     }
    #     for domain in self.model.inventory.domains:
    #         _inventory_bound[domain.resource].append((domain.space, domain.time))

    #     return _inventory_bound
