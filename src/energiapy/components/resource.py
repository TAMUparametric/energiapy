"""energiapy.Resource - Resource as refined in the RT(M)N framework  
"""
import uuid
from dataclasses import dataclass
from typing import List, Tuple, Union

from pandas import DataFrame

from ..model.bound import Big, BigM
from ..model.factor import Factor
from ..model.theta import Theta
from ..model.parameter import Parameter
from ..model.aspect import Aspect, AspectOver
from ..model.type.aspect import Limit, CashFlow, Emission, Loss
from ..model.type.disposition import SpatialDisp, TemporalDisp
from .temporal_scale import TemporalScale
from .type.resource import ResourceType


@dataclass
class Resource:
    """Object with resource data that can be consumed (purchased if consumed at a price), discharged (sold if revenue is generated), 
    stored, used or made by process, transported.

    The emission potentials [gwp, odp, acid, eutt, eutf, eutm] can also be provided
    Given that maximum consumption (consume), purchase price, and sell price can vary by location,
    localization can be achieved by providing the consume_localize, purchase_cost_localize, and sell_cost_localize
    at Location level

    Demand needs to be declared at Location

    Args:
        name (str): name of resource. Enter None to randomly assign a name.
        discharge (Union[float, Tuple[float], Theta, bool, 'Big'], optional): if can be discharged or sold. Defaults to None
        sell_cost (Union[float, Tuple[float], Theta], optional): revenue if generated on selling. Defaults to None
        purchase_cost (Union[float, Tuple[float], Theta], optional): purchase price.Defaults to None
        consume (Union[float, Tuple[float], Theta, bool, 'Big'], optional): maximum amount that can be consumed. Defaults to None
        store_max (Union[float, Tuple[float], Theta, bool, 'Big'], optional): maximum amount that can be stored in inventory. Defaults to None
        store_min (float, optional): minimum amount of that is need to setup inventory. Defaults to None
        store_loss (float, optional): amount lost in inventory per time period of the scheduling scale. Defaults to None
        storage_cost: (float, optional): penalty for mainting inventory per time period in the scheduling scale. Defaults to None.
        transport (bool, optional): if can be transported, also determined if mentioned while defining Transport. Defaults to None
        gwp (Union[float, Tuple[float], Theta], optional): global warming potential. Defaults to None.
        odp (Union[float, Tuple[float], Theta], optional): ozone depletion potential. Defaults to None.
        acid (Union[float, Tuple[float], Theta], optional): acidification potential. Defaults to None.
        eutt (Union[float, Tuple[float], Theta], optional): terrestrial eutrophication potential. Defaults to None.
        eutf (Union[float, Tuple[float], Theta], optional): fresh water eutrophication potential. Defaults to None.
        eutm (Union[float, Tuple[float], Theta], optional): marine eutrophication potential. Defaults to None.
        basis (str, optional): unit in which resource is measured. Defaults to None 
        block (Union[str, list, dict], optional): block to which it belong. Convinient to set up integer cuts. Defaults to None
        label (str, optional): used while generating plots. Defaults to None
        citation (str, optional): can provide citations for your data sources. Defaults to None
        ctype (List[Union[ResourceType, Dict[ResourceType, Set['Location']]]], optional): List of resource ctypes. Defaults to None
        aspect (Dict[ResourceParamType, Union[Aspect, Dict['Location', Aspect]]], optional): dict with parameters declared and thier types. Defaults to None.
        ltype (Dict[ResourceParamType, List[Tuple['Location', LocalizationType]]], optional): which parameters are localized at Location. Defaults to None.
        ftype (Dict[ResourceParamType, List[Tuple['Location', Aspect]]], optional): which parameters are provided with factors at Location. Defaults to None
        etype (List[EmissionType], optional): list of emission types defined. Defaults to None
        localizations (Dict[ResourceParamType, List[Tuple['Location', Localization]]], optional): collects localizations when defined at Location. Defaults to None.
        factors (Dict[ResourceParamType, List[Tuple['Location', Factor]]], optional): collects factors when defined at Location. Defaults to None.
        emissions (Dict[str, float], optional): collects emission data. Defaults to None.

    Examples:

        [1] A resource that can be consumed is declared by setting a consume 

        >>> Solar = Resource(name='Solar', consume= 100)

        [2] A resource that can be purchase need a price to be set, besides consume.

        >>> Water = Resource(name='H2O', consume= 100, purchase_cost= 20)

        [3] If the resource can be discharged.

        >>> CO2 = Resource(name='CO2', discharge = True)

        [4] If the resource can be sold. A selling price is set along with sell = True.

        >>> Power = Resource(name='Power', discharge = True, sell_cost = 0.2)

        [5] Additional attributes can be added. Note that this resource is only used implicitly in the system. 

        >>> H2 = Resource(name='H2', basis = 'tons', label = 'Hydrogen', block= 'DEC', citation = 'Kakodkar, et. al (2024)')

        [6] A storage resource can be declared here. Or a resource can be given to a storage type Process which generates a stored resource

        >>> Money= Resource(name='Poishe', basis = 'Rupees', store_max= 2, store_min = 0, store_loss = 0.01)

        [7] Uncertainty in resource parameters for selling price, availability, and purchase price can be handled by either:

        1. Providing deterministic dataset for variablity at the Location level 

        OR through:

        2. Multiparameteric programming (mpP). To declare a parameteric variable, either give ranges for data (as tuples )instead of floats
        or insert energiapy.Theta(bounds = (_, _)) in place of the parameter.

        For example, if the availability of water is uncertain:

        >>>  H2 = Resource(name='H2', discharge = True, sell_cost = (0, 10)) 

        or 

        >>> H2 = Resource(name='H2', discharge = True, sell_cost = Theta(bounds = (0, 10)))

        Multiple parameters of a resource can also be uncertain. As shown here, where water has both uncertain availability as well as price.

        >>> Water = Resource(name='H2O', consume= Theta((0, 45)), purchase_cost= Theta((0, 3))) 

        [8] Environmental impact potentials can also be declared for resources

        >>> NaturalGas = Resource(name = 'NG', consume = 1000, gwp = 30, odp = 50, acid = 20, eutt = 5, eutf = 60, eutm = 10)

    """

    name: str
    # Temporal scale
    # not needed if no deterministic data or parameter scale is provided
    scales: TemporalScale = None
    # LimitType
    discharge: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                     DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    consume: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                   DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    store: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                 DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    transport:  Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                      DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    # LossType
    store_loss: Union[float, Tuple[float], Theta] = None
    # Temporal Scale over which limit is set
    # or loss is incurred
    discharge_over: int = None
    consume_over: int = None
    store_over: int = None
    transport_over: int = None
    store_loss_over : int = None
    # CashFlowType
    sell_cost: Union[float, Theta, DataFrame,
                     Tuple[Union[float, DataFrame, Factor]]] = None
    purchase_cost: Union[float, Theta, DataFrame,
                         Tuple[Union[float, DataFrame, Factor]]] = None
    store_cost: Union[float, Theta, DataFrame,
                      Tuple[Union[float, DataFrame, Factor]]] = None
    credit: Union[float, Theta, DataFrame,
                  Tuple[Union[float, DataFrame, Factor]]] = None
    penalty: Union[float, Theta, DataFrame,
                   Tuple[Union[float, DataFrame, Factor]]] = None
    # EmissionType
    gwp: Union[float, Tuple[float], Theta] = None
    odp: Union[float, Tuple[float], Theta] = None
    acid: Union[float, Tuple[float], Theta] = None
    eutt: Union[float, Tuple[float], Theta] = None
    eutf: Union[float, Tuple[float], Theta] = None
    eutm: Union[float, Tuple[float], Theta] = None
    # Details
    basis: str = None
    block: Union[str, list, dict] = None
    label: str = None
    citation: str = None
    # Types
    ctype: List[ResourceType] = None

    constraints: List[str] = None
    # Depreciated
    sell: bool = None
    varying: bool = None
    price: bool = None
    revenue: bool = None
    cons_max: bool = None
    store_max: bool = None
    store_min: bool = None

    def __post_init__(self):

        if not self.constraints:
            self.constraints = list()
        # *-----------------Set ctype (ResourceType)---------------------------------
        # .DISCHARGE allows the resource to be discharged (consume > 0)
        # .SELL is when a Resource generated revenue (has a sell_cost)
        # .CONSUME is when a Resource can be consumed
        # .PURCHASE is when a consumed Resource has a purchase_cost
        # .IMPLICIT is when a Resource only exists insitu (not discharged or consumed)
        # .PRODUCED is when a Resource is produced by a Process
        # .SELL and .DEMAND imply that .DISCHARGE is True
        # .STORE is set if a store_max is given
        # .DEMAND is set if a specific demand for resource is declared at Location
        # .TRANSPORT is set if a Resource is in the set Transport.resources
        # storage resources are also generated implicitly if a Resource is provided to a Process as storage

        if not self.ctype:
            self.ctype = list()

        if self.sell_cost is not None:
            self.ctype.append(ResourceType.SELL)
            if self.discharge is None:
                self.discharge = BigM

        if self.discharge is not None:
            self.ctype.append(ResourceType.DISCHARGE)

        if self.consume is not None:
            self.ctype.append(ResourceType.CONSUME)
        else:
            # if it is not consumed from outside the system, it has to be made in the system
            self.ctype.append(ResourceType.PRODUCE)
            if self.discharge is None:
                # is not discharged or consumed. Produced and used within the system captively
                self.ctype.append(ResourceType.IMPLICIT)

        if self.purchase_cost:
            self.ctype.append(ResourceType.PURCHASE)
            if self.consume is None:
                self.consume = BigM

        if self.store is not None:
            self.ctype.append(ResourceType.STORE)

        # *----------------- Update Aspect ---------------------------------

        for i in self.all():  # iter over all aspects
            asp_ = i.name.lower()  # get name of aspect            
            if getattr(self, asp_) is not None:
                attr = getattr(self, asp_)
                temporal = None
                if i in self.limits() + self.losses():
                    temporal = getattr(self, f'{asp_}_over')

                aspect = Aspect(aspect=i, component=self)
                aspect.add(value=attr, aspect=i, temporal=temporal, component=self,
                           scales=self.scales, declared_at=self)
                setattr(self, asp_, aspect)
                
                if i in self.limits() + self.losses():
                    setattr(self, f'{asp_}_over', AspectOver(aspect=i, temporal=aspect.temporal))
                

        # *-----------------Random name ---------------------------------
        # A random name is generated if self.name = None

        if not self.name:
            self.name = f'{self.class_name()}_{uuid.uuid4().hex}'

        # *----------------- Depreciation Warnings---------------------------------

        if self.store_max:
            raise ValueError(
                f'{self.name}: store_max is depreciated. Please use store instead')
        if self.store_min:
            raise ValueError(
                f'{self.name}: store_min is depreciated. Please use store instead')
        if self.cons_max:
            raise ValueError(
                f'{self.name}: cons_max is depreciated. Please use consume instead')
        if self.sell:
            raise ValueError(
                f'{self.name}: sell has been depreciated. set discharge = True and specify selling_price if needed')
        if self.varying:
            raise ValueError(
                f'{self.name}: varying has been depreciated. Variability will be intepreted based on data provided to energiapy.Location factors')
        if self.price:
            raise ValueError(
                f'{self.name}: price has been depreciated. Please use purchase_cost instead')
        if self.revenue:
            raise ValueError(
                f'{self.name}: revenue has been depreciated. Please use sell_cost instead')
        if self.revenue:
            raise ValueError(
                f'{self.name}: cons_max has been depreciated. Please use consume instead')

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if hasattr(getattr(self, name), 'constraints'):
            self.constraints.extend(getattr(self, name).constraints)

    def cons(self):
        for j in self.constraints:
            print(j)

    # *----------------- Class Methods ---------------------------------

    @classmethod
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__

    @classmethod
    def limits(cls) -> List[str]:
        return Limit.resource()

    @classmethod
    def cashflows(cls) -> List[str]:
        return CashFlow.resource()

    @classmethod
    def emissions(cls) -> List[str]:
        return Emission.all()

    @classmethod
    def losses(cls) -> List[str]:
        return Loss.resource()

    @classmethod
    def all(cls) -> List[str]:
        return cls.limits() + cls.cashflows() + cls.emissions() + cls.losses()

    # *----------- Hashing --------------------------------

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
