"""Decision Space of the Model"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..components.commodity.currency import Currency
from ..components.commodity.emission import Emission
from ..components.commodity.land import Land
from ..components.commodity.material import Material
from ..components.commodity.resource import Resource
from ..components.commodity.stored import Stored
from ..components.impact.categories import Economic, Environ, Social
from ..components.operation.process import Process
from ..components.operation.transport import Transport
from ..modeling.variables.control import Control
from ..modeling.variables.states import (EndoStream, ExoStream, IndStream,
                                         SetPoint, Size)

if TYPE_CHECKING:
    from ..represent.model import Model


def capacity_sizing(model: Model):
    """Sets capacity sizing decisions"""
    model.Recipe(
        "capacity",
        Size,
        primary_type=(Process, Transport),
        label="Capacitate Operation",
        latex=r"{cap}",
        add_kind=Control,
        add="setup",
        add_latex=r"{cap}^{+}",
        sub="dismantle",
        sub_latex=r"{cap}^{-}",
    )


def operating(model: Model):
    """Operating/Scheduling decisions"""

    model.Recipe(
        "operate",
        SetPoint,
        primary_type=(Process, Transport),
        label="Capacity Utilization",
        latex=r"{opr}",
        add_kind=Control,
        add="rampup",
        add_latex=r"{opr}^{+}",
        sub="rampdown",
        sub_latex=r"{opr}^{-}",
        bound="capacity",
    )

    model.Recipe(
        "produce",
        EndoStream,
        primary_type=Resource,
        latex="prod",
        label="Stream produced in Operation",
        neg="expend",
        neg_latex=r"{expd}",
        neg_label="Stream expended in Operation",
    )

    model.Recipe(
        "ship_in",
        EndoStream,
        primary_type=Resource,
        label="Resource Imported into Location",
        latex=r"{impt}",
        neg="ship_out",
        neg_label="Resource Exported out of Location",
    )


def inventory_sizing(model: Model):
    """Inventory management decisions"""
    model.Recipe(
        "invcapacity",
        Size,
        primary_type=Stored,
        label="Inventory Capacity",
        latex=r"{icap}",
        add_kind=Control,
        add="invdismantle",
        add_latex=r"{icap}^{-}",
        sub="invsetup",
        sub_latex=r"{icap}^{+}",
    )

    model.Recipe(
        "inventory",
        EndoStream,
        primary_type=Stored,
        label="Stored Resource",
        latex=r"{inv}",
        ispos=False,
        bound="invcapacity",
    )


def usage(model: Model):
    """Resource usage decisions"""
    model.Recipe(
        "dispose",
        EndoStream,
        primary_type=(Resource, Land, Material),
        label="Dispose Resource",
        latex=r"{disp}",
        neg="use",
        neg_label="Use Resource",
    )


def free_movement(model: Model):
    """
    Free movement entails consumption or release of resources
    This is an interaction with the system exterior

    .. note::
        Use buy and sell if interacting with a Player
    """
    model.Recipe(
        "consume",
        ExoStream,
        primary_type=Resource,
        label="Free Resource Stream",
        latex=r"{cons}",
        add_kind=Control,
        neg="release",
        neg_latex=r"{rlse}",
    )


def trade(model: Model):
    """Trade decisions"""
    model.Recipe(
        "buy",
        ExoStream,
        primary_type=Resource,
        label="Buy Resource",
        neg="sell",
    )


def economic(model: Model):
    """Economic decisions"""
    model.Recipe(
        "earn",
        IndStream,
        primary_type=(Currency, Economic),
        neg="spend",
    )


def environmental(model: Model):
    """Environmental impact decisions"""
    model.Recipe(
        "emit",
        IndStream,
        primary_type=(Environ, Emission),
        neg="abate",
    )


def social(model: Model):
    """Social impact decisions"""
    model.Recipe(
        "benefit",
        IndStream,
        primary_type=(Social, Currency),
        neg="detriment",
    )
