from dataclasses import dataclass
from ..components.resource import Resource
from typing import Dict, Union
from ..utils.data_utils import get_depth
from functools import reduce
import operator
from .type.disposition import SpatialDisp


@dataclass
class Conversion:
    conversion: Union[Dict[Resource, Dict], Dict[Resource, float]]
    process: 'Process'

    def __post_init__(self):

        self.base = list(self.conversion)[0]

        if get_depth(self.conversion) > 2:
            self.n_modes = len(self.conversion[self.base])
            self.modes = list(self.conversion[self.base])
            self.involve = reduce(
                operator.or_, (set(self.conversion[self.base][i]) for i in self.modes), set())
        elif get_depth(self.conversion) == 2:
            self.n_modes = 1
            self.modes = None
            self.involve = set(self.conversion[self.base])
        elif get_depth(self.conversion) == 1:
            self.n_modes = 1
            self.modes = None
            self.involve = self.create_storage_resource()
            self.conversion = {self.involve: {
                self.base: self.conversion[self.base]}}

        self.name = f'Conv({self.base.name},{self.process.name})'

    def create_storage_resource(self) -> Resource:
        """Creates a resource for storage, used if ProcessType is STORAGE

        Args:
            resource (Resource): Resource to be stored
        Returns:
            Resource: of ResourceType.STORE, named Process.name_Resource.name_stored
        """

        return Resource(name=f"{self.process.name}_{self.base.name}_stored", store_loss=self.process.store_loss, store=self.process.store,
                        store_cost=self.process.store_cost, store_loss_scale=self.base.store_loss_scale,
                        store_scale=self.base.store_loss_scale, label=f'{self.base.label} stored in {self.process.label}')

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
