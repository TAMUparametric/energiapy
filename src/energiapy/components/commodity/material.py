from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .._base._defined import _Commodity

if TYPE_CHECKING:
    from ..._core._aliases._is_input import IsBoundInput, IsExactInput


@dataclass
class Material(_Commodity):

    use: IsBoundInput = field(default=None)
    use_price: IsExactInput = field(default=None)

    def __post_init__(self):
        _Commodity.__post_init__(self)

    @staticmethod
    def quantify():
        """The quantified data inputs to the component"""
        return ['use']

    @staticmethod
    def expenses():
        """The expense data inputs to the component"""
        return ['use_price']

    @staticmethod
    def collection():
        """The collection in scenario"""
        return 'materials'

    # """
    # Materials are needed to set up processes.

    # Args:
    #     name (str): name of the material. Enter None to randomly assign a name.
    #     gwp (float, optional): global warming potential per unit basis of Material produced. Defaults to None.
    #     odp (float, optional): ozone depletion potential per unit basis of Material produced. Defaults to None.
    #     acid (float, optional): acidification potential per unit basis of Material produced. Defaults to None.
    #     eutt (float, optional): terrestrial eutrophication potential per unit basis of Material produced. Defaults to None.
    #     eutf (float, optional): fresh water eutrophication potential per unit basis of Material produced. Defaults to None.
    #     eutm (float, optional): marine eutrophication potential per unit basis of Material produced. Defaults to None.
    #     basis (str, optional): Unit basis for material. Defaults to None.
    #     citation (str, optional): Add citation. Defaults to None.
    #     label (str, optional): Longer descriptive label if required. Defaults to None.

    # Examples:
    #     Materials can be declared using the resources they consume

    #     >>>  Steel = Material(name='Steel', gwp=0.8, basis= 'kg', label='Steel')

    # """
    # name: str
    # gwp: float = None
    # odp: float = None
    # acid: float = None
    # eutt: float = None
    # eutf: float = None
    # eutm: float = None
    # basis: str = None
    # citation: str = None
    # label: str = None

    # def __post_init__(self):

    #     # *-----------------Set etype (Emission)---------------------------------

    #     self.etype = []
    #     self.emissions = dict()
    #     for i in ['gwp', 'odp', 'acid', 'eutt', 'eutf', 'eutm']:
    #         if getattr(self, i):
    #             self.etype.append(getattr(EmissionType, i.upper()))
    #             self.emissions[i] = getattr(self, i)

    #     if not self.name:
    #         self.name = f'{self.class_name()}_{uuid.uuid4().hex}'

    # @classmethod
    # def class_name(cls) -> str:
    #     """Returns class name
    #     """
    #     return cls.__name__

    # def __repr__(self):
    #     return self.name

    # def __hash__(self):
    #     return hash(self.name)

    # def __eq__(self, other):
    #     return self.name == other.name
