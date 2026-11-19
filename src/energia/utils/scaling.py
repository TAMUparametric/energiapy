"""Function for scaling input data"""

from typing import Literal

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def scaling(data: DataFrame, how: Literal['max', 'minmax', 'standard']) -> DataFrame:
    """Scale each DataFrame column independently and retain both axes.

    Max scaling divides by the column maximum, using the largest magnitude
    when the maximum is zero. All-zero columns remain zero.

    :param data: Input DataFrame.
    :param how: Scaling method, one of ``max``, ``minmax``, or ``standard``.
    :return: Scaled DataFrame with the input index and column labels.
    """
    if not isinstance(data, DataFrame):
        raise ValueError("please provide DataFrame")

    if how == "max":
        maxima = data.max()
        divisors = maxima.mask(maxima == 0, data.min().abs()).replace(0, 1)
        return data / divisors

    if how == "minmax":
        scaler = MinMaxScaler()
    elif how == "standard":
        scaler = StandardScaler()
    else:
        message = f"Unknown scaling method {how!r}"
        raise ValueError(message)
    values = scaler.fit_transform(data.to_numpy(na_value=float("nan")))
    return DataFrame(values, index=data.index, columns=data.columns)
