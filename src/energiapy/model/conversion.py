import operator
from dataclasses import dataclass
from functools import reduce
from typing import Dict, Union

from ..components.resource import Resource
from ..utils.data_utils import get_depth
from .type.disposition import SpatialDisp


@dataclass
class Conversion:
    conversion: Union[Dict[Resource, Dict], Dict[Resource, float]]
    process: 'Process'

    def __post_init__(self):

        self.name = f'Conv|{self.process.name}|'

        if get_depth(self.conversion) > 2:
            self.produce = list(self.conversion)[0]
            self.n_modes = len(self.conversion[self.produce])
            self.modes = list(self.conversion[self.produce])
            self.involve = list(reduce(
                operator.or_, (set(self.conversion[self.produce][i]) for i in self.modes), set()))

            self.discharge = list(reduce(
                operator.or_, (set(j for j, k in self.conversion[self.produce][i].items() if k > 0) for i in self.modes), set()))
            self.consume = list(reduce(
                operator.or_, (set(j for j, k in self.conversion[self.produce][i].items() if k < 0) for i in self.modes), set()))

        elif get_depth(self.conversion) == 2:
            self.produce = list(self.conversion)[0]
            self.n_modes = 1
            self.modes = None
            self.involve = list(self.conversion[self.produce])

            self.discharge = [
                self.produce] + [i for i in self.conversion[self.produce] if self.conversion[self.produce][i] > 0]
            self.consume = [i for i in self.conversion[self.produce]
                            if self.conversion[self.produce][i] < 0]

        elif get_depth(self.conversion) == 1:
            self.n_modes = 1
            self.modes = None
            # TODO: Create Storage Resource and Process
            self.stored_resource = list(self.conversion)[0]
            self.produce = Resource(
                label=f'{self.stored_resource.label} stored in {self.process.label}')
            self.involve = [self.stored_resource, self.produce]
            
            # setattr(self.produce, 'horizon', self.stored_resource.horizon)
            # setattr(self.produce, 'name', f'{self.stored_resource.name}_in_{self.process.name}')

            # for i in ['store', 'store_loss', 'store_cost']:
            #     setattr(self.produce, i, getattr(self.process, i))

            # self.conversion = {self.produce: {
            #     self.stored_resource: self.conversion[self.stored_resource]}}
            # self.conversion_discharge = {
            #     self.stored_resource: {self.produce: 1}}

            # self.conversion = {self.produce: {
            #     self.produce: self.conversion[self.produce]}}
            self.discharge = [self.produce]
            self.consume = [self.stored_resource]

        self.name = f'Conv({self.produce.name},{self.process.name})'

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
