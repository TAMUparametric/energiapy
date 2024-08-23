"""Class with functions to update:
    1. Components in the Scenario
    2. The Model Blocks 
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from operator import is_not
from typing import TYPE_CHECKING
from warnings import warn

from ...components.operational.process import Process
from ...components.scope.horizon import Horizon
from ...components.spatial.linkage import Linkage
from ...components.spatial.location import Location
from ...components.temporal.scale import Scale
from ..data import DataBlock
from ..program import ProgramBlock

if TYPE_CHECKING:
    from ..._core._aliases._is_component import (
        IsDefined,
        IsHorizon,
        IsLinkage,
        IsLonely,
        IsNetwork,
        IsOperational,
        IsStorage,
        IsResource,
    )


class _Update(ABC):
    """Has all the function needed to update the Scenario with Components and Model Blocks"""

    @property
    @abstractmethod
    def system(self):
        """System Model Block of the Scenario"""

    @property
    @abstractmethod
    def program(self):
        """Program Model Block of the Scenario"""

    @property
    @abstractmethod
    def data(self):
        """Data Model Block of the Scenario"""

    def cleanup(self, cmp: str):
        """Cleans up components which can have only one instance in the System
        Also the stuff they generate such as Scales (Horizon) and Locations (Network)

        Args:
            cmp (str): property in Scenario that stores Component 'cash', 'land', 'horizon', 'network'
        """

        cmp = getattr(self, cmp)

        if cmp:
            if isinstance(cmp, Horizon):
                # remove scales if type Horizon
                for scale in cmp.scales:
                    delattr(self, scale.name)
                    delattr(self.system, scale.name)

            # remove the component from Scenario
            delattr(self, cmp.name)

            # remove the component from System
            delattr(self.system, cmp.name)

            # remove the component from Program Block
            if hasattr(self.program, cmp.name):
                delattr(self.program, cmp.name)

            # remove the component from Data Block
            if hasattr(self.data, cmp.name):
                delattr(self.data, cmp.name)

            warn(
                f'\nA {cmp} object was already defined.\n'
                'Overwriting.\n'
                'This should not cause any modeling issues.\n'
                'Check Scenario defaults if unintended.\n'
            )

    def locate_commodities(self, operation: IsOperational):
        """Locates Commodities based on their participation in Operations

        Args:
            operation (IsOperational): _Operation object
        """
        # commodities for Process come from conversion
        # for Storage from conersion_c and conversion_d
        # for Transit from freight
        for cmd in getattr(self.system, operation.name).commodities:
            if not cmd.is_located:
                cmd.locate()

    def handle_unique_cmp(self, cmp: str, component: IsLonely):
        """Handles components which can have only one instance in the System
        Args:
            cmp (str): 'cash', 'land', 'horizon', 'network'
            component(IsComponent): Component to be added

        """

        if getattr(self, f'_{cmp}'):
            # if there is an existing instance of the same type
            # remove it before adding the new one
            # also remove generated components such as scales and locations
            # also remove associated data and program if they exist
            self.cleanup(cmp)

        # set the component in the system
        setattr(self.system, cmp, component)

        # set the flag to True
        setattr(self, f'_{cmp}', True)

    def update_model(self, name: str, component: IsDefined):
        """Updates the Data and System Model with the components

        Args:
            name (str): name of component
            component (IsDefined): Component to be added
        """

        # Make the component inputs consistent
        # i.e. of the form - {Spatial[Location, Linkage, Network]: Temporal[Scale]: Mode[X]: Value}
        # Value can be numeric, DataFrame, True
        # or a tuple of numeric or DataFrame
        # or a list or numeric, DataFrame, True, or a tuple of numeric or DataFrame
        component.make_consistent()

        # make Small Blocks to be added to the larger Model Blocks
        # where all the data values go
        datablock = DataBlock(component=component, m=getattr(self, 'm'))
        # where all the model elements go
        programblock = ProgramBlock(component=component)

        # Each _Defined component has inputs which are categorized
        # check individual component parent classes _Operational, _Commodity (_Traded and _Used) for details
        for inp in component.inputs():
            # if the input is provided (they all default to None)
            if getattr(component, inp, False):
                # set the input as attribute in the DataBlock
                # This will make them into energiapy internal formats - Constant, DataSet, Theta, M
                setattr(datablock, inp, {component: getattr(component, inp)})

                # The updated Values are then set back into the component
                setattr(component, inp, getattr(datablock, inp))

        # The smaller Blocks are then added to the Larger Scenario Level Model Blocks
        # The DataBlock is added to the Data Model
        setattr(self.data, name, datablock)

        # The DataBlock is then added to the ProgramBlock
        # The disposition and type of value is used to generate Program elements:
        # Parameters, Variables, Constraints, and Objectives
        setattr(programblock, name, datablock)

        # The ProgramBlock is also added to the Program Model
        setattr(self.program, name, programblock)

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
