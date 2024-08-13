from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from ...type.alias import IsAspect, IsComponent


def add_element(component: TypeVar, aspect: IsAspect):
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