"""A Pre-set Parameter"""

from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from ..._core._component import _Component
    from ...represent.model import Model


class Instruction:
    """
    Pre-set instructions to deal with parameter calculations

    :param deciding: Name of the deciding aspect
    :type deciding: str
    :param depending: Name of the depending aspect
    :type depending: str
    :param default: Name of the default component
    :type default: str
    :param label: Label for the parameter. Defaults to ''.
    :type label: str, optional
    :param citations: Captions for the parameter. Defaults to ''.
    :type citations: str, optional

    :raises TypeError: If the component provided is not of the correct kind.
    """

    def __init__(
        self,
        name: str,
        kind: Type[_Component],
        deciding: str,
        depending: str,
        default: str,
        label: str = "",
    ):
        self.name = name
        self.kind = kind
        self.deciding = deciding
        self.depending = depending
        self.default = default
        self.label = label
        self.model: Model | None = None

    def __call__(self, component: _Component):
        # create the calculation
        # there has to be a model

        if isinstance(component, self.kind):

            self.model = component.model

            default_comp = self.model.default_components[self.default]()

            depending = getattr(default_comp, self.depending)
            deciding = getattr(component, self.deciding)

            return deciding[depending]

        raise TypeError(
            f"{component} ({type(component)}): {self.name} earmarked for {self.kind.__name__}"
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)
