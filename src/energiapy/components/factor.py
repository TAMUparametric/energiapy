"""Factor of deterministic data 
"""
from dataclasses import dataclass
from typing import Union
from .comptype import FactorType
from .resource import Resource
from .process import Process
from .temporal_scale import TemporalScale
from warnings import warn
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from pandas import DataFrame


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
        component (Union[Process, Resource, Location, Transport], optional): energiapy component that experiences variability. Do not define for user defined factors. Defaults to None
        ctype (FactorType): check energiapy.components.comptype 
        apply_min_max_scaler (bool, optional): This is inherited form the scales object if not provided, where it defaults to True.
        apply_standard_scaler (bool, optional): This is inherited form the scales object if not provided, where it defaults to False.
    """
    
    data: DataFrame
    scales: TemporalScale
    component: Union[Process, Resource, 'Location', 'Transport'] = None
    ctype: FactorType = None
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
            self.name = f'{self.component.name}_{str(self.ctype).lower()}_factor'.replace(
                'factortype.', '')
            print('a')

        else:
            if self.component is not None:
                if isinstance(self.data, DataFrame) is False:
                    warn(
                        f'{str(self.ctype).lower()} factor for {self.component.name}: please provide DataFrame')
                self.name = f'{self.component.name}_{str(self.ctype).lower()}_factor'.replace(
                    'factortype.', '')
            else:
                if isinstance(self.data, DataFrame) is False:
                    warn(f'{str(self.ctype).lower()}: please provide DataFrame')
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
                        list(self.data)[0]]

                elif self.apply_standard_scaler is True:
                    scaler = StandardScaler()
                    self.scaled = 'standard'
                    self.data = DataFrame(scaler.fit_transform(self.data), columns=self.data.columns).to_dict()[
                        list(self.data)[0]]

                elif self.apply_max_scaler is True:
                    self.scaled = 'max'
                    self.data = self.data/self.data.max()
                    self.data = self.data.to_dict()[list(self.data)[0]]

                else:
                    self.scaled = 'no'
                    self.data = self.data.to_dict()[list(self.data)[0]]

            else:
                warn(f'{str(self.ctype).lower()} factor for {self.component.name}: length of data does not match any scale index'.replace(
                    'factortype.', ''))

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
