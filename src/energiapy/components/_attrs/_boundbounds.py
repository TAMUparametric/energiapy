"""Bound Bound Input attributes for all Defined Components
"""

from dataclasses import dataclass, field, fields

from ...core.isalias.inps.isinp import IsBnd


@dataclass
class _OpnBoundBounds:
    """Bound Bounds for Operational Components

    Attributes:
        operate (IsBnd): bound on how much capacity (setup) can be utilized
    """

    operate: IsBnd = field(default=None)


class _BoundBoundAttrs:
    """Bound Bound Input attributes for all Defined Components"""

    @staticmethod
    def boundbounds():
        """Returns all BoundBounds"""
        return sum(
            [[f.name for f in fields(bnds)] for bnds in [_OpnBoundBounds]],
            [],
        )
