"""energiapy.Resource - Resource as refined in the RT(M)N framework  
"""
from dataclasses import dataclass
from typing import Union, List, Tuple, Dict
import uuid
from .comptype import ResourceType, ParameterType, Th
from warnings import warn


@dataclass
class Resource:
    """Object with resource data that can be consumed (purchased if consumed at a price), discharged (sold if revenue is generated), 
    stored, used or made by process, transported.

    The resource can 

    Args:
        name (str, optional): name of resource. Defaults to None
        sell (bool, optional): if can be discharged or sold. Defaults to None
        revenue (Union[float, Tuple[float], Th], optional): revenue if generated on selling. Defaults to None
        cons_max (Union[float, Tuple[float], Th], optional): maximum amount that can be consumed. Defaults to None
        price (Union[float, Tuple[float], Th], optional): purchase price.Defaults to None
        store_max (float, optional): maximum amount that can be stored in inventory. Defaults to None
        store_min (float, optional): minimum amount of that is need to setup inventory. Defaults to None
        store_loss (float, optional): amount lost in inventory per time period of the scheduling scale. Defaults to None
        basis (str, optional): unit in which resource is measured. Defaults to None 
        block (Union[str, list, dict], optional): block to which it belong. Convinient to set up integer cuts. Defaults to None
        citation (str, optional): can provide citations for your data sources. Defaults to None
        demand (bool, optional): if a specific demand needs to be met, also determined if a demand is specified at Location. Defaults to None
        transport (bool, optional): if can be transported, also determined if mentioned while defining Transport. Defaults to None
        gwp (float, optional): global warming potential. Defaults to None.
        odp (float, optional): ozone depletion potential. Defaults to None.
        acid (float, optional): acidification potential. Defaults to None.
        eutt (float, optional): terrestrial eutrophication potential. Defaults to None.
        eutf (float, optional): fresh water eutrophication potential. Defaults to None.
        eutm (float, optional): marine eutrophication potential. Defaults to None.
        label (str, optional): used while generating plots. Defaults to None
        ctype (List[ResourceType], optional): List of resource types. Defaults to None

        Examples:

            [1] A resource that can be consumed is declared by setting a cons_max 

            >>> Solar = Resource(name='Solar', cons_max= '100')

            [2] A resource that can be purchase need a price to be set, besides cons_max.

            >>> Water = Resource(name='H2O', cons_max= 100, price= 20)

            [3] If the resource can be discharged.

            >>> CO2 = Resource(name='CO2', sell = True)

            [4] If the resource can be sold. A selling price is set along with sell = True.

            >>> Power = Resource(name='Power', sell = True, revenue = 0.2)

            [5] Additional attributes can be added. Note that this resource is only used implicitly in the system. 

            >>> H2 = Resource(name='H2', basis = 'tons', label = 'Hydrogen', block= 'DEC', citation = 'Kakodkar, et. al (2024)')

            [6] A storage process can be declared here. Or a resource can be given to a storage type Process which generates a stored resource

            >>> Money= Resource(name='Poishe', basis = 'Rupees'. store_max= 2, store_min = 0, store_loss = 0.01)

            [7] Uncertainty in resource parameters for revenue, availability, and price can be handled by either:

            1. Providing deterministic dataset for variablity at the Location level 

            OR through:

            2. Multiparameteric programming (mpP). To declare a parameteric variable, either give ranges for data (as tuples )instead of floats
            or insert energiapy.Th(bounds = (_, _)) in place of the parameter.

            For example, if the availability of water is uncertain:

            >>>  H2 = Resource(name='H2', sell = True, revenue = (0, 10)) 

            or 

            >>> H2 = Resource(name='H2', sell = True, revenue = Th(bounds = (0, 10)))

            Multiple parameters of a resource can also be uncertain. As shown here, where water has both uncertain availability as well as price.

            >>> Water = Resource(name='H2O', cons_max= Th((0, 45)), price= Th((0, 3))) 

            [8] Environmental impact potentials can also be declared for resources

            >>> NaturalGas = Resource(name = 'NG', cons_max = 1000, gwp = 30, odp = 50, acid = 20, eutt = 5, eutf = 60, eutm = 10)

    """

    name: str = None
    discharge: bool = None
    sell_price: Union[float, Tuple[float], Th] = None
    cons_max: Union[float, Tuple[float], Th] = None
    purchase_price: Union[float, Tuple[float], Th] = None
    store_max: float = None
    store_min: float = None
    store_loss: float = None
    basis: str = None
    block: Union[str, list, dict] = None
    citation: str = 'citation needed'
    demand: bool = None
    transport: bool = None
    ctype: List[ResourceType] = None
    label: str = None
    gwp: float = None
    odp: float = None
    acid: float = None
    eutt: float = None
    eutf: float = None
    eutm: float = None

    def __post_init__(self):

        if self.ctype is None:
            self.ctype = []

        # *-----------------Set ctype---------------------------------

        if self.sell_price is not None:
            self.ctype.append(ResourceType.SELL)
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

        # *-----------------Set ptype---------------------------------
        self.ptype = {i: ParameterType.CERTAIN for i in self.ctype}

        if self.sell_price is not None:
            if isinstance(self.sell_price, (tuple, Th)):
                self.ptype[ResourceType.SELL] = ParameterType.UNCERTAIN

        if self.cons_max is not None:
            if isinstance(self.cons_max, (tuple, Th)):
                self.ptype[ResourceType.CONSUME] = ParameterType.UNCERTAIN

        if self.purchase_price is not None:
            if isinstance(self.purchase_price, (tuple, Th)):
                self.ptype[ResourceType.PURCHASE] = ParameterType.UNCERTAIN

        # self.emission_potentials_dict = {'gwp': self.gwp, 'odp': self.odp,
        #                                  'acid': self.acid, 'eutt': self.eutt, 'eutf': self.eutf, 'eutm': self.eutm}

        if self.demand is True:  # if somebody sets the demand to be true, sell will need to updated here
            self.discharge = True

        if self.name is None:
            self.name = f"Resource_{uuid.uuid4().hex}"

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
