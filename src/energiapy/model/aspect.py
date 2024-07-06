
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union
from .parameter import Parameter
from .variable import Variable
from .constraint import Constraint
from .type.aspect import Limit, CashFlow, Land, Life, Loss, Emission
from ..components.temporal_scale import TemporalScale
from pandas import DataFrame
from .factor import Factor
from .theta import Theta
from .type.disposition import SpatialDisp, TemporalDisp
from .type.match import matches


@dataclass
class Aspect:
    
    aspect: Union[Limit, CashFlow, Land, Life, Loss, Emission]
    component: Union['Resource', 'Process', 'Location', 'Transport', 'Network']       
    
    def __post_init__(self):
        self.name = f'{self.aspect.name.lower().capitalize()}({self.component.name})'
        self.parameters= list()
        self.variables= list()
        self.constraints= list()
        self.dispositions = list()
        self.indices = list()

    
    
    def add(self, value: Union[float, bool, 'BigM', List[float], List[Union[float, 'BigM']],
                 DataFrame, Dict[float, DataFrame], Dict[float, Factor], Tuple[float], Theta], aspect: Union[Limit, CashFlow, Land, Life, Loss, Emission],
            component: Union['Resource', 'Process', 'Location', 'Transport', 'Network'], 
            declared_at: Union['Resource', 'Process', 'Location', 'Transport', Tuple['Location'], 'Network'], 
            temporal: Union[TemporalDisp, int] = 0, scales: TemporalScale = None):
        
        parameter = Parameter(value=value, aspect=aspect, temporal=temporal, component=component,
                                  scales=scales, declared_at=declared_at)
        
        self.parameters.append(parameter)
        
        for i in matches.find(aspect):
            variable, associated = None, None
            if i.variable:
                variable = Variable(aspect=aspect, component=component, declared_at=declared_at, spatial=parameter.spatial, temporal=parameter.temporal, disposition=parameter.disposition, index=parameter.index)
                self.variables.append(variable)

            if i.associated:
                associated = Variable(aspect=i.associated, component=component, declared_at=declared_at, spatial=parameter.spatial, temporal=parameter.temporal, disposition=parameter.disposition, index=parameter.index)
            
            constraint =  Constraint(condition=i.condition, variable=variable, associated=associated, parameter=parameter, bound=parameter.bound, lb=parameter.lb, ub= parameter.ub)
            
            self.constraints.append(constraint)
    
    

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name