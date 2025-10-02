"""Decision Space of the Model"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..components.commodity.currency import Currency
from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.commodity.emission import Emission
from ..components.commodity.stored import Stored
from ..components.impact.categories import Environ, Social, Economic
from ..components.operation.process import Process
from ..components.operation.storage import Storage
from ..components.operation.transport import Transport
from ..modeling.variables.control import Control
from ..modeling.variables.impact import Impact
from ..modeling.variables.state import State
from ..modeling.variables.stream import ExoStream, IndStream, EndoStream

if TYPE_CHECKING:
    from ..represent.model import Model


def capacity_sizing(model: Model):
    """Sets capacity sizing decisions"""
    model.Recipe(
        'capacity',
        State,
        types_opr=(Process, Transport),
        label='Capacitate Operation',
        latex=r'{cap}',
        add_kind=Control,
        add='setup',
        add_latex=r'{cap}^{+}',
        sub='dismantle',
        sub_latex=r'{cap}^{-}',
    )


def operating(model: Model):
    """Operating/Scheduling decisions"""

    model.Recipe(
        'operate',
        State,
        types_opr=(Process, Transport),
        label='Capacity Utilization',
        latex=r'{opr}',
        add_kind=Control,
        add='rampup',
        add_latex=r'{opr}^{+}',
        sub='rampdown',
        sub_latex=r'{opr}^{-}',
        bound='capacity',
    )

    model.Recipe(
        'produce',
        EndoStream,
        types_res=Resource,
        latex='prod',
        label='Stream produced in Operation',
        neg='expend',
        neg_latex=r'{expd}',
        neg_label='Stream expended in Operation',
    )

    model.Recipe(
        'ship_in',
        EndoStream,
        types_res=Resource,
        label='Resource Imported into Location',
        latex=r'{impt}',
        neg='ship_out',
        neg_label='Resource Exported out of Location',
    )


def inventory_sizing(model: Model):
    """Inventory management decisions"""
    model.Recipe(
        'invcapacity',
        State,
        types_res=Resource,
        label='Inventory Capacity',
        latex=r'{icap}',
        add_kind=Control,
        add='invdismantle',
        add_latex=r'{icap}^{-}',
        sub='invsetup',
        sub_latex=r'{icap}^{+}',
    )

    model.Recipe(
        'inventory',
        EndoStream,
        types_res=Stored,
        label='Stored Resource',
        latex=r'{inv}',
        ispos=False,
        bound='invcapacity',
    )


def usage(model: Model):
    """Resource usage decisions"""
    model.Recipe(
        'dispose',
        EndoStream,
        types_res=(Resource, Land, Material),
        label='Dispose Resource',
        latex=r'{disp}',
        neg='use',
        neg_label='Use Resource',
    )


def free_movement(model: Model):
    """Free movement entails consumption or release of resources

    This is an interaction with the system exterior

    .. note::
        Use buy and sell if interacting with a Player

    """
    model.Recipe(
        'consume',
        ExoStream,
        types_res=Resource,
        label='Free Resource Stream',
        latex=r'{cons}',
        add_kind=Control,
        neg='release',
        neg_latex=r'{rlse}',
    )


def trade(model: Model):
    """Trade decisions"""
    model.Recipe(
        'buy',
        ExoStream,
        types_res=Resource,
        label='Buy Resource',
        neg='sell',
    )


def economic(model: Model):
    """Economic decisions"""
    model.Recipe(
        'earn',
        IndStream,
        types_res=(Currency, Economic),
        neg='spend',
    )


def environmental(model: Model):
    """Environmental impact decisions"""
    model.Recipe(
        'emit',
        IndStream,
        types_res=(Environ, Emission),
        neg='abate',
    )


def social(model: Model):
    """Social impact decisions"""
    model.Recipe(
        'benefit',
        IndStream,
        types_res=(Social, Currency),
        neg='detriment',
    )
