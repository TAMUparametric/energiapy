"""Custom Error Classes
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..isalias.cmps.iscmp import IsCmp


class CacodcarError(ValueError):
    """This error could be because of some booboo I made"""

    def __init__(self, message):
        self.message = f'{message}\n This could be a developer error\n raise an issue on github if you think this is a bug\n or contact cacodcar@tamu.edu\n'

        super().__init__(self.message)


def check_attr(component: IsCmp, attr: str):
    """Checks if an attribute is present in the Component

    Args:
        component (IsCmp): Component to check
        attr (str): Attribute to check

    """
    if not hasattr(component, attr):
        raise CacodcarError(f'{type(component)} has no attribute {attr}')


class OverWriteError(AttributeError):
    """Error for Overwriting attributes

    Attributes:
        cmp (str): Component being overwritten
    """

    def __init__(self, cmp):
        self.message = (
            f'{cmp} already exists\nset Scenario.ok_overwrite=True if intentional'
        )

        super().__init__(self.message)


class NoBasisError(AttributeError):
    """Error for having no basis

    Attributes:
        component (IsCmp): Component with no basis
    """

    def __init__(self, component: IsCmp):
        self.message = (
            f'{component} has no basis\nset Scenario.ok_basis=True if intentional'
        )

        super().__init__(self.message)


class NoLabelError(AttributeError):
    """Error for having no label

    Attributes:
        component (IsCmp): Component with no label
    """

    def __init__(self, component: IsCmp):
        self.message = (
            f'{component} has no label\nset Scenario.ok_label=True if intentional'
        )

        super().__init__(self.message)


class NoScaleMatchError(ValueError):
    """Error for no scale match

    Attributes:
        component (IsCmp): Component with no scale match
        value (Any): Value with length
        attr (str): Attribute being checked
    """

    def __init__(self, value: Any, component: IsCmp, attr: str):
        self.message = (
            f'{component}: Length ({len(value)}) of {attr}  does not match any scale'
        )

        super().__init__(self.message)


class InconsistencyError(AttributeError):
    """Error for spatiotemporal inconsistencies

    Attributes:
        component (str): Component with inconsistency
        attr (str): Attribute with inconsistency
        spt (str): Spatial Component
        tmp (str): Scale
        scale_upd (str): Updated Scale
    """

    def __init__(self, component, attr, spt, tmp, scale_upd):
        self.message = f'{component}.{attr}:Inconsistent temporal scale for {spt} at {tmp}.\nUpdating to {scale_upd}.\nSet Scneario.ok_inconsistent=True, to let energiapy fix scales'

        super().__init__(self.message)


class InputTypeError(TypeError):
    """Error for wrong input type

    Attributes:
        component (IsCmp): Component with wrong input type
        attr (str): Attribute with wrong input type
        value (Any): Value with wrong input type
    """

    def __init__(self, message: str, component: IsCmp, attr: str, value: Any):
        msg_bounds = '\nCheck Scenario.attr.bounds() for Bound attrs.'
        msg_exact = '\nCheck Scenario.attr.exacts() for Exact attrs.'
        msg_alias = '\nCheckout energiapy.core.aliases.is_input for valid input types.'
        self.message = f'{value} [{type(value)}] is not a valid input for {component}.{attr}.\n{message}.{msg_bounds}{msg_exact}{msg_alias}'

        super().__init__(self.message)
