"""The main object in energiapy. Everything else is defined as a scenario attribute.
"""

from dataclasses import dataclass, field
from warnings import warn

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
from ..components.commodity._commodity import _Commodity
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


class _ScnCols(
    _Alys, _Imps, _Cmds, _LocOpns, _LnkOpns, _Spts, _Scls, _Scps, _Elms, _Vlus
):
    """Scenario Collections"""


@dataclass
class Scenario(_Default, _ScnCols):
    """
    A scenario for a considered system. It collects all the components of the model.

    Input:
        name (str, optional): Name. Defaults to 'energia'.
        horizon (Horizon): Planning horizon of the problem, generated post-initialization.
        scales (List[Scale]): List of Scale objects, generated post-initialization.
        resources (List[Resource]): List of Resource objects, generated post-initialization.
        processes (List[Process]): List of Process objects, generated post-initialization.
        locations (List[Location]): List of Location objects, generated post-initialization.
        transports (List[Transit]): List of Transit objects, generated post-initialization.
        linkages (List[Linkage]): List of Linkage objects, generated post-initialization.
        network (Network): Network

    Examples:

        There is not much to this class, it is just a container for the components of the model.

        >>> from energiapy.components import Scenario
        >>> s = Scenario(name='Current')

    """

    name: str = field(default=':s:')

    def __post_init__(self):

        # Declare Model
        self.model = Model(name=self.name)
        self._default()

    def __setattr__(self, name, value):

        if isinstance(value, _Component):

            # Only one of Cash or Land can be defined
            # if already defined, remove it
            if isinstance(value, Cash):
                self.cleanup('cash')

            if isinstance(value, Land):
                self.cleanup('land')

            if isinstance(value, Horizon):
                self.cleanup('horizon')

            if isinstance(value, Network):
                self.cleanup('network')

            value.personalize(name=name, model=self.model)
            setattr(self.system, name, value)

            if isinstance(value, _Defined):

                value.make_consistent()

                datablock = DataBlock(component=value)
                programblock = ProgramBlock(component=value)

                for inp in value.inputs():

                    if getattr(value, inp, False):
                        setattr(datablock, inp, {value: getattr(value, inp)})

                        setattr(value, inp, getattr(datablock, inp))

                setattr(self.data, name, datablock)

                setattr(programblock, name, datablock)

                setattr(self.program, name, programblock)

        if isinstance(value, Horizon):

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

        if isinstance(value, _Operational):

            for cmd in value.commodities:
                if not cmd._located:
                    cmd.locate()

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
        """Cleans up components which can have only one instance in the Model
        Args:
            cmp (str): Component to be removed
        """

        cmp = getattr(self, cmp)

        if cmp:

            if isinstance(cmp, Horizon):
                for scale in cmp.scales:
                    delattr(self, scale.name)
                    delattr(self.system, scale.name)

            delattr(self, cmp.name)
            delattr(self.system, cmp.name)

            if hasattr(self.program, cmp.name):
                delattr(self.program, cmp.name)

            if hasattr(self.data, cmp.name):
                delattr(self.data, cmp.name)

            warn(
                f'\nA {cmp} object was already defined.\n'
                'Overwriting.\n'
                'This should not cause any modeling issues.\n'
                'Check Scenario defaults if unintended.\n'
            )
