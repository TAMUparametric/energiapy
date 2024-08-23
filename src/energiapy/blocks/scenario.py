"""Scenario, is the core object 

    All Components defined as a scenario attribute.

    energiapy.components get added to the System Model Block
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

from dataclasses import dataclass, field

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
from .._core._handy._dunders import _Dunders
from .._core._handy._printers import _Print
from ..components._base._component import _Component
from ..components._base._defined import _Defined
from ..components.commodity.cash import Cash
from ..components.commodity.land import Land
from ..components.commodity.resource import ResourceStg, ResourceTrn
from ..components.operational._operational import _Operational
from ..components.operational.process import Process
from ..components.operational.storage import Storage
from ..components.operational.transit import Transit
from ..components.scope.horizon import Horizon
from ..components.scope.network import Network
from ..components.spatial.linkage import Linkage
from ._base._default import _Default
from ._base._ok import _Ok
from ._base._update import _Update
from .model import Model


class _ScnCols(
    _Alys, _Imps, _Cmds, _LocOpns, _LnkOpns, _Spts, _Scls, _Scps, _Elms, _Vlus
):
    """Scenario Collections"""


@dataclass
class Scenario(_Ok, _Default, _Update, _ScnCols, _Dunders, _Print):
    """
    A scenario for a considered system. It collects all the components of the model.

    Some default components can be created (def_ attributes):
        1. Network with no Locations or Linkages
        2. Horizon with only a root scale, i.e. the planning horizon (ph)
        3. Land with no bounds
        4. Cash with no bounds
        5. Players, viz. Consumer, Decision Maker, Market , Earth
        6. Emissions such as gwp, odp, etc.

    The strictness of checks can also be controlled (ok_ attribures).

    Attributes:
        name (str, optional): Name. Defaults to ':s:'.
        m (float): replaces 0 inputs with a small m (bearing this value). Default is None
        def_scope (bool): create default Scope (Network, Horizon) Components. Default is False
        def_players (bool): create default (Players) Components. Default is False
        def_emissions (bool): create default (Emission) Components. Default is False
        def_cash (bool): create default (Cash) Components. Default is False
        def_land (bool): create default (Land) Components. Default is False
        default (bool): create default Components of all the above. Default is False
        ok_overwrite (bool): Allow overwriting of Components. Default is False
        ok_nobasis (bool): Allow Components without basis. Default is False
        ok_nolabel (bool): Allow Components without label. Default is False
        chill (bool): Allow all the above. Default is True

    Examples:

        >>> from energiapy.components import Scenario
        >>> s = Scenario(name='Current')

    """

    name: str = field(default=':s:')
    m: float = field(default=None)

    def __post_init__(self):
        _Ok.__post_init__(self)
        _Default.__post_init__(self)

        # These are flags to check existence of components which can have only one instance in the System
        for cmp in ['horizon', 'network', 'land', 'cash']:
            setattr(self, f'_{cmp}', False)

        # Declare Model, contains system, program, data, matrix
        self.model = Model(name=self.name)

        # set default values if self.default (inherited from _Default) is True
        self._default()

    def __setattr__(self, name, value):

        # All components are personlized with the attribute name provided
        # The Model [System, Program, Data, Matrix] is also added
        # This is a cursory step to check what is being added, also excludes name
        if isinstance(value, _Component):
            # Personalize the component

            value.personalize(name=name, model=self.model)

            # Check if ok to overwrite
            # Inherited from _Ok
            self.isok_ovewrite(cmp=name)

            # set the component in the system
            setattr(self.system, name, value)

            # defined components generate constraints (ProgramBlock) which are added to the Program
            if isinstance(value, _Defined):

                # Run some checks based on what is ok
                # Inherited from _Ok
                self.isok_nobasis(component=value)
                self.isok_nolabel(component=value)

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

            # Horizon, Network, Linkages and Storage give birth to new components
            if isinstance(value, Horizon):
                self.handle_unique_cmp('horizon', value)
                self.birth_scales(horizon=value)

            if isinstance(value, Network):
                self.handle_unique_cmp('network', value)
                self.birth_locations(network=value)
                if value.link_all:
                    self.birth_all_linkages(network=value)

            if isinstance(value, Linkage):
                self.birth_sib_linkage(linkage=value)

            # find where all the Operation is located
            # if nothing is provided, available throughout Network (all locations)
            if isinstance(value, _Operational):
                value.locate()

            # Operation are gotten from the System because at this point they are not set to the Scenario
            if isinstance(value, Process):
                process = getattr(self.system, name)
                # make the conversion into a Conversion
                process.conversionize()
                self.locate_commodities(operation=process)

            if isinstance(value, Storage):
                storage = getattr(self.system, name)
                # make the inventory into Inventory
                storage.inventorize()
                # birth the Charging and Discharging processes
                # and the Storage Resource
                self.birth_bal_processes(operation=storage, res=ResourceStg())

            if isinstance(value, Transit):
                transit = getattr(self.system, name)
                # make the freight into Freight
                transit.freightize()
                # birth the Loading and Unloading processes
                # and the Transit Resource
                self.birth_bal_processes(operation=transit, res=ResourceTrn())

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
        for eqn in self.program.eqns(at_cmp=at_cmp, at_disp=at_disp):
            yield eqn
