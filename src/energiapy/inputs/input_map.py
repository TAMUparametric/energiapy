from dataclasses import dataclass

from ..type.input.aspect import (CapBound, CashFlow, Emission, Land, Life,
                                 Limit, Loss)
from ..type.input.balance import Conv, MatUse
from ..type.input.detail import Detail


@dataclass
class CompAspectMap:
    """Tells what aspects need to be considered for components 
    """
    resource: list
    resource_at_process: list
    resource_at_storage: list
    resource_at_transport: list
    material: list
    operation: list
    spatial: list

    def __post_init__(self):
        # doing this because currently operation and spatial components share all Aspects
        for i in ['process', 'storage', 'transport']:
            setattr(self, i, self.operation)

        for i in ['location', 'linkage', 'network']:
            setattr(self, i, self.spatial)


comp_aspect_map = CompAspectMap(
    resource=Limit.resource() + CashFlow.resource() +
    Emission.all() + CapBound.all(),
    resource_at_process=Limit.resource() + CashFlow.resource() +
    CapBound.at_process(),
    resource_at_storage=CapBound.at_storage() + Loss.during_storage(),
    resource_at_transport=CapBound.at_transport() + Loss.during_transport(),
    material=Emission.all(),
    operation=Limit.operation() + Land.operation() + CashFlow.operation() +
    Emission.all() + Life.all(),
    spatial=Land.spatial() + CashFlow.spatial()
)


@dataclass
class InputMap:
    """Maps component attributes to aspects or balance or detail 
    """
    aspects: list
    comp_aspect_map: CompAspectMap
    details: list
    balances: list

    def __post_init__(self):
        for i in ['aspects', 'details', 'balances']:
            self.map_maker(i)

    def map_maker(self, attr: str):
        """makes a map between the attribute and the aspect or balance or detail
        """
        map_ = [{i.name.lower(): i for i in j} for j in getattr(self, attr)]
        setattr(self, f'{attr}_map', {
                i: j for k in map_ for i, j in k.items()})

    def find_aspect(self, attr: str):
        """finds the Aspect matching the input 
        """
        if attr in getattr(self, 'aspects_map'):
            return getattr(self, 'aspects_map')[attr]

    def is_conv(self, attr: str):
        """Is the input conversion 
        """
        if attr == 'conversion':
            return True
        else:
            return False

    def is_matuse(self, attr: str):
        """Is the input material consumed
        """
        if attr == 'material_use':
            return True
        else:
            return False

    def is_component_aspect(self, attr: str, component: str, at: str = ''):
        """Is the input a resource aspect
        """
        check = f'{component}_at_{at}'

        if self.find_aspect(attr) in getattr(self.comp_aspect_map, check):
            return True
        else:
            return False


input_map = InputMap(aspects=[Limit, CashFlow, Emission, CapBound, Loss, Life, Land],
                     comp_aspect_map=comp_aspect_map,
                     details=[Detail],
                     balances=[Conv, MatUse])
