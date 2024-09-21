"""Operational Components that give birth to Processes
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ._operation import _Operation

if TYPE_CHECKING:
    from ...elements.parameters.balances.conversion import Conversion
    from .process import Process


@dataclass
class _Birther(_Operation):
    """Operations that have balance
    They give birth to input and output Processes
    They have input and output conversions
    They have input and output balances
    """

    def __post_init__(self):
        # flag to check whether proceses have been birthed
        # important to know what capacity Transit should pass on
        # basically, conversion_in and conversion_out
        # The processes inherit the original capacities
        # (before they are made into SpatioTemporal Dicts)
        self.birthed = False
        _Operation.__post_init__(self)

        self.process_in: Process = None
        self.process_out: Process = None

    @property
    def processes(self) -> list[Process]:
        """Processes that are birthed"""
        return [self.process_in, self.process_out]

    @property
    def conversion_in(self) -> Conversion:
        """Conversion from Resource to Birthed Resource"""
        return self.process_in.conversion

    @property
    def conversion_out(self) -> Conversion:
        """Conversion from Birthed Resource to Resource"""
        return self.process_out.conversion

    @property
    def balance_in(self):
        """Balance from Resource to Birthed Resource"""
        return self.conversion_in.balance

    @property
    def balance_out(self):
        """Balance from Birthed Resource to Resource"""
        return self.conversion_out.balance

    @property
    def resources(self):
        """Resources in Balance"""
        return sorted(set(self.conversion_in.involved))
