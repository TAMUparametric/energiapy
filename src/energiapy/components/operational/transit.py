"""energiapy.Transit - moves Resources between Locations
"""

# TODO ---- apply material constraints
# TODO --- trans_loss, retire, introduce, land, land_cost (could be between location.. will need to check)
# TODO -- PWL CAPEX


from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._defined import _Operational

# import operator
# from functools import reduce


if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsExactInput


@dataclass
class Transit(_Operational):
    loss: IsExactInput = field(default=None)

    def __post_init__(self):
        _Operational.__post_init__(self)

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'transits'

    # name: str
    # # Primary attributes
    # resources: Set[Resource]
    # cap_max: Union[float, Tuple[float], Theta, bool, 'Big']
    # # Design Parameters
    # cap_min: Union[float, Tuple[float], Theta] = None
    # land: Union[float, Tuple[float], Theta] = None
    # trans_loss: Union[float, Tuple[float], Theta] = None
    # material_cons: Dict[Material, float] = None
    # # Expenditure
    # capex: Union[float, dict, Tuple[float], Theta] = None
    # vopex: Union[float, Tuple[float], Theta] = None
    # fopex: Union[float, Tuple[float], Theta] = None
    # incidental: Union[float, dict, Tuple[float], Theta] = None
    # # Emissions
    # gwp: Union[float, Tuple[float], Theta] = None
    # odp: Union[float, Tuple[float], Theta] = None
    # acid: Union[float, Tuple[float], Theta] = None
    # eutt: Union[float, Tuple[float], Theta] = None
    # eutf: Union[float, Tuple[float], Theta] = None
    # eutm: Union[float, Tuple[float], Theta] = None
    # # Readiness
    # introduce: Union[float, Tuple[float], Theta] = None
    # retire: Union[float, Tuple[float], Theta] = None
    # lifetime: Union[float, Tuple[float], Theta] = None
    # p_fail: Union[float, Tuple[float], Theta] = None
    # # Details
    # basis: str = None
    # block: str = None
    # label: str = None
    # citation: str = None
    # # Type
    # # ctype: List[Union[TransitType,
    # #                   Dict[TransitType, Set[Tuple[Location, Location]]]]] = None
    # # aspect: Dict[TransitParamType, ParameterType] = None
    # # ftype: Dict[TransitParamType,
    # #             Tuple[Tuple[Location, Location], FactorType]] = None
    # # etype: List[EmissionType] = None
    # # # Collections
    # # factors: Dict[TransitParamType,
    # #               Tuple[Tuple[Location, Location], Factor]] = None
    # emissions: Dict[str, float] = None

    # # Depricated
    # trans_max: float = None
    # trans_min: float = None
    # emission: float = None
    # varying: bool = None

    # def __post_init__(self):

    #     # *-----------------Set ctype (TransitType)-------------------------

    #     if not self.ctype:
    #         self.ctype = []

    #     for i in self.resources:  # update Resource if transported
    #         # TODO - FIX

    #         i.ctype.append(ResourceType.TRANSPORT)
    #         if ResourceType.IMPLICIT in i.ctype:
    #             i.ctype.remove(ResourceType.IMPLICIT)
    #         if not i.transport:
    #             i.transport = set()
    #         i.transport.add(self)

    #     # Materials are not necessarily consumed (NO_MATMODE), if material_cons is None
    #     # If consumed, there could be multiple modes of consumption (MULTI_MATMODE) or one (SINGLE_MATMODE)
    #     # for MULTI_MATMODE, provide a dict of type ('material_mode' (str, int): {Material: float})

    #     if self.material_cons is None:
    #         self.ctype.append(TransitType.NO_MATMODE)
    #         self.materials = set()

    #     else:
    #         if get_depth(self.material_cons) > 1:
    #             self.ctype.append(TransitType.MULTI_MATMODE)
    #             self.material_modes = set(self.material_cons)
    #             self.materials = reduce(
    # operator.or_, (set(self.material_cons[i]) for i in self.material_modes),
    # set())

    #         else:
    #             self.ctype.append(TransitType.SINGLE_MATMODE)
    #             self.materials = set(self.material_cons)

    #     # capex can be linear (LINEAR_CAPEX) or piecewise linear (PWL_CAPEX)
    #     # if PWL, capex needs to be provide as a dict {capacity_segment: capex_segement}
    #     if self.capex:
    #         if isinstance(self.capex, dict):
    #             self.ctype.append(TransitType.PWL_CAPEX)
    #             self.capacity_segments = list(self.capex)
    #             self.capex_segments = list(self.capex.values())
    #         else:
    #             self.ctype.append(TransitType.LINEAR_CAPEX)

    #     # if any expenditure is incurred
    #     if any([self.capex, self.fopex, self.vopex, self.incidental]):
    #         self.ctype.append(TransitType.EXPENDITURE)

    #     # if it requires land to set up
    #     if self.land:
    #         self.ctype.append(TransitType.LAND)

    #     # if this process fails
    #     if self.p_fail:
    #         self.ctype.append(TransitType.FAILURE)

    #     # if this process has some readiness aspects defined
    #     if any([self.introduce, self.retire, self.lifetime]):
    #         self.ctype.append(TransitType.READINESS)

    #     # *-----------------Set aspect---------------------------------
    #     # If parameter provided as Theta or tuple bounds are provided - makes MPVar

    #     self.aspect = dict()

    #     for i in self.aspects():
    #         self.update_transport_level_parameter(parameter=i)

    #     # *-----------------Set etype (Emission)----------------------------
    #     # Types of emission accounted for are declared here and EmissionTypes are set

    #     for i in self.etypes():
    #         attr_ = getattr(self, i.lower())
    #         etype_ = getattr(EmissionType, i)
    #         if attr_:
    #             if not self.etype:  # if etype is not yet defined
    #                 self.etype = []
    #                 self.emissions = dict()
    #                 self.ctype.append(TransitType.EMISSION)
    #             self.etype.append(etype_)
    #             self.emissions[i.lower()] = attr_

    #     # *----------------- Depreciation Warnings--------------------------
    #     if self.trans_max:
    #         raise ValueError(
    # f'{self.name}: trans_max has been depreciated. Please use cap_max
    # instead')

    #     if self.trans_min:
    #         raise ValueError(
    # f'{self.name}: trans_max has been depreciated. Please use cap_min
    # instead')

    #     if self.varying:
    #         raise ValueError(
    # f'{self.name}: varying has been depreciated. Variability will be
    # determined from factors provided to Network')

    #     if self.emission:
    #         raise ValueError(
    # f'{self.name}: emission has been depreciated. Please provide individual
    # emissions (gwp, odp, acid, eutt, eutf, eutm) instead')

    # # *----------------- Properties ---------------------------------

    # @property
    # def capacity(self):
    #     """Sets capacity
    #     """
    #     if self.cap_max:
    #         return CouldBeVar

    # # *----------------- Class Methods -------------------------------------

    # @classmethod
    # def class_name(cls) -> str:
    #     """Returns class name
    #     """
    #     return cls.__name__

    # # * Transit parameters

    # @classmethod
    # def aspects(cls) -> Set[str]:
    #     """All Transit parameters
    #     """
    #     return TransitParamType.all()

    # @classmethod
    # def uncertain_parameters(cls) -> Set[str]:
    #     """Uncertain parameters
    #     """
    #     return TransitParamType.uncertain()

    # @classmethod
    # def uncertain_factors(cls) -> Set[str]:
    #     """Uncertain parameters for which factors are defined
    #     """
    #     return TransitParamType.uncertain_factor()

    # @classmethod
    # def transport_level_readiness_parameters(cls) -> Set[str]:
    #     """Set when Transit are declared
    #     """
    #     return TransitParamType.readiness()

    # @classmethod
    # def transport_level_failure_parameters(cls) -> Set[str]:
    #     """Set when Transit are declared
    #     """
    #     return TransitParamType.failure()

    # # * Transit classifications

    # @classmethod
    # def ctypes(cls) -> Set[str]:
    #     """All Transit parameters
    #     """
    #     return TransitType.all()

    # @classmethod
    # def transport_level_classifications(cls) -> Set[str]:
    #     """Set when Transit is declared
    #     """
    #     return TransitType.transport_level()

    # @classmethod
    # def network_level_classifications(cls) -> Set[str]:
    #     """Set when Network is declared
    #     """
    #     return TransitType.network_level()

    # # * factor types

    # @classmethod
    # def ftypes(cls) -> Set[str]:
    #     """Factor types
    #     """
    #     return TransitParamType.uncertain_factor()

    # # * emission types

    # @classmethod
    # def etypes(cls) -> Set[str]:
    #     """Emission types
    #     """
    #     return EmissionType.all()

    # # *----------------- Functions -----------------------------------------

    # def update_transport_level_parameter(self, parameter: str):
    #     """updates parameter, sets aspect

    #     Args:
    #         parameter (str): parameter to update
    #     """
    #     attr_ = getattr(self, parameter.lower())
    #     if attr_:
    #         aspect_ = getattr(TransitParamType, parameter)
    #         if isinstance(attr_, (tuple, Theta)):
    #             self.aspect[aspect_] = ParameterType.UNCERTAIN
    #             theta_ = birth_theta(
    #                 value=attr_, component=self, aspect=getattr(MPVarType, f'{self.cname}_{parameter}'.upper()))
    #             setattr(self, parameter.lower(), theta_)
    #         elif hasattr(attr_, 'bigm') or attr_ is True:
    #             self.aspect[aspect_] = ParameterType.BIGM
    #             if attr_ is True:
    #                 setattr(self, parameter.lower(), BigM)
    #         elif hasattr(attr_, 'couldbevar'):
    #             self.aspect[aspect_] = ParameterType.UNDECIDED
    #         else:
    #             self.aspect[aspect_] = ParameterType.CERTAIN

    # def __repr__(self):
    #     return self.name

    # def __hash__(self):
    #     return hash(self.name)

    # def __eq__(self, other):
    #     return self.name == other.name
