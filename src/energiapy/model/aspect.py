
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
        self.index = None
        self.spatial = None
        self.temporal = None
        self.disposition = None
    
    
    def add(self, value: Union[float, bool, 'BigM', List[float], List[Union[float, 'BigM']],
                 DataFrame, Dict[float, DataFrame], Dict[float, Factor], Tuple[float], Theta], aspect: Union[Limit, CashFlow, Land, Life, Loss, Emission],
            component: Union['Resource', 'Process', 'Location', 'Transport', 'Network'], 
            declared_at: Union['Resource', 'Process', 'Location', 'Transport', Tuple['Location'], 'Network'], 
            temporal: Union[TemporalDisp, int] = 0, scales: TemporalScale = None):

        parameter = Parameter(value=value, aspect=aspect, temporal=temporal, component=component,
                            scales=scales, declared_at=declared_at)
        
        for i in ['index', 'temporal', 'spatial', 'disposition']:
            setattr(self, i, getattr(parameter, i))
        
        if parameter not in self.parameters:
            self.parameters.append(parameter)
        
        for i in matches.find(aspect):
            variable_, associated_, parameter_, bound_, lb_, ub_ = (None for _ in range(6))
                    
            bound_ = parameter.bound
            
            if i.variable:
                variable_ = Variable(aspect=aspect, component=component, declared_at=declared_at, spatial=parameter.spatial, temporal=parameter.temporal, disposition=parameter.disposition, index=parameter.index)
                if variable_ not in self.variables:    
                    self.variables.append(variable_)

            if i.associated:
                associated_ = Variable(aspect=i.associated, component=component, declared_at=declared_at, spatial=parameter.spatial, temporal=parameter.temporal, disposition=parameter.disposition, index=parameter.index)
            
            if i.parameter:
                parameter_ = parameter
                lb_ = parameter.lb
                ub_ = parameter.ub
            
            
            constraint_ =  Constraint(condition=i.condition, variable=variable_, associated=associated_, parameter=parameter_, bound=bound_, lb=lb_, ub= ub_)
            
            # print(i, variable_, associated_, parameter_, constraint_)
            if constraint_ not in self.constraints:
                self.constraints.append(constraint_)
    

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
    

@dataclass
class AspectOver:
    aspect: Union[Limit, Loss] 
    temporal: TemporalDisp
    
    def __post_init__(self):
        self.name = f'{self.aspect.name.lower()}_over:{self.temporal.name.lower()}'

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
