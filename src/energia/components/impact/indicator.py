"""Impact Indicator"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..._core._component import _Component

if TYPE_CHECKING:
    from ...dimensions.consequence import Consequence


@dataclass
class Indicator(_Component):
    """Impact Indicator

    :param basis: Unit basis of the component. Defaults to None.
    :type basis: Unit, optional
    :param label: An optional label for the component. Defaults to None.
    :type label: str, optional
    :param captions: An optional citation or description for the component. Defaults to None.
    :type captions: str | list[str] | dict[str, str | list[str]], optional

    :ivar model: The model to which the component belongs.
    :vartype model: Model
    :ivar name: Set when the component is assigned as a Model attribute.
    :vartype name: str
    :ivar _indexed: True if an index set has been created.
    :vartype _indexed: bool
    :ivar constraints: List of constraints associated with the component.
    :vartype constraints: list[str]
    :ivar domains: List of domains associated with the component.
    :vartype domains: list[Domain]
    :ivar aspects: Aspects associated with the component with domains.
    :vartype aspects: dict[Aspect, list[Domain]]
    """

    def __post_init__(self):
        _Component.__post_init__(self)

    @property
    def consequence(self) -> Consequence:
        """Impact object"""
        return self.model.consequence
