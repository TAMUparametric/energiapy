"""Player"""

from ..._core._component import _Component


class Player(_Component):
    """
    Player or Actor, the one taking the decisions
    based on information provided

    Players own certain processes and be responsible for the streams and impact
    caused by their decisions pertaining to this

    :param label: An optional label for the component. Defaults to None.
    :type label: str, optional
    :param citations: An optional citation or description for the component. Defaults to None.
    :type citations: str | list[str] | dict[str, str | list[str]], optional

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
    """

    def __init__(self, label: str = "", citations: str = "", **kwargs):

        _Component.__init__(self, label=label, citations=citations, **kwargs)
