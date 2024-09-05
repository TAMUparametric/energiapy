"""Bound input attributes for Components
"""

from dataclasses import dataclass, field

from ...core.isalias.inps.isinp import IsBnd


@dataclass
class _StgBirthing:
    """Bounds for Processes birthed in Storage

    Attributes:
        capacity_in (IsBnd): capacity of charging Process
        capacity_out (IsBnd): capacity of discharging Process

    """

    setup_in: IsBnd = field(default=None)
    setup_out: IsBnd = field(default=None)
