from __future__ import annotations

from typing import TYPE_CHECKING

from pandas import DataFrame

from ...parameters.data.bounds import Bound
from ...parameters.data.constant import Number
from ...parameters.data.dataset import DataSet
from ...parameters.data.m import M
from ...parameters.data.theta import Theta

if TYPE_CHECKING:
    from ...type.alias import (IsCommodity, IsDerived, IsIndex, IsInput,
                               IsOperation, IsSpatial, IsValue)


def make_value(
    name: str,
    value: IsInput,
    index: IsIndex,
    bound: Bound,
    derived: IsDerived = None,
    commodity: IsCommodity = None,
    operation: IsOperation = None,
    spatial: IsSpatial = None,
) -> IsValue:
    """Converts a value to a Value object

    Args:
        name (str): name of the value
        value (IsInput): input value
        index (IsIndex): index of the value
        bound (Bound): bound of the value [UPPER, LOWER, EXACT]
        derived (IsDerived, optional): Derived Commodity. Defaults to None.
        commodity (IsCommmodity, optional): Commodity. Defaults to None.
        operation (IsOperation, optional): Operation. Defaults to None.
        spatial (IsSpatial, optional): Spatial. Defaults to None.

    Returns:
        IsValue: Value object
    """

    args = {
        'name': name,
        'index': index,
        'bound': bound,
        'derived': derived,
        'commodity': commodity,
        'operation': operation,
        'spatial': spatial,
    }

    if isinstance(value, (float, int)):
        return Number(number=value, **args)

    if isinstance(value, bool):
        return M(big=value, **args)

    if isinstance(value, DataFrame):
        return DataSet(data=value, **args)

    if isinstance(value, tuple):
        return Theta(space=value, **args)

    # if passing a BigM or Th, update
    if hasattr(value, 'big') or hasattr(value, 'space'):
        for i, j in args.items():
            setattr(value, i, j)
        return value
