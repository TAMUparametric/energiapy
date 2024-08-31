"""Bound input attributes for Components
"""

from dataclasses import dataclass, field

from ...core.aliases.inps.isinp import IsBnd


@dataclass
class _StgBirthing:
    """Bounds for Processes birthed in Storage

    Attributes:
        capacity_in (IsBnd): capacity of charging Process
        capacity_out (IsBnd): capacity of discharging Process

    """

    capacity_in: IsBnd = field(default=None)
    capacity_out: IsBnd = field(default=None)
