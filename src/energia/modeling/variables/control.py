"""Control Variable"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from ..constraints.vmap import Map
from .aspect import Aspect

if TYPE_CHECKING:
    from ..indices.domain import Domain
    from .states import State


@dataclass
class Control(Aspect):
    """
    Some action to be performed by a component
    that adjusts a state variable
    can have a consequence (Impact)
    or elicit a motion (Stream) that has a consequence (Impact)

    :param primary_types: associated components type(s). Defaults to None.
    :type primary_types: Type[_Component] | tuple[Type[_Component], ...]
    :param nn: If True, the decision is a non-negative decision. Defaults to True.
    :type nn: bool
    :param ispos: If True, the decision is positive (non-negative). Defaults to True.
    :type ispos: bool
    :param neg: Negative form or representation of the decision, if any. Defaults to "".
    :type neg: str
    :param latex: LaTeX string. Defaults to "".
    :type latex: str
    :param bound: if the aspect is bounded by another. Defaults to "".
    :type bound: str
    :param label: Label for the decision. Defaults to "".
    :type label: str

    :ivar model: Model to which the Aspect belongs.
    :vartype model: Model
    :ivar name: Name of the Aspect.
    :vartype name: str
    :ivar indices: List of indices (Location, Periods) associated with the Aspect.
    :vartype indices: list[Location | Linkage, Periods]
    :ivar bound_spaces: Spaces where the Aspect has been already bound.
    :vartype bound_spaces: dict[Commodity | Process | Storage | Transport, list[Location | Linkage]]
    :ivar domains: List of domains associated with the Aspect.
    :vartype domains: list[Domain]

    :raises ValueError: If `primary_type` is not defined.
    """

    def __post_init__(self):
        Aspect.__post_init__(self)

        # a state that is being controlled
        self.state: State = None
        # a stream that is being controlled
        self.stream: Self = None
        # an impact that is being controlled
        self.impact: Self = None
        # what increase the state/impact/stream
        self.more: Self = None
        # what decreases the state/impact/stream
        self.less: Self = None

        self.mapped_from: list[Domain] = []

    def update(self, domain: Domain, reporting: bool = False):
        """Add a domain to the decision variable"""

        # Write a mapping constraint
        Map(aspect=self, domain=domain, reporting=reporting)
