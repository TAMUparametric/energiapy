from __future__ import annotations

from typing import TYPE_CHECKING

from ...funcs.utils.attr_input import get_depth

if TYPE_CHECKING:
    from ...type.alias import IsHorizon, IsInput, IsNetwork, IsSptTmpDict


def make_consistent(attr_input: IsInput, network: IsNetwork, horizon: IsHorizon) -> IsSptTmpDict:

    if get_depth(attr_input) == 0:
        return {network: {horizon.scales[0]: attr_input}}

    if get_depth(attr_input) == 1:
        for i in attr_input:
            if isinstance()
