"""Custom Error and Warning Classes"""

from __future__ import annotations

from typing import TYPE_CHECKING
import warnings

if TYPE_CHECKING:
    from ..aliases.is_component import IsComponent


class CacodcarError(ValueError):
    """This error could be because of some booboo I made"""

    def __init__(self, message):
        self.message = f'{message}\n This could be a developer error\n raise an issue on github if you think this is a bug\n or contact cacodcar@tamu.edu\n'

        super().__init__(self.message)


def check_attr(component: IsComponent, attr: str):
    """Checks if an attribute is present in the component

    Args:
        component (IsComponent): Component to check
        attr (str): Attribute to check

    """
    if not hasattr(component, attr):
        raise CacodcarError(f'{type(component)} has no attribute {attr}')


class OverWriteWarning(UserWarning):
    """Warning for overwriting attributes"""

    def __init__(self, cmp):
        self.message = f'\nA {cmp} object was already defined.\nOverwriting.\nThis should not cause any modeling issues.\nCheck Scenario defaults if unintended.\n'

    def __str__(self):
        return repr(self.message)
