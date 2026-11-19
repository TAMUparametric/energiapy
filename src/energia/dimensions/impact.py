"""Consequence."""

from dataclasses import dataclass

from .._core._dimension import _Dimension
from ..components.impact.categories import Economic, Environ, Social


@dataclass
class Impact(_Dimension):
    """
    Represent the impacts associated with model activities.

    An activity multiplied by its indicator gives its contribution to the impact.

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
        """Initialize the economic, environmental, and social indicator collections."""
        # economic impact
        self.economy: list[Economic] = []
        # environmental impact
        self.environment: list[Environ] = []
        # social impact
        self.society: list[Social] = []

        _Dimension.__post_init__(self)

    @property
    def indicators(self) -> list[Environ | Social | Economic]:
        """All indicators."""
        return self.environment + self.society + self.economy
