"""Consequence"""

from dataclasses import dataclass

from .._core._dimension import _Dimension
from ..components.impact.categories import Economic, Environ, Social


@dataclass
class Consequence(_Dimension):
    """
    A representation of the Consequence of the system dimensions based on the impact
    determined as the product of activity and indicators.

    All impact indicators are attached to this object.

    :param model: Model to which the representation belongs.
    :type model: Model

    :ivar name: Name of the dimension, generated based on the class and model name. 
    :vartype name: str
    :ivar envs: List of environmental indicators.
    :vartype envs: list[Env]
    :ivar socs: List of social indicators.
    :vartype socs: list[Soc]
    :ivar ecos: List of economic indicators.
    :vartype ecos: list[Eco]

    .. note::
        - name is self generated
        - environ, socs, and ecos are populated as model is defined

    """

    def __post_init__(self):
        # environmental impact
        self.envs: list[Environ] = []
        # social impact
        self.socs: list[Social] = []
        # economic impact
        self.ecos: list[Economic] = []

        _Dimension.__post_init__(self)

    @property
    def indicators(self):
        """All indicators"""
        return self.envs + self.socs + self.ecos
