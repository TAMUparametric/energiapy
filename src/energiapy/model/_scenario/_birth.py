"""Class with functions to birth Components in the Scenario
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from operator import is_not
from typing import TYPE_CHECKING

from ...components.operational.process import Process
from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.temporal.scale import Scale

if TYPE_CHECKING:
    from ...core.aliases.iscmp import (IsHorizon, IsLinkage, IsNetwork,
                                             IsOperational, IsResource)


class _Birth(ABC):

    @property
    @abstractmethod
    def system(self):
        """System Model Block of the Scenario"""

    def birth_scales(self, horizon: IsHorizon):
        """Births temporal Scales based on discretizations provided in the Horizon

        Args:
            horizon (IsHorizon): Horizon object
        """
        for i in range(horizon.n_scales):
            # labels can be provided. or they are set to t0, t1, t2, ...

            if horizon.label_scales:
                label_scale = horizon.label_scales[i]
            else:
                label_scale = horizon.label_scales

            # set the scales as attributes of the Scenario
            setattr(
                self,
                horizon.name_scales[i],
                Scale(
                    index=horizon.make_index(position=i, nested=horizon.nested),
                    label=label_scale,
                ),
            )

    def birth_locations(self, network: IsNetwork):
        """Births Locations based on the locs provided in the Network

        Args:
            network (IsNetwork): Network object
        """

        for i in network.locs:
            if network.label_locs:
                label_node = network.label_locs[i]
            else:
                label_node = network.label_locs
            # set the locations as attributes of the Scenario
            setattr(self, i, Location(label=label_node))

    def birth_sib_linkage(self, linkage: IsLinkage):
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
                getattr(self.system, linkage.name),
                'sib',
                getattr(self.system, f'{linkage.name}_'),
            )
            setattr(
                getattr(self.system, f'{linkage.name}_'),
                'sib',
                getattr(self.system, linkage.name),
            )

    def birth_all_linkages(self, network: IsNetwork):
        """Births Linkages for between all Locations in the Network

        Triggered if Network.link_all is set to True

        Args:
            network (IsNetwork): Network object
        """

        for i, src in enumerate(network.locations):
            for snk in network.locations:
                if is_not(src, snk):
                    # set the linkages as attributes of the Scenario
                    setattr(self, f'lnk{i}', Linkage(source=src, sink=snk, bi=True))

    def birth_bal_processes(self, operation: IsOperational, res: IsResource):
        """Births Balance Processes
        Charging and Discharging Processes for a Operation Component
        Loading and Unloading Processes for a Transit Component

        Args:
            operation (IsOperation): Operation object
        """

        # The base resource (what is stored)
        balance = operation.balance
        base = balance.base
        conv_in, conv_out = balance.conversion_in, balance.conversion_out

        # A Operation Resource is birthed
        setattr(self, f'{operation}_{base}', res)
        res = getattr(self, f'{operation}_{base}')

        # When Invetory is made within the Operation
        # Place holders are used for Operation Resource (res)
        # This is to keep birthing operations only in the Scenario
        # The conversions are updated in Operation Balance as well
        # These are cleaned up here
        conv_in[res] = conv_in.pop('r')
        conv_out[res] = conv_out[base].pop('r')

        # Charging(_in) and Discharging(_out) Processes are birthed
        process_in = Process(conversion=conv_in, capacity=operation.capacity_in)
        process_out = Process(conversion=conv_out, capacity=operation.capacity_out)
        processes = [process_in, process_out]

        # update processes in Operation
        setattr(operation, 'processes', processes)
        # set the processes as attributes of the Scenario
        setattr(self, f'{operation}_in', operation.process_in)
        setattr(self, f'{operation}_out', operation.process_out)

        # set the flag to True
        setattr(operation, '_birthed', True)
