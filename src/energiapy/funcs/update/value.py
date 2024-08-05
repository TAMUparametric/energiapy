from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...types.alias import (IsApproach, IsCertainty, IsSpcLmt, IsValue,
                                IsVarBnd)


def update_bounds(value: IsValue, varbound: IsVarBnd = None, spclimit: IsSpcLmt = None):
    """Updates the name to add a variable bound"""
    if varbound:
        setattr(value, '_varbound', varbound)

    if spclimit:
        setattr(value, '_spclimit', spclimit)
