"""Scenario is the core object in energiapy. 

    Everything else is defined as a scenario attribute.

    energiapy.components are added to the System Model Block
    _Components are the base for all components in energiapy, broadly categorized into
    Components the do not generate constraints and those that do.
    The former are further divided into -
          _Scope: Horizon, Network
          These create the spatiotemporal scope of the problem
    Scopes are further divided into -
          _Spatial: Location, Linkage
          _Temporal: Scale
          Locations and Scales are generated internally, Linkages are user-defined
    _Defined components generate constraints which are added to the Program Model Block
    
    These include -
          _Commodity: Cash, Land, Resource, Material, Emission
          _Operational: Process, Storage, Transit
          _Analytical: Players
    The data provided as attributes is added to the Data Model Block
    provided data is converted into in internal formats: Constant, DataSet, Theta, M
    Theta - provided as tuple
    M - provided as True
    Constant - provided as float, int
    DataSet - provided as DataFrame
    Further any of these can be provided as a list to create an upper and lower bound for bounded variables
    
    The DataBlock is then added to the Program Model Block
    The Program Model Block is used to generate Parameters, Variables, Constraints, and Objectives
    
    The Matrix Model is just a matrix representation of the problem block

"""

from __future__ import annotations
from dataclasses import dataclass, field
from warnings import warn
from typing import Any, TYPE_CHECKING

from .._core._handy._collections import (
    _Alys,
    _Cmds,
    _Elms,
    _Imps,
    _LnkOpns,
    _LocOpns,
    _Scls,
    _Scps,
    _Spts,
    _Vlus,
)
from ..components._base._component import _Component
from ..components._base._defined import _Defined
from ..components.commodity.cash import Cash
from ..components.commodity.land import Land
from ..components.commodity.resource import ResourceStg
from ..components.operational._operational import _Operational
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.scope.horizon import Horizon
from ..components.scope.network import Network
from ..components.spatial.linkage import Linkage
from ..components.spatial.location import Location
from ..components.temporal.scale import Scale
from ._base._default import _Default
from .data import DataBlock
from .model import Model
from .program import ProgramBlock

if TYPE_CHECKING:
    from .._core._aliases._is_component import IsDefined, IsScopeScale, IsLonely


class _ScnCols(
    _Alys, _Imps, _Cmds, _LocOpns, _LnkOpns, _Spts, _Scls, _Scps, _Elms, _Vlus
):
    """Scenario Collections"""


@dataclass
class Scenario(_Default, _ScnCols):
    """
    A scenario for a considered system. It collects all the components of the model.

    Input:
        name (str, optional): Name. Defaults to ':s:'.

    Examples:

        >>> from energiapy.components import Scenario
        >>> s = Scenario(name='Current')

    """

    name: str = field(default=':s:')

    def __post_init__(self):

        # These are flags to check existence of components which can have only one instance in the System
        for cmp in ['horizon', 'network', 'land', 'cash']:
            setattr(self, f'_{cmp}', False)

        # Declare Model, contains system, program, data, matrix
        self.model = Model(name=self.name)

        # set default values if self.default (inherited from _Default) is True
        self._default()

    def __setattr__(self, name, value):

        if isinstance(value, _Component):

            # Personalize the component
            value.personalize(name=name, model=self.model)

            # set the component in the system
            setattr(self.system, name, value)

            if isinstance(value, _Defined):

                # defined components generate constraints (ProgramBlock) which are added to the Program

                # Components that can have only one instance in the System are handled here
                # Unique components are set as properties of the System which the Scenario can access
                if isinstance(value, Cash):
                    self.handle_unique_cmp(cmp='cash', component=value)

                if isinstance(value, Land):
                    self.handle_unique_cmp(cmp='land', component=value)

                # All defined components have constraints
                # The data is handled first and made into internal formats and added to the Data Model
                # The Program Model is then generated using information from the Data Model
                self.update_model(name=name, component=value)

        if isinstance(value, Horizon):

            self.handle_unique_cmp('horizon', value)

            for i in range(value.n_scales):

                if value.label_scales:
                    label_scale = value.label_scales[i]
                else:
                    label_scale = value.label_scales

                setattr(
                    self,
                    value._name_scales[i],
                    Scale(
                        index=value.make_index(position=i, nested=value.nested),
                        label=label_scale,
                    ),
                )

        if isinstance(value, Network):

            self.handle_unique_cmp('network', value)

            for i in value.locs:

                if value.label_locs:
                    label_node = value.label_locs[i]
                else:
                    label_node = value.label_locs

                setattr(self, i, Location(label=label_node))

        if isinstance(value, Linkage):
            if value.bi:

                setattr(value, 'bi', False)

                setattr(
                    self,
                    f'{value.name}_',
                    Linkage(
                        source=value.sink,
                        sink=value.source,
                        label=value.label,
                        distance=value.distance,
                        bi=False,
                    ),
                )

        if isinstance(value, _Operational):
            value.locate()

        if isinstance(value, Process):

            getattr(self.system, name).conversionize()

        if isinstance(value, Storage):

            storage = getattr(self.system, name)
            storage.inventorize()

            base = storage.inventory.base
            conv_c = storage.inventory.conversion_c
            conv_d = storage.inventory.conversion_d

            setattr(self, f'{storage}_{base}', ResourceStg())
            resourcestg = getattr(self, f'{storage}_{base}')

            conv_c[resourcestg] = conv_c.pop('resource_stg')
            setattr(self, f'{name}_c', Process(conversion=conv_c))
            storage.inventory.conversion_c = getattr(self, f'{name}_c').conversion

            conv_d[base][resourcestg] = conv_d[base].pop('resource_stg')
            setattr(self, f'{name}_d', Process(conversion=conv_d))
            storage.inventory.conversion_d = getattr(self, f'{name}_d').conversion

        # if isinstance(value, _Operational):
        #     for cmd in value.commodities:
        #         if not cmd._located:
        #             cmd.locate()

        super().__setattr__(name, value)

    @property
    def system(self):
        """System of the Scenario"""
        return self.model.system

    @property
    def program(self):
        """Program of the Scenario"""
        return self.model.program

    @property
    def data(self):
        """Data of the Scenario"""
        return self.model.data

    @property
    def matrix(self):
        """Matrix of the Scenario"""
        return self.model.matrix

    @property
    def components(self):
        """All Components of the System"""
        return self.system.components()

    def eqns(self, at_cmp=None, at_disp=None):
        """Prints all equations in the program
        Args:
            at_cmp (IsComponent, optional): Component to search for. Defaults to None.
            at_disp (IsDisposition, optional): Disposition to search for. Defaults to None.
        """
        self.program.eqns(at_cmp=at_cmp, at_disp=at_disp)

    def cleanup(self, cmp: str):
        """Cleans up components which can have only one instance in the System
        Args:
            cmp (str): 'cash', 'land', 'horizon', 'network'
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
        datablock = DataBlock(component=component)
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
