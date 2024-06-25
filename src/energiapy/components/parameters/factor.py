"""Factor of deterministic data ftype
"""
from dataclasses import dataclass
from typing import Tuple, Union

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from ..temporal_scale import TemporalScale
from .paramtype import FactorType


@dataclass
class Factor:
    """Deterministic data factor given to account for temporal variability in parameter. 
    changes data to a dictionary with keys being the scale index that matches the length of data 
    sets appropriate scale_level

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

    data: DataFrame
    scales: TemporalScale
    component: Union['Process', 'Resource', 'Location', 'Transport'] = None
    location: Union['Location', Tuple['Location', 'Location']] = None
    ftype: FactorType = None
    apply_max_scaler: bool = None
    apply_min_max_scaler: bool = None
    apply_standard_scaler: bool = None

    def __post_init__(self):

        self.name = None

        if hasattr(self.data, 'dont_redef'):
            self.component = self.component
            self.scale_level = self.data.scale_level
            self.scaled = self.data.scaled
            self.data = self.data.data
            if isinstance(self.location, tuple):
                self.name = f'{self.component.name}_({self.location[0].name},{self.location[1].name})_{str(self.ftype).lower()}_factor'.replace(
                    'factortype.', '')
            else:
                self.name = f'{self.component.name}_{self.location.name}_{str(self.ftype).lower()}_factor'.replace(
                    'factortype.', '')

        else:
            if self.component is not None:
                if isinstance(self.data, DataFrame) is False:
                    raise ValueError(
                        f'{str(self.ftype).lower()} factor for {self.component.name}: please provide DataFrame')

                if isinstance(self.location, tuple):
                    self.name = f'{self.component.name}_({self.location[0].name},{self.location[1].name})_{str(self.ftype).lower()}_factor'.replace(
                        'factortype.', '')
                else:
                    self.name = f'{self.component.name}_{self.location.name}_{str(self.ftype).lower()}_factor'.replace(
                        'factortype.', '')
            else:
                if isinstance(self.data, DataFrame) is False:
                    raise ValueError(
                        f'{str(self.ftype).lower()}: please provide DataFrame')
                self.dont_redef = True

            if len(self.data) in self.scales.index_n_list:
                self.scale_level = self.scales.index_n_list.index(
                    len(self.data))
                self.data.index = self.scales.index_list[self.scale_level]

                if self.apply_min_max_scaler is None:
                    self.apply_min_max_scaler = self.scales.scale_factors_min_max

                if self.apply_standard_scaler is None:
                    self.apply_standard_scaler = self.scales.scale_factors_standard

                if self.apply_max_scaler is None:
                    self.apply_max_scaler = self.scales.scale_factors_max

                if self.apply_min_max_scaler is True:
                    scaler = MinMaxScaler()
                    self.scaled = 'min_max'
                    self.data = DataFrame(scaler.fit_transform(self.data), columns=self.data.columns).to_dict()[
                        self.data.columns[0]]

                elif self.apply_standard_scaler is True:
                    scaler = StandardScaler()
                    self.scaled = 'standard'
                    self.data = DataFrame(scaler.fit_transform(self.data), columns=self.data.columns).to_dict()[
                        self.data.columns[0]]

                elif self.apply_max_scaler is True:
                    self.scaled = 'max'
                    self.data = self.data/self.data.max()
                    self.data = self.data.to_dict()[self.data.columns[0]]

                else:
                    self.scaled = 'no'
                    self.data = self.data.to_dict()[self.data.columns[0]]

            else:
                raise ValueError(f'{str(self.ftype).lower()} factor for {self.component.name}: length of data does not match any scale index'.replace(
                    'factortype.', ''))

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
