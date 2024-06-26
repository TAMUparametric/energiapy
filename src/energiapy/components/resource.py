"""energiapy.Resource - Resource as refined in the RT(M)N framework  
"""
import uuid
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union
from warnings import warn

from .comptype.emission import EmissionType
from .comptype.resource import ResourceType
from .parameters.factor import Factor
from .parameters.localization import Localization
from .parameters.mpvar import Theta, create_mpvar
from .parameters.paramtype import (FactorType, LocalizationType, MPVarType,
                                   ParameterType)
from .parameters.resource import ResourceParamType


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
        ctype (List[ResourceType], optional): List of resource types. Defaults to None
        ptype (Dict[ResourceParamType, ParameterType], optional): dict with parameters declared and thier types. Defaults to None.
        ltype (Dict[ResourceParamType, List[Tuple['Location', LocalizationType]]], optional): which parameters are localized at Location. Defaults to None.
        ftype (Dict[ResourceParamType, List[Tuple['Location', ParameterType]]], optional): which parameters are provided with factors at Location. Defaults to None
        etype (List[EmissionType], optional): list of emission types defined. Defaults to None
        localizations (Dict[ResourceParamType, List[Tuple['Location', Localization]]], optional): collects localizations when defined at Location. Defaults to None.
        factors (Dict[ResourceParamType, List[Tuple['Location', Factor]]], optional): collects factors when defined at Location. Defaults to None.
        emissions (Dict[str, float], optional): collects emission data. Defaults to None.

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
    # Primary attributes. cons_max has alias availability
    discharge: bool = None
    sell_price: Union[float, Tuple[float], Theta] = None
    purchase_price: Union[float, Tuple[float], Theta] = None
    cons_max: Union[float, Tuple[float], Theta] = None
    # Inventory params, can be provided to STORE type Process
    store_max: Union[float, Tuple[float], Theta] = None
    store_min: float = None
    store_loss: Union[float, Tuple[float], Theta] = None
    storage_cost: Union[float, Tuple[float], Theta] = None
    # Transportation
    transport: bool = None
    # Emissions
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
    ptype: Dict[ResourceParamType, ParameterType] = None
    ltype: Dict[ResourceParamType,
                List[Tuple['Location', LocalizationType]]] = None
    ftype: Dict[ResourceParamType, List[Tuple['Location', FactorType]]] = None
    etype: List[EmissionType] = None
    # Collections
    localizations: Dict[ResourceParamType,
                        List[Tuple['Location', Localization]]] = None
    factors: Dict[ResourceParamType, List[Tuple['Location', Factor]]] = None
    emissions: Dict[str, float] = None
    # Depreciated
    sell: bool = None
    varying: bool = None
    price: bool = None
    revenue: bool = None


    def __post_init__(self):

        # *-----------------Set ctype (ResourceType)---------------------------------
        # .DISCHARGE allows the resource to be discharged (cons_max > 0)
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

        if self.sell_price:
            self.ctype.append(ResourceType.SELL)
            if self.discharge is None:
                self.discharge = True
                warn(f'{self.name}: discharge set to True, since sell_price is given')

        if self.discharge:
            self.ctype.append(ResourceType.DISCHARGE)

        if self.cons_max:
            self.ctype.append(ResourceType.CONSUME)
        else:
            # if it is not consumed from outside the system, it has to be made in the system
            self.ctype.append(ResourceType.PRODUCE)
            if not self.discharge:
                # is not discharged or consumed. Produced and used within the system captively
                self.ctype.append(ResourceType.IMPLICIT)

        if self.purchase_price:
            self.ctype.append(ResourceType.PURCHASE)
            if not self.cons_max:
                warn(f'{self.name}: Price given, suggest providing cons_max as well')

        if self.store_max:
            self.ctype.append(ResourceType.STORE)

        # *-----------------Set ptype (ParameterType) ---------------------------------
        # ptypes of declared parameters are set to .UNCERTAIN if a MPVar Theta or a tuple of bounds is provided,
        # .CERTAIN otherwise
        # If empty Theta is provided, the bounds default to (0, 1)
        # Factors can be declared at Location (Location, DataFrame), gets converted to  (Location, Factor)

        self.ptype = dict()

        for i in self.resource_level_parameters():
            self.update_resource_level_parameter(parameter=i)

        # *-----------------Set etype (Emission)---------------------------------
        # Types of emission accounted for are declared here and EmissionTypes are set

        for i in self.etypes():
            attr_ = getattr(self, i.lower())
            etype_ = getattr(EmissionType, i)
            if attr_ is not None:
                if not self.etype:  # if etype is not yet defined
                    self.etype = []
                    self.emissions = dict()
                    self.ctype.append(ResourceType.EMISSION)
                self.etype.append(etype_)
                self.emissions[i.lower()] = attr_

        # *-----------------Random name ---------------------------------
        # A random name is generated if self.name = None

        if self.name is None:
            self.name = f'{self.class_name()}_{uuid.uuid4().hex}'

        # *----------------- Depreciation Warnings---------------------------------

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

    # *----------------- Properties ---------------------------------

    @property
    def availability(self):
        """Sets alias for cons_max
        """
        return self.cons_max

    # *----------------- Class Methods ---------------------------------

    @classmethod
    def class_name(cls) -> List[str]:
        """Returns class name 
        """
        return cls.__name__

    # * parameter types

    @classmethod
    def ptypes(cls) -> List[str]:
        """All Resource paramters
        """
        return ResourceParamType.all()

    @classmethod
    def resource_level_parameters(cls) -> List[str]:
        """Set when Resource is declared
        """
        return ResourceParamType.resource_level()

    @classmethod
    def location_level_parameters(cls) -> List[str]:
        """Set when Location is declared
        """
        return ResourceParamType.location_level()

    @classmethod
    def transport_level_parameters(cls) -> List[str]:
        """Set when Transport is declared
        """
        return ResourceParamType.transport_level()

    @classmethod
    def uncertain_parameters(cls) -> List[str]:
        """Uncertain parameters
        """
        return ResourceParamType.uncertain()

    @classmethod
    def uncertain_factors(cls) -> List[str]:
        """Uncertain parameters for which factors are defined
        """
        return ResourceParamType.uncertain_factor()

    # * component class types

    @classmethod
    def ctypes(cls) -> List[str]:
        """All Resource paramters
        """
        return ResourceType.all()

    @classmethod
    def resource_level_classifications(cls) -> List[str]:
        """Set when Resource is declared
        """
        return ResourceType.resource_level()

    @classmethod
    def location_level_classifications(cls) -> List[str]:
        """Set when Location is declared
        """
        return ResourceType.location_level()

    @classmethod
    def transport_level_classifications(cls) -> List[str]:
        """Set when Transport is declared
        """
        return ResourceType.transport_level()

    # * localization types

    @classmethod
    def ltypes(cls) -> List[str]:
        """Resource parameters than can be localized 
        """
        return ResourceParamType.localize()

    # * factor types

    @classmethod
    def ftypes(cls) -> List[str]:
        """Factor types
        """
        return ResourceParamType.uncertain_factor()

    # * emission types

    @classmethod
    def etypes(cls) -> List[str]:
        """Emission types
        """
        return EmissionType.all()

    # *----------------- Functions ---------------------------------------------
    def update_resource_level_parameter(self, parameter: str):
        """updates parameter, sets ptype

        Args:
            parameter (str): parameter to update 
        """
        attr_ = getattr(self, parameter.lower())
        if attr_ is not None:
            ptype_ = getattr(ResourceParamType, parameter)

            if isinstance(attr_, (tuple, Theta)):
                self.ptype[ptype_] = ParameterType.UNCERTAIN
                mpvar_ = create_mpvar(
                    value=attr_, component=self, ptype=getattr(MPVarType, f'{self.class_name()}_{parameter}'.upper()))
                setattr(self, parameter.lower(), mpvar_)
            else:
                self.ptype[ptype_] = ParameterType.CERTAIN

    # *----------- Hashing --------------------------------

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
