from __future__ import annotations

from operator import is_
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...types.alias import IsHorizon, IsScale, IsValue


def scale_match(value: IsValue, scale: IsScale, horizon: IsHorizon) -> IsScale:
    """if on default scale, and value has non unity length, find a scale that matches

    Args:
        value (IsValue): Value being passed
        scale (IsScale): Scale being passed
        horizon (IsHorizon): Horizon being passed

    Returns:
        IsScale: updated scale or False
    """

    if is_(scale, horizon.scales[0]):
        if len(value) in horizon.n_indices:
            scale = horizon.scales[horizon.n_indices.index(
                len(value))]
        else:
            scale = None

    return scale
