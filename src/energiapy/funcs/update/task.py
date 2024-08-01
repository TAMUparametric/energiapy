from __future__ import annotations

from operator import is_
from typing import TYPE_CHECKING

from ...elements.index import Index
from ...funcs.birth.task import birth_task
from ...funcs.birth.value import birth_value
from ...funcs.check.value import scale_match
from ...funcs.update.value import update_bounds
from ...inputs.values.bounds import VarBnd

if TYPE_CHECKING:
    from ...types.alias import (IsCommodity, IsComponent, IsInput, IsOperation,
                                IsPlayer, IsScale, IsSpatial)


def update_task(player: IsPlayer, component: IsComponent, attr_name: str, attr_input: IsInput, derived: IsCommodity, commodity: IsCommodity, operation: IsOperation, spatial: IsSpatial, scale: IsScale):
    
    task = birth_task(component=component, attr_name=attr_name)

    horizon = component.horizon
    if not isinstance(attr_input, dict):
        scl_val = {horizon[0]: attr_input}

    for scale_, value_ in scl_val.items():

        if isinstance(value_, list):

            low_or_up = {0: VarBnd.LOWER, 1: VarBnd.UPPER}

            if len(value_) > 2:
                raise ValueError(
                    f'{component.name}: tuple must be of length 2')
            # if only one value, then it is an upper bound
            elif len(value_) == 1:
                value_ = [0] + value_

            value_ = [birth_value(
                name=attr_name, attr_input=i, index=index) for i in value_]

            for i, j in enumerate(value_):

                scale_ = scale_match(value=j, horizon=horizon, scale=scale_)

                if not scale_:
                    raise ValueError(
                        f'{component.name}.{attr_name}: length of data does not match any scale index')

                index = Index(player=player, derived=derived, commodity=commodity,
                              operation=operation, spatial=spatial, scale=scale_)

                update_bounds(value=j, varbound=low_or_up[i])

                
                task.add(j, index=index)
                

        else:

            scale_ = scale_match(value=j, horizon=horizon, scale=scale_)

            index = Index(player=player, derived=derived, commodity=commodity,
                          operation=operation, spatial=spatial, scale=scale_)

            if not scale_:
                raise ValueError(
                    f'{component.name}.{attr_name}: length of data does not match any scale index')

            value_ = birth_value(
                name=attr_name, attr_input=attr_input, index=index)


            task.add(value=value_, index=index)

        setattr(component, attr_name, task)
