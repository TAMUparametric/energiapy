"""Consequence"""

from dataclasses import dataclass

from ..components.impact.categories import Economic, Environ, Social
from ..core.dimension import Dimension


@dataclass
class Consequence(Dimension):
    """A representation of the Consequence of the system
    dimensions based on the impact determined as the product of
    activity and indicators

    All impact indicators are attached to this object

    Attributes:
        model (Model): Model to which the representation belongs.
        name (str): Name of the model. Defaults to None.
        envs (list[Env]): List of environmental indicators.
        socs (list[Soc]): List of social indicators.
        ecos (list[Eco]): List of economic indicators.

    Note:
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

        Dimension.__post_init__(self)

    @property
    def indicators(self):
        """All indicators"""
        return self.envs + self.socs + self.ecos
