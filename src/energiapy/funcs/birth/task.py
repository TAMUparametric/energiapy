from __future__ import annotations

from typing import TYPE_CHECKING

from ...tasks.task_map import task_map

if TYPE_CHECKING:
    from ...type.alias import IsComponent, IsInput, IsTask


def birth_task(component: IsComponent, attr_name: str) -> IsTask:
    """Births Task from component attribute

    Args:
        attr_name (str): name of the attribute

    Returns:
        IsTask: Task that a company does
    """
    current_value = getattr(component, attr_name)
    
    # Checks if attribute is already an Aspect
    if hasattr(current_value, '_tasked'):
        task = current_value
    # if not make an Aspect
    else:
        task = task_map[attr_name](component=component)

    return task

