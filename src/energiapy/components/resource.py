"""energiapy.Resource - Resource as refined in the RT(M)N framework  
"""
import uuid
from dataclasses import dataclass
from typing import List, Tuple, Union

from pandas import DataFrame

from ..parameters.bound import Big, BigM
from ..parameters.factor import Factor
from ..parameters.mpvar import Theta
from ..parameters.parameter import Parameter, Parameters
from ..parameters.type.property import *
from ..parameters.type.disposition import *
from .temporal_scale import TemporalScale
from .type.resource import ResourceType


@dataclass
class Resource:
    """Object with resource data that can be consumed (purchased if consumed at a price), discharged (sold if revenue is generated), 
    stored, used or made by process, transported.

    The emission potentials [gwp, odp, acid, eutt, eutf, eutm] can also be provided
    Given that maximum consumption (consume), purchase price, and sell price can vary by location,
    localization can be achieved by providing the consume_localize, purchase_price_localize, and sell_price_localize
    at Location level

    Demand needs to be declared at Location

    Args:
        name (str): name of resource. Enter None to randomly assign a name.
        discharge (Union[float, Tuple[float], Theta, bool, 'Big'], optional): if can be discharged or sold. Defaults to None
        sell_price (Union[float, Tuple[float], Theta], optional): revenue if generated on selling. Defaults to None
        purchase_price (Union[float, Tuple[float], Theta], optional): purchase price.Defaults to None
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
        ptype (Dict[ResourceParamType, Union[Property, Dict['Location', Property]]], optional): dict with parameters declared and thier types. Defaults to None.
        ltype (Dict[ResourceParamType, List[Tuple['Location', LocalizationType]]], optional): which parameters are localized at Location. Defaults to None.
        ftype (Dict[ResourceParamType, List[Tuple['Location', Property]]], optional): which parameters are provided with factors at Location. Defaults to None
        etype (List[EmissionType], optional): list of emission types defined. Defaults to None
        localizations (Dict[ResourceParamType, List[Tuple['Location', Localization]]], optional): collects localizations when defined at Location. Defaults to None.
        factors (Dict[ResourceParamType, List[Tuple['Location', Factor]]], optional): collects factors when defined at Location. Defaults to None.
        emissions (Dict[str, float], optional): collects emission data. Defaults to None.

    Examples:

        [1] A resource that can be consumed is declared by setting a consume 

        >>> Solar = Resource(name='Solar', consume= 100)

        [2] A resource that can be purchase need a price to be set, besides consume.

        >>> Water = Resource(name='H2O', consume= 100, purchase_price= 20)

        [3] If the resource can be discharged.

        >>> CO2 = Resource(name='CO2', discharge = True)

        [4] If the resource can be sold. A selling price is set along with sell = True.

        >>> Power = Resource(name='Power', discharge = True, sell_price = 0.2)

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

        >>>  H2 = Resource(name='H2', discharge = True, sell_price = (0, 10)) 

        or 

        >>> H2 = Resource(name='H2', discharge = True, sell_price = Theta(bounds = (0, 10)))

        Multiple parameters of a resource can also be uncertain. As shown here, where water has both uncertain availability as well as price.

        >>> Water = Resource(name='H2O', consume= Theta((0, 45)), purchase_price= Theta((0, 3))) 

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
    discharge_scale: int = None
    consume: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                   DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    consume_scale: int = None
    store: Union[float, bool, 'BigM', List[Union[float, 'BigM']],
                 DataFrame, Tuple[Union[float, DataFrame, Factor]], Theta] = None
    store_scale: int = None
    # LossType
    store_loss: Union[float, Tuple[float], Theta] = None
    store_loss_scale: int = None
    # CashFlowType
    sell_price: Union[float, Theta, DataFrame,
                      Tuple[Union[float, DataFrame, Factor]]] = None
    purchase_price: Union[float, Theta, DataFrame,
                          Tuple[Union[float, DataFrame, Factor]]] = None
    storage_cost: Union[float, Theta, DataFrame,
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
    # Depreciated
    sell: bool = None
    varying: bool = None
    price: bool = None
    revenue: bool = None
    cons_max: bool = None
    store_max: bool = None
    store_min: bool = None

    def __post_init__(self):

        # *-----------------Set ctype (ResourceType)---------------------------------
        # .DISCHARGE allows the resource to be discharged (consume > 0)
        # .SELL is when a Resource generated revenue (has a sell_price)
        # .CONSUME is when a Resource can be consumed
        # .PURCHASE is when a consumed Resource has a purchase_price
        # .IMPLICIT is when a Resource only exists insitu (not discharged or consumed)
        # .PRODUCED is when a Resource is produced by a Process
        # .SELL and .DEMAND imply that .DISCHARGE is True
        # .STORE is set if a store_max is given
        # .DEMAND is set if a specific demand for resource is declared at Location
        # .TRANSPORT is set if a Resource is in the set Transport.resources
        # storage resources are also generated implicitly if a Resource is provided to a Process as storage

        if not self.ctype:
            self.ctype = list()

        if self.sell_price is not None:
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

        if self.purchase_price:
            self.ctype.append(ResourceType.PURCHASE)
            if self.consume is None:
                self.consume = BigM

        if self.store is not None:
            self.ctype.append(ResourceType.STORE)

        # *----------------- Update parameters ---------------------------------

        for i in self.limits() + self.cashflows() + self.losses() + self.emissions():
            if getattr(self, i.lower()) is not None:
                attr = getattr(self, i.lower())      
                if i in self.limits():
                    temporal, ptype, psubtype = getattr(self, f'{i.lower()}_scale'), Property.LIMIT, getattr(Limit, i)
                if i in self.cashflows(): 
                    temporal, ptype, psubtype = None, Property.CASHFLOW, getattr(CashFlow, i)

                if i in self.emissions():
                    temporal, ptype, psubtype  = None, Property.EMISSION, getattr(Emission, i)
                if i in self.losses():
                    temporal, ptype, psubtype  = getattr(self, f'{i.lower()}_scale'), Property.LOSS, getattr(Loss, i)
                
                param = Parameter(value=attr, ptype=ptype, spatial=SpatialDisp.NETWORK,
                                   temporal=temporal, psubtype=psubtype, component=self,
                                   scales=self.scales)
                setattr(self, i.lower(), Parameters(param))
                
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
                f'{self.name}: price has been depreciated. Please use purchase_price instead')
        if self.revenue:
            raise ValueError(
                f'{self.name}: revenue has been depreciated. Please use sell_price instead')
        if self.revenue:
            raise ValueError(
                f'{self.name}: cons_max has been depreciated. Please use consume instead')

    # *----------------- Class Methods ---------------------------------

    @classmethod
    def class_name(cls) -> str:
        """Returns class name 
        """
        return cls.__name__

    # * parameter types

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

    # *----------- Hashing --------------------------------

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
