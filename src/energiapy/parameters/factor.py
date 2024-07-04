"""Factor of deterministic data ftype
"""
from dataclasses import dataclass
from typing import Tuple, Union, Dict

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from ..components.temporal_scale import TemporalScale
from .type.disposition import *
from .type.property import *
from .type.special import SpecialParameter
from .type.variability import *


@dataclass
class Factor:
    """Deterministic data factor given to account for temporal variability in parameter. 
    changes data to a dictionary with keys being the scale index that matches the length of data 
    sets appropriate scale

    A Factor can also be defined externally and passed instead of a DataFrame. 
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

    data: Union[DataFrame, Dict[float, DataFrame]]
    scales: TemporalScale
    ptype: Property = None
    psubtype: Union[Limit, CashFlow, Land, Emission, Life, Loss] = None
    bounds: tuple = None
    component: Union['Resource', 'Process', 'Location',
                     'Transport', 'Network', 'Scenario'] = None
    spatial: SpatialDisp = None
    declared_at: Union['Process', 'Location',
                       'Transport', 'Network', 'Scenario'] = None
    apply_max_scaler: bool = None
    apply_min_max_scaler: bool = None
    apply_standard_scaler: bool = None

    def __post_init__(self):

        self.name = None

        self.special = SpecialParameter.FACTOR

        self.nominal = 1

        if isinstance(self.data, dict):
            self.nominal = list(self.data)[0]
            self.data = self.data[self.nominal]

        if isinstance(self.data, Factor):
            self.component = self.component
            self.scale = self.data.scale
            self.scaled = self.data.scaled
            self.data = self.data.data

        elif isinstance(self.data, DataFrame):
            if len(self.data) in self.scales.index_n_list:
                self.scale = self.scales.index_n_list.index(
                    len(self.data))
            else:
                raise ValueError(
                    f'{str(self.psubtype).lower()} factor for {self.component.name}: length of data does not match any scale index')

            self.data.index = self.scales.index_list[self.scale]

            if self.apply_min_max_scaler is None:
                self.apply_min_max_scaler = self.scales.scale_factors_min_max

            if self.apply_standard_scaler is None:
                self.apply_standard_scaler = self.scales.scale_factors_standard

            if self.apply_max_scaler is None:
                self.apply_max_scaler = self.scales.scale_factors_max

            if self.apply_min_max_scaler:
                scaler = MinMaxScaler()
                self.scaled = 'min_max'
                self.data = DataFrame(scaler.fit_transform(self.data), columns=self.data.columns).to_dict()[
                    self.data.columns[0]]

            elif self.apply_standard_scaler:
                scaler = StandardScaler()
                self.scaled = 'standard'
                self.data = DataFrame(scaler.fit_transform(self.data), columns=self.data.columns).to_dict()[
                    self.data.columns[0]]

            elif self.apply_max_scaler:
                self.scaled = 'max'
                self.data = self.data/self.data.max()
                self.data = self.data.to_dict()[self.data.columns[0]]

            else:
                self.scaled = 'no'
                self.data = self.data.to_dict()[self.data.columns[0]]

        else:
            raise ValueError(
                f'{str(self.psubtype.name).lower()} factor for {self.component.name}: please provide DataFrame')

        temporal_disps = TemporalDisp.all()

        if self.scale < 11:
            self.temporal = temporal_disps[self.scale]
        else:
            self.temporal = TemporalDisp.T10PLUS

        comp, dec_at, pst, temp = ('' for _ in range(4))

        if self.component:
            comp = f'{self.component.name}'

        if self.declared_at:
            dec_at = f',{self.declared_at.name}'

        elif self.spatial:
            dec_at = f',{self.spatial.name.lower()}'

        if self.psubtype:
            pst = f'{self.psubtype.name.lower().capitalize()}'

        if self.temporal:
            temp = f',{self.temporal.name.lower()}'

        self.name = f'{pst}({comp}{dec_at}{temp})'

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
