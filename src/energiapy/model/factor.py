"""Factor of deterministic data ftype
"""
from dataclasses import dataclass
from typing import Tuple, Union, Dict

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from ..components.temporal_scale import TemporalScale
from .type.disposition import SpatialDisp, TemporalDisp
from .type.aspect import Limit, CashFlow, Land, Emission, Life, Loss
from .type.special import SpecialParameter
from .type.variability import Variability, Uncertain
from .type.bound import Bound


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
    aspect: Union[Limit, CashFlow, Land, Emission, Life, Loss] = None
    bounds: tuple = None
    component: Union['Resource', 'Process', 'Location',
                     'Transport', 'Network', 'Scenario'] = None
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
            if not self.scales:
                raise ValueError(
                    f'{str(self.aspect).lower()} for {self.component.name}: please provide scales = TemporalScale')

            if len(self.data) in self.scales.index_n_list:
                self.scale = self.scales.index_n_list.index(
                    len(self.data))
            else:
                raise ValueError(
                    f'{str(self.aspect).lower()} for {self.component.name}: length of data does not match any scale index')

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
                f'{str(self.aspect.name).lower()} factor for {self.component.name}: please provide DataFrame')

        temporal_disps = TemporalDisp.all()

        if self.scale < 11:
            self.temporal = temporal_disps[self.scale]
        else:
            self.temporal = TemporalDisp.T10PLUS

        comp, dec_at, par = ('' for _ in range(3))

        temp = f'{self.temporal.name.lower()}'

        if self.aspect:
            if self.declared_at.class_name() in ['Process', 'Location', 'Linkage']:
                if self.declared_at.class_name() != self.component.class_name():
                    self.spatial = (getattr(SpatialDisp, self.component.class_name(
                    ).upper()), getattr(SpatialDisp, self.declared_at.class_name().upper()))
                else:
                    self.spatial = getattr(
                        SpatialDisp, self.declared_at.class_name().upper())
            else:
                self.spatial = SpatialDisp.NETWORK
            
            self.disposition = ((self.spatial), self.temporal)

            par = f'{self.aspect.name.lower().capitalize()}'
            comp = f'{self.component.name}'
            dec_at = f'{self.declared_at.name}'

            self.index = tuple(dict.fromkeys([comp, dec_at, temp]).keys())
            self.name = f'{par}{self.index}'

        else:
            self.name = f'Data({temp})'

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
