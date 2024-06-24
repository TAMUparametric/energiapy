"""energiapy.Resource - Resource as refined in the RT(M)N framework  
"""
import uuid
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union
from warnings import warn

from .comptype import EmissionType, ResourceType
from .parameters.mpvar import Theta, create_mpvar
from .parameters.paratype import (FactorType, LocalizeType, MPVarType,
                                  ParameterType)


@dataclass
class Resource:
    """Object with resource data that can be consumed (purchased if consumed at a price), discharged (sold if revenue is generated), 
    stored, used or made by process, transported.

    The emission potentials [gwp, odp, acid, eutt, eutf, eutm] can also be provided
    Given that maximum consumption (cons_max), purchase price, and sell price can vary by location,
    localization can be achieved by providing the cons_max_localize, purchase_price_localize, and sell_price_localize
    at Location level

    Demand needs to be declared at Location

    Args:
        name (str): name of resource. Enter None to randomly assign a name.
        discharge (bool, optional): if can be discharged or sold. Defaults to None
        sell_price (Union[float, Tuple[float], Theta], optional): revenue if generated on selling. Defaults to None
        purchase_price (Union[float, Tuple[float], Theta], optional): purchase price.Defaults to None
        cons_max (Union[float, Tuple[float], Theta], optional): maximum amount that can be consumed. Defaults to None
        store_max (float, optional): maximum amount that can be stored in inventory. Defaults to None
        store_min (float, optional): minimum amount of that is need to setup inventory. Defaults to None
        store_loss (float, optional): amount lost in inventory per time period of the scheduling scale. Defaults to None
        storage_cost: (float, optional): penalty for mainting inventory per time period in the scheduling scale. Defaults to None.
        transport (bool, optional): if can be transported, also determined if mentioned while defining Transport. Defaults to None
        gwp (float, optional): global warming potential. Defaults to None.
        odp (float, optional): ozone depletion potential. Defaults to None.
        acid (float, optional): acidification potential. Defaults to None.
        eutt (float, optional): terrestrial eutrophication potential. Defaults to None.
        eutf (float, optional): fresh water eutrophication potential. Defaults to None.
        eutm (float, optional): marine eutrophication potential. Defaults to None.
        basis (str, optional): unit in which resource is measured. Defaults to None 
        block (Union[str, list, dict], optional): block to which it belong. Convinient to set up integer cuts. Defaults to None
        label (str, optional): used while generating plots. Defaults to None
        citation (str, optional): can provide citations for your data sources. Defaults to None
        ctype (List[ResourceType], optional): List of resource types. Defaults to None
        ptype (Dict[ResourceType, ParameterType], optional): dict with parameters declared and thier types. Defaults to None.
        ltype (Dict[ResourceType, List[Tuple['Location', LocalizeType]]], optional): which parameters are localized at Location. Defaults to None.
        ftype (Dict[ResourceType, List[Tuple['Location', ParameterType]]], optional): which parameters are provided with factors at Location. Defaults to None

    Examples:

        [1] A resource that can be consumed is declared by setting a cons_max 

        >>> Solar = Resource(name='Solar', cons_max= 100)

        [2] A resource that can be purchase need a price to be set, besides cons_max.

        >>> Water = Resource(name='H2O', cons_max= 100, purchase_price= 20)

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

        >>> Water = Resource(name='H2O', cons_max= Theta((0, 45)), purchase_price= Theta((0, 3))) 

        [8] Environmental impact potentials can also be declared for resources

        >>> NaturalGas = Resource(name = 'NG', cons_max = 1000, gwp = 30, odp = 50, acid = 20, eutt = 5, eutf = 60, eutm = 10)

    """

    name: str
    # Primary attributes
    discharge: bool = None
    sell_price: Union[float, Tuple[float], Theta] = None
    purchase_price: Union[float, Tuple[float], Theta] = None
    cons_max: Union[float, Tuple[float], Theta] = None
    # Inventory params, can be provided to STORE type Process
    store_max: float = None
    store_min: float = None
    store_loss: float = None
    storage_cost: float = None
    # Transportation
    transport: bool = None
    # Emissions
    gwp: float = None
    odp: float = None
    acid: float = None
    eutt: float = None
    eutf: float = None
    eutm: float = None
    # Details
    basis: str = None
    block: Union[str, list, dict] = None
    label: str = None
    citation: str = None
    # Types
    ctype: List[ResourceType] = None
    ptype: Dict[ResourceType, ParameterType] = None
    ltype: Dict[ResourceType, List[Tuple['Location', LocalizeType]]] = None
    ftype: Dict[ResourceType, List[Tuple['Location', FactorType]]] = None
    # Depreciated
    sell: bool = None
    demand: bool = None
    varying: list = None
    price: float = None
    revenue: float = None

    def __post_init__(self):

        self.availability = self.cons_max  # An alias for cons_max

        # *-----------------Set ctype (ResourceType)---------------------------------
        # .DISCHARGE allows the resource to be discharged (cons_max > 0)
        # .SELL is when a Resource generated revenue (has a sell_price)
        # .DEMAND is set if a specific demand for resource is declared at Location
        # .CONSUME is when a Resource can be consumed
        # .PURCHASE is when a consumed Resource has a purchase_price
        # .IMPLICIT is when a Resource only exists insitu (not discharged or consumed)
        # .PRODUCED is when a Resource is produced by a Process
        # .SELL and .DEMAND imply that .DISCHARGE is True
        # .STORE is set if a store_max is given
        # storage resources are also generated implicitly if a Resource is provided to a Process as storage

        if self.ctype is None:
            self.ctype = []

        if self.sell_price is not None:
            self.ctype.append(ResourceType.SELL)
            if self.discharge is None:
                self.discharge = True
                warn(f'{self.name}: discharge set to True, since sell_price is given')

        if self.discharge is not None:
            self.ctype.append(ResourceType.DISCHARGE)

        if self.cons_max is not None:
            self.ctype.append(ResourceType.CONSUME)
        else:
            # if it is not consumed from outside the system, it has to be made in the system
            self.ctype.append(ResourceType.PRODUCE)
            if self.discharge is None:
                # is not discharged or consumed. Produced and used within the system captively
                self.ctype.append(ResourceType.IMPLICIT)

        if self.purchase_price is not None:
            self.ctype.append(ResourceType.PURCHASE)
            if self.cons_max is None:
                warn(f'{self.name}: Price given, suggest providing cons_max as well')

        if self.store_max is not None:
            self.ctype.append(ResourceType.STORE)

        # *-----------------Set ptype (ParameterType) ---------------------------------
        # The parameter types (ptypes) are set to .CERTAIN initially
        # They are replaced by .UNCERTAIN if a MPVar Theta or a tuple of bounds is provided
        # If empty Theta is provided, the bounds default to (0, 1)
        # They are replaced by a list of (Location, .FactorType) if factors are declared at Location

        self.ptype = {i: ParameterType.CERTAIN for i in self.ctype}

        if self.sell_price is not None:
            if isinstance(self.sell_price, (tuple, Theta)):
                self.ptype[ResourceType.SELL] = ParameterType.UNCERTAIN
                self.sell_price = create_mpvar(
                    value=self.sell_price, component=self, ptype=getattr(MPVarType, 'SELL_PRICE'))

        if self.purchase_price is not None:
            if isinstance(self.purchase_price, (tuple, Theta)):
                self.ptype[ResourceType.PURCHASE] = ParameterType.UNCERTAIN
                self.purchase_price = create_mpvar(
                    value=self.purchase_price, component=self, ptype=getattr(MPVarType, 'PURCHASE_PRICE'))

        if self.cons_max is not None:
            if isinstance(self.cons_max, (tuple, Theta)):
                self.ptype[ResourceType.CONSUME] = ParameterType.UNCERTAIN
                self.cons_max = create_mpvar(
                    value=self.cons_max, component=self, ptype=getattr(MPVarType, 'AVAILABILITY'))

        # *-----------------Set etype (Emission)---------------------------------
        # Types of emission accounted for are declared here and EmissionTypes are set

        self.etype = []
        self.emissions = dict()
        for i in ['gwp', 'odp', 'acid', 'eutt', 'eutf', 'eutm']:
            if getattr(self, i) is not None:
                self.etype.append(getattr(EmissionType, i.upper()))
                self.emissions[i] = getattr(self, i)

        # *----------------- Parameter localizations populated at Location ---------------------------------
        # Localization factors can be provided for parameters at Location
        # These include purchase_price, sell_price and cons_max (if declared), and demand if provided at location
        # ltype is a Dict[ResourceType, List[Tuple['Location', LocalizeType]]]
        # localizations a Dict[ResourceType, List[Tuple['Location', Localize]]]

        self.ltype, self.localizations = dict(), dict()

        # *------------ Parameter factors populated at Location -----------
        # Factors can be provided for parameters at Location
        # Thes are filled in at Location and save localizations and parameter factors
        # These include purchase_price, sell_price and cons_max (if declared), and demand if provided at location
        # ftype is a Dict[ResourceType, List[Tuple['Location', FactorType]]]
        # factors a Dict[ResourceType, List[Tuple['Location', Factor]]]

        self.ftype, self.factors = dict(), dict()

        # *-----------------Random name ---------------------------------
        # A random name is generated if self.name = None

        if self.name is None:
            self.name = f'{self.__class__.__name__}_{uuid.uuid4().hex}'

        # *----------------- Depreciation Warnings---------------------------------

        if self.demand is True:
            raise ValueError(
                f'{self.name}: demand will be intepreted in energiapy.Location. Set discharge = True and set Location.demand = {{Resource: demand}}')
        if self.sell is not None:
            raise ValueError(
                f'{self.name}: sell has been depreciated. set discharge = True and specify selling_price if needed')
        if self.varying is not None:
            raise ValueError(
                f'{self.name}: varying has been depreciated. Variability will be intepreted based on data provided to energiapy.Location factors')
        if self.price is not None:
            raise ValueError(
                f'{self.name}: price has been depreciated. Please use purchase_price instead')
        if self.revenue is not None:
            raise ValueError(
                f'{self.name}: revenue has been depreciated. Please use sell_price instead')

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
