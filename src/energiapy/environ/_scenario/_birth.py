"""Class with functions to birth Components in the Scenario
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from operator import is_not, mul
from itertools import accumulate
from typing import TYPE_CHECKING

from ...components.operation.process import Process
from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.temporal.scale import Scale

if TYPE_CHECKING:
    from ..system import System
    from ..network import Network
    from ..horizon import Horizon
    from ...components.commodity.resource import Resource
    from ...components.operation.storage import Storage
    from ...components.operation.transit import Transit
    from ...elements.parameters.balances.inventory import Inventory
    from ...elements.parameters.balances.freight import Freight


class _Birth(ABC):

    @property
    @abstractmethod
    def system(self) -> System:
        """System Model Block of the Scenario"""

    @property
    @abstractmethod
    def horizon(self) -> Horizon:
        """Horizon of the Scenario"""

    @property
    @abstractmethod
    def network(self) -> Network:
        """Network of the Scenario"""

    def birth_partitions(
        self,
        birth: Scale | Location,
        birth_list: int | list[int],
        birth_names: str | list[str],
        nested: bool,
        name_str: str,
    ):
        """Births temporal Scales based on discretizations provided in the Horizon

        Args:
            scope (Horizon | Network): Scope Component
        """

        if isinstance(birth_list, int):

            birth_list = [birth_list]
            birth_names = [birth_names]

        if nested:
            birth_list = list(accumulate(birth_list, mul))

        if not birth_names:
            birth_names = [f'{name_str}{b}' for b in range(len(birth_list))]

        for i, d in enumerate(birth_list):
            # set the scales as attributes of the Scenario
            setattr(
                self,
                f'{birth_names[i]}',
                birth(d),
            )

    def birth_scales(
        self,
        scales: int | list[int],
        names: str | list[str] = None,
        nested: bool = False,
    ):
        """Births temporal Scales based on discretizations provided in the Horizon"""

        self.birth_partitions(
            birth=Scale,
            birth_list=scales,
            birth_names=names,
            nested=nested,
            name_str='t',
        )

    def birth_locations(
        self,
        locations: int | list[int],
        names: str | list[str] = None,
        nested: bool = False,
    ):
        """Births Locations based on discretizations provided in the Network"""

        self.birth_partitions(
            birth=Location,
            birth_list=locations,
            birth_names=names,
            nested=nested,
            name_str='l',
        )

    def birth_sib_linkage(self, linkage: Linkage):
        """Births a Linkage going in the opposite direction of the provided Linkage
        if bi is set to True

        Args:
            linkage (IsLinkage): Linkage object
        """

        if linkage.bi:
            # Internally, linkages can only go in one direction
            # The direction of the declared linkage is set in the original order of Locations
            setattr(linkage, 'bi', False)

            # The name of the birthed Linkage is name with '_' appended
            # The source and sink are reversed
            setattr(
                self,
                f'{linkage.name}_',
                Linkage(
                    source=linkage.sink,
                    sink=linkage.source,
                    label=linkage.label,
                    distance=linkage.distance,
                    bi=False,
                ),
            )
            setattr(
                getattr(self.network, linkage.name),
                'sib',
                getattr(self.network, f'{linkage.name}_'),
            )
            setattr(
                getattr(self.network, f'{linkage.name}_'),
                'sib',
                getattr(self.network, linkage.name),
            )

    def link_all(self):
        """Births Linkages for between all Locations in the Network

        Triggered if Network.link_all is set to True

        Args:
            network (IsNetwork): Network object
        """

        for i, src in enumerate(self.network.locations):
            for snk in self.network.locations:
                if is_not(src, snk):
                    # set the linkages as attributes of the Scenario
                    setattr(self, f'lnk{i}', Linkage(source=src, sink=snk, bi=True))

    def birth_bal_processes(self, operation: Storage | Transit, res: Resource):
        """Births Balance Processes
        Charging and Discharging Processes for a Operation Component
        Loading and Unloading Processes for a Transit Component

        Args:
            operation (IsOperation): Operation object
        """

        # The base resource (what is stored)
        balance: Inventory | Freight = operation.balance
        base: Resource = balance.operated
        # eta is the efficiency of the operation
        # Input conversion produces ResourceStg, using Resource
        # {ResourceStg: {Resource: -eta}}
        conv_in: dict = balance.conversion_in
        # Output conversion consumes Resource, using ResourceStg
        # {Resource: {ResourceStg: -eta}}
        conv_out: dict = balance.conversion_out[base]

        # A Operation Resource is birthed
        setattr(self, f'{operation}_{base}', res)
        res = getattr(self, f'{operation}_{base}')

        # When Invetory is made within the Operation
        # Place holders are used for Operation Resource (res)
        # This is to keep birthing operations only in the Scenario
        # The conversions are updated in Operation Balance as well
        # These are cleaned up here
        conv_in[res] = conv_in.pop('r')
        conv_out[res] = conv_out.pop('r')

        # Charging(_in) and Discharging(_out) Processes are birthed
        # and set on the scenario
        setattr(
            self,
            f'{operation}_in',
            Process(conversion=conv_in, setup=operation.setup_in),
        )
        setattr(
            self,
            f'{operation}_out',
            Process(conversion=conv_out, setup=operation.setup_out),
        )

        # The Processes are set as attributes of the Operation
        operation.process_in = getattr(self, f'{operation}_in')
        operation.process_out = getattr(self, f'{operation}_out')

        # set the flag to True
        operation.birthed = True
