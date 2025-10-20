"""Land"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ._commodity import _Commodity

if TYPE_CHECKING:
    from ..measure.unit import Unit


class Land(_Commodity):
    """
    Land used by Operations

    :param label: Label of the commodity, used for plotting. Defaults to None.
    :type label: str, optional
    :param name: Name of the commodity, used for indexing. Defaults to None.
    :type name: str, optional
    :param basis: Unit basis of the commodity. Defaults to None.
    :type basis: Unit, optional


    :ivar model: The model to which the component belongs.
    :vartype model: Model
    :ivar name: Set when the component is assigned as a Model attribute.
    :vartype name: str

    :ivar constraints: List of constraints associated with the component.
    :vartype constraints: list[str]
    :ivar domains: List of domains associated with the component.
    :vartype domains: list[Domain]
    :ivar aspects: Aspects associated with the component with domains.
    :vartype aspects: dict[Aspect, list[Domain]]
    :ivar conversions: List of conversions associated with the commodity. Defaults to [].
    :vartype conversions: list[Conversion]
    :ivar insitu: If the commodity only exists insitu, i.e., does not scale any domains
    :vartype insitu: bool, optional
    """

    def __init__(
        self,
        basis: Unit | None = None,
        label: str = "",
        captions: str = "",
    ):
        _Commodity.__init__(self, basis=basis, label=label, captions=captions)
