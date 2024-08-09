from __future__ import annotations

from typing import TYPE_CHECKING

from pandas import DataFrame

from ...inputs.values.constant import Number
from ...inputs.values.dataset import DataSet
from ...inputs.values.m import M
from ...inputs.values.theta import Theta
from ...model.index import Index

if TYPE_CHECKING:
    from ..type.alias import IsIndex, IsInput, IsSpcLmt, IsValue, IsVarBnd


def birth_value(name: str, attr_input: IsInput, index: IsIndex) -> IsValue:
    """Converts a value to a Value object

    Args:
        name (str): name of the value
        attr_input (IsInput): input value
        index (IsIndex): index of the value

    Returns:
        IsValue: Value object
    """

    args = {'name': name, 'index': index}

    if isinstance(attr_input, (float, int)) and not isinstance(attr_input, bool):
        return Number(number=attr_input, **args)

    if isinstance(attr_input, bool):
        return M(big=attr_input, **args)

    if isinstance(attr_input, DataFrame):
        return DataSet(data=attr_input, **args)

    if isinstance(attr_input, tuple):
        return Theta(space=attr_input, **args)

    # if passing a BigM or Th, update
    if hasattr(attr_input, 'big') or hasattr(attr_input, 'space'):
        for i, j in args.items():
            setattr(attr_input, i, j)
        return attr_input
