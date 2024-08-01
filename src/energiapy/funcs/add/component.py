from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import warn

if TYPE_CHECKING:
    from ...types.alias import IsComponent, IsScenario


def add_component(scenario: IsScenario, list_attr: str, component: IsComponent):
    """Updates the lists of components in the scenario.

    Args:
        scenario (IsScenario): The scenario to which the component is added.
        list_attr (str): The name of the attribute representing the list of components.
        component (IsComponent): The component to be added to the list.

    Returns:
        None

    Raises:
        None

    """
    list_curr = getattr(scenario, list_attr)
    if component in list_curr:
        warn(f'{component.name} is being replaced in Scenario')
    # add component to list
    setattr(scenario, list_attr, list(set(list_curr) | {component}))
