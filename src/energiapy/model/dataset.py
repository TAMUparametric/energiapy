"""Deterministic data set ftype
"""
from dataclasses import dataclass
from typing import Union

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from ..components.horizon import Horizon
from .type.aspect import CashFlow, Emission, Land, Life, Limit, Loss
from .type.bound import Bound
from .type.disposition import SpatialDisp, TemporalDisp
from .type.special import SpecialParameter
from .index import Index


@dataclass
class DataSet:
    """Deterministic data given to account for temporal variability in parameter. 
    changes data to a dictionary with keys being the scale index that matches the length of data 
    sets appropriate scale

    DataSet can also be defined externally and passed instead of a DataFrame. 
    In this case, only provide data, scales, and whether to apply any scaler [max, min_max, standard]

    Args:
        data (DataFrame): varying data. The length of data needs to match one of the scale indices. Check TemporalScale.index_n_list
        scales (TemporalScale): The planning horizon 
        component (Union[Process, Resource, Location, Transport], optional): energiapy component that experiences variability. Do not define for user defined factors. Defaults to None.
        location (Union['Location', Tuple['Location', 'Location']], optional): Location or tuple of locations for transport factors
        ftype (FactorType): type of factor 
        apply_min_max_scaler (bool, optional): This is inherited form the scales object if not provided, where it defaults to True.
        apply_standard_scaler (bool, optional): This is inherited form the scales object if not provided, where it defaults to False.
    """

    data: Union[DataFrame, 'DataSet']
    horizon: Horizon
    aspect: Union[Limit, CashFlow, Land, Emission, Life, Loss] = None
    bound: Bound = None
    component: Union['Resource', 'Process', 'Location',
                     'Transport', 'Network', 'Scenario'] = None
    declared_at: Union['Process', 'Location',
                       'Transport', 'Network', 'Scenario'] = None
    scaling_max: bool = None
    scaling_min_max: bool = None
    scaling_standard: bool = None

    def __post_init__(self):

        self.name = None

        self.special = SpecialParameter.DATASET

        if isinstance(self.data, DataSet):
            self.scaled = self.data.scaled
            self.temporal = self.data.temporal
            self.data = self.data.data

        elif isinstance(self.data, DataFrame):

            if not self.horizon:
                raise ValueError(
                    f'{str(self.aspect).lower()} for {self.component.name}: please provide scales = TemporalScale')

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
                self.data = DataFrame(scaler.fit_transform(self.data), columns=self.data.columns).to_dict()[
                    self.data.columns[0]]

            elif self.scaling_standard:
                scaler = StandardScaler()
                self.scaled = 'standard'
                self.data = DataFrame(scaler.fit_transform(self.data), columns=self.data.columns).to_dict()[
                    self.data.columns[0]]

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
            if self.declared_at.cname() in ['Process', 'Location', 'Linkage']:
                if self.declared_at.cname() != self.component.cname():
                    self.spatial = (getattr(SpatialDisp, self.component.class_name(
                    ).upper()), getattr(SpatialDisp, self.declared_at.cname().upper()))
                else:
                    self.spatial = getattr(
                        SpatialDisp, self.declared_at.cname().upper())
            else:
                self.spatial = SpatialDisp.NETWORK

            self.disposition = ((self.spatial), self.temporal)

            self.index = Index(component=self.component, declared_at=self.declared_at, temporal=self.temporal,
                               spatial=self.spatial, disposition=self.disposition, length=len(self.data))

            par = f'{self.aspect.name.lower().capitalize()}'

            if self.bound == Bound.LOWER:
                bnd = '_lb'
            elif self.bound == Bound.UPPER:
                bnd = '_ub'
            else:
                bnd = ''

            self.name = f'DSet|{par}{bnd}{self.index.name}|'

        else:
            temp = f'{self.temporal.name.lower()}'
            self.name = f'DSet|{temp}|'

    def __len__(self):
        if hasattr(self, 'index'):
            return self.index.length
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

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
