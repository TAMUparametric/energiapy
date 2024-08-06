from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import warn

if TYPE_CHECKING:
    from ..._core._aliases._is_component import IsComponent
    from ..._core._aliases._is_epclass import IsEpClass


def add_component(to: IsEpClass, list_attr: str, add: IsComponent):
    """Updates the lists of components in the scenario.

    Args:
        to (TypeVar): to some energiapy object
        list_attr (str): The name of the attribute representing the list of components.
        add (IsComponent): The component to be added to the list.
    """

    if isinstance(list_curr, list):
        list_curr = getattr(to, list_attr)
        if add in list_curr:
            warn(f'{add} is being replaced in Scenario')
        # add component to list
        setattr(to, list_attr, sorted(set(list_curr) | {add}))

    else:
        setattr(to, list_attr, add)
