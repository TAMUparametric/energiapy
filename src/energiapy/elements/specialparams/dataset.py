"""DataSet is a deterministic data given to account for temporal variability in parameter.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from ...core.general import Dunders
from ...type.element.bound import Bound
from ..index import Index

if TYPE_CHECKING:
    from ...components.horizon import Horizon
    from ...type.alias import IsAspect, IsComponent, IsData, IsDeclaredAt


@dataclass
class DataSet(Dunders):
    """
    Args:
        data (IsData): Data to be used
        horizon (Horizon): Horizon of the data
        aspect (IsAspect, optional): Aspect of the data. Defaults to None.
        bound (Bound, optional): Bound of the data. Defaults to None.
        component (IsComponent, optional): Component of the data. Defaults to None.
        declared_at (IsComponent, optional): Component where the data is declared. Defaults to None.
        scaling_max (bool, optional): Scale the data to maximum value. Defaults to None.
        scaling_min_max (bool, optional): Scale the data to minimum and maximum value. Defaults to None.
        scaling_standard (bool, optional): Scale the data to standard value. Defaults to None.
    """
    data: IsData
    horizon: Horizon
    aspect: IsAspect = None
    bound: Bound = None
    component: IsComponent = None
    declared_at: IsDeclaredAt = None
    scaling_max: bool = None
    scaling_min_max: bool = None
    scaling_standard: bool = None

    def __post_init__(self):

        self.name = None

        if isinstance(self.data, DataSet):
            self.scaled = self.data.scaled
            self.temporal = self.data.temporal
            self.data = self.data.data

        elif isinstance(self.data, DataFrame):

            if not self.horizon:
                raise ValueError(
                    f'{str(self.aspect).lower()} for {self.component.name}: please provide scales = Scale')

            if len(self.data) in self.horizon.n_indices:
                index = self.horizon.n_indices.index(len(self.data))
                self.temporal = self.horizon.scales[index]
                self.data.index = self.horizon.indices[self.temporal]

            else:
                raise ValueError(
                    f'{str(self.aspect).lower()} for {self.component.name}: length of data does not match any scale index')

            for i in ['scaling_max', 'scaling_min_max', 'scaling_standard']:
                if getattr(self, i) is None:
                    setattr(self, i, getattr(self.horizon, i))

            if self.scaling_min_max:
                scaler = MinMaxScaler()
                self.scaled = 'min_max'
                data_array = scaler.fit_transform(self.data)
                data_list = [i for j in data_array.tolist() for i in j]
                self.data = {list(self.data.index)[
                    i]: j for i, j in enumerate(data_list)}

            elif self.scaling_standard:
                scaler = StandardScaler()
                self.scaled = 'standard'
                data_array = scaler.fit_transform(self.data)
                data_list = [i for j in data_array.tolist() for i in j]
                self.data = {list(self.data.index)[
                    i]: j for i, j in enumerate(data_list)}

            elif self.scaling_max:
                self.scaled = 'max'
                self.data = self.data/self.data.max()
                self.data = self.data.to_dict()[self.data.columns[0]]

            else:
                self.scaled = 'no'
                self.data = self.data.to_dict()[self.data.columns[0]]

        else:
            raise ValueError(
                f'{str(self.aspect.name).lower()} factor for {self.component.name}: please provide DataFrame, DataSet, or a dict of either with the nominal value as key')

        if self.aspect:

            self.index = Index(
                component=self.component, declared_at=self.declared_at, temporal=self.temporal)

            self.name = f'DSet|{self.aspect.pnamer()}{self.bound.namer()}{self.index.name}|'

        else:
            temp = f'{self.temporal.name.lower()}'
            self.name = f'DSet|{temp}|'

    def __len__(self):
        if hasattr(self, 'index'):
            return len(self.index)
        else:
            return len(self.data)

    def __lt__(self, other):
        if isinstance(other, (int, float)) and self.bound == Bound.UPPER:
            return False
        elif isinstance(other, DataSet) and other.bound == Bound.LOWER:
            return False
        else:
            return True

    def __gt__(self, other):
        if isinstance(other, (int, float)) and self.bound == Bound.UPPER:
            return True
        elif isinstance(other, DataSet) and other.bound == Bound.LOWER:
            return True
        else:
            return False
