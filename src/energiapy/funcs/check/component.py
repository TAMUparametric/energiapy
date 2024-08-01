from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...types.alias import IsComponent, IsInput


def is_named(component: IsComponent, attr_input: IsInput) -> bool:
    """Checks if attribute is ready to be made into an Aspect

    Args:
        attr_value (IsInput): value assigned to aspect attribute

    Returns:
        bool: True if component is ready and value is assigned
    """
    cndtn_named = hasattr(component, '_named') and getattr(
        component, '_named')
    cndtn_value = attr_input is not None
    if cndtn_named and cndtn_value:
        return True
    else:
        return False
