"""energiapy.Resource - Resource as refined in the RT(M)N framework  
"""
from dataclasses import dataclass
from typing import Union, List, Tuple
import uuid
from .comptype import ResourceType, ParameterType, Th


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
        storage_loss (float, optional): amount lost in inventory per time period of the scheduling scale. Defaults to None
        basis (str, optional): unit in which resource is measured. Defaults to None 
        block (Union[str, list, dict], optional): block to which it belong. Convinient to set up integer cuts. Defaults to None
        citation (str, optional): can provide citations for your data sources. Defaults to None
        demand (bool, optional): if a specific demand needs to be met, also determined if a demand is specified at Location. Defaults to None
        transport (bool, optional): if can be transported, also determined if mentioned while defining Transport. Defaults to None
        label (str, optional): used while generating plots. Defaults to None
        ctype (List[ResourceType], optional): List of resource types. Defaults to None
        ptype (List[ParameterType], optional): List of parameter types. Defaults to None

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

            [7] A storage process can be declared here. Or a resource can be given to a storage type Process which generates a stored resource

            >>> Money= Resource(name='Poishe', basis = 'Rupees'. store_max= 2, store_min = 0, loss = 0.01)

            [6] Uncertainty in resource parameters for revenue, availability, and price can be handled by either:

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

    """

    name: str = None
    sell: bool = None
    revenue: Union[float, Tuple[float], Th] = None
    cons_max: Union[float, Tuple[float], Th] = None
    price: Union[float, Tuple[float], Th] = None
    store_max: float = None
    store_min: float = None
    loss: float = None
    basis: str = None
    block: Union[str, list, dict] = None
    citation: str = 'citation needed'
    demand: bool = None
    transport: bool = None
    ctype: List[ResourceType] = None
    ptype: List[ParameterType] = None
    label: str = None

    # gwp: float = 0
    # odp: float = 0
    # acid: float = 0
    # eutt: float = 0
    # eutf: float = 0
    # eutm: float = 0

    def __post_init__(self):

        if self.ctype is None:
            self.ctype = []

        if self.ptype is None:
            self.ptype = []

        if self.sell is not None:
            self.ctype.append(ResourceType.DISCHARGE)

        if self.revenue is not None:
            self.ctype.append(ResourceType.SELL)
            if isinstance(self.revenue, (tuple, Th)):
                self.ptype.append(ParameterType.UNCERTAIN)

        if self.cons_max is not None:
            self.ctype.append(ResourceType.CONSUME)
            if isinstance(self.cons_max, (tuple, Th)):
                self.ptype.append(ParameterType.UNCERTAIN)
        else:
            # if it is not consumed from outside the system, it has to be made in the system
            self.ctype.append(ResourceType.PRODUCE)
            if (self.sell is None):
                # is not discharged or consumed. Produced and used within the system captively
                self.ctype.append(ResourceType.IMPLICIT)

        if self.price is not None:
            self.ctype.append(ResourceType.PURCHASE)
            if isinstance(self.price, (tuple, Th)):
                self.ptype.append(ParameterType.UNCERTAIN)

        if self.store_max is not None:
            self.ctype.append(ResourceType.STORE)

        # self.emission_potentials_dict = {'gwp': self.gwp, 'odp': self.odp,
        #                                  'acid': self.acid, 'eutt': self.eutt, 'eutf': self.eutf, 'eutm': self.eutm}

        if self.demand is True:  # if somebody sets the demand to be true, sell will need to updated here
            self.sell = True

        if self.name is None:
            self.name = f"Process_{uuid.uuid4().hex}"

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
