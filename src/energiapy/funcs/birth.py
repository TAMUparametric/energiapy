from __future__ import annotations

from typing import TYPE_CHECKING

from ..model.specialparams.theta import Theta

if TYPE_CHECKING:
    from ..model.type.aliases import (IsAspect, IsComponent, IsDeclaredAt,
                                      IsTemporal, ParVar)


def birth_theta(value: ParVar, component: IsComponent = None,
                declared_at: IsDeclaredAt = None,
                aspect: IsAspect = None, temporal: IsTemporal = None) -> Theta:
    """Creates a parametric variable

    Args:
        value (Union[Theta, tuple]): _description_
        component (Union[energiapy.components]): components such Resource, Process, Location, Transport, Network, Scenario
        aspect (MPVarType): type of parametric variable. Check energiapy.components.parameters
        location (Location, optional): Location where this is being defined. Defaults to None
    Returns:
        Theta: parametric variable 
    """

    if isinstance(value, Theta):
        bounds = value.bounds
    else:
        bounds = value

    return Theta(bounds=bounds, component=component, aspect=aspect, declared_at=declared_at, temporal=temporal)
