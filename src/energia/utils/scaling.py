"""Function for scaling input data"""

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def scaling(data: DataFrame, how: str) -> DataFrame:
    """Scales input DataFrame

    Args:
        data (DataFrame): input data
        how (str): 'max', 'minmax', 'standard'

    Returns:
        DataFrame: scaled DataFrame

    Raises:
        ValueError: if data is not a DataFrame

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
