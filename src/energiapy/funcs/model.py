from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..model.type.alias import IsComponent, IsValue, IsAspect


def model_updater(component: IsComponent, aspect: IsAspect):
    """updates parameters, varaibles and constraints of a component with those of an aspect

    Args:
        component (IsComponent): energiapy Component
        aspect (IsAspect): energiapy Aspect
    """
    for i in ['parameters', 'variables', 'constraints']:
        if hasattr(aspect, i):
            current = set(getattr(component, i))
            adding = set(getattr(aspect, i))
            setattr(component, i, sorted(list(current | adding)))
