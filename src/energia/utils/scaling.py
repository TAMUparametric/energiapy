"""Function for scaling input data"""

from typing import Literal

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def scaling(data: DataFrame, how: Literal['max', 'minmax', 'standard']) -> DataFrame:
    """Scales input DataFrame

    :param data: input data
    :type data: DataFrame
    :param how: 'max', 'minmax', 'standard'
    :type how: Literal['max', 'minmax', 'standard']

    :return: scaled DataFrame
    :rtype: DataFrame

    :raises ValueError: if data is not DataFrame
    """
    if not isinstance(data, DataFrame):
        raise ValueError("please provide DataFrame")

    if how == "max":
        data = data / data.max()

    else:
        if how == "standard":
            scaler = StandardScaler()
        if how == "minmax":
            scaler = MinMaxScaler()
        data = DataFrame(scaler.fit_transform(data))

    return data
