"""Varying factor 
"""
from dataclasses import dataclass
from typing import Union
from .comptype import FactorType
from .resource import Resource
from .process import Process
from .temporal_scale import TemporalScale


@dataclass
class Factor:
    component: Union[Process, Resource, 'Location']
    data: dict
    ctype: FactorType
    scales: TemporalScale
    normalize: bool = True 

    def __post_init__(self):
        self.name = f'{self.component.name}_{str(self.ctype).lower()}_factor'.replace(
            'FactorType.', '')
        self.scale_level = self.scales.index_n_list.index(len(self.data))
        self.data.index = self.scales.index_list[self.scale_level]
        
        if self.normalize is True:
            self.data = self.data.apply(lambda x: x/x.max(), axis=0)

        self.data = self.data.to_dict()[list(self.data)[0]]

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
