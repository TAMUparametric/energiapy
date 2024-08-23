"""Operational Components that give birth to Processes
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from ._operational import _Operational


@dataclass
class _Birther(_Operational, ABC):
    """Operations that have balance
    They give birth to input and output Processes
    They have input and output conversions
    They have input and output balances
    """

    def __post_init__(self):
        _Operational.__post_init__(self)

    @property
    @abstractmethod
    def balance(self):
        """Balance attribute"""

    @property
    @abstractmethod
    def capacity_in(self):
        """Process Capacity for Input Process"""

    @property
    @abstractmethod
    def capacity_out(self):
        """Process Capacity for Output Process"""

    @property
    def processes(self):
        """Birthed Processes"""
        return self._processes

    @processes.setter
    def processes(self, processes):
        """Set Processes"""
        self._processes = processes

    @property
    def process_in(self):
        """Process from Resource to Birthed Resource"""
        return self.processes[0]

    @property
    def process_out(self):
        """Process from Birthed Resource to Resource"""
        return self.processes[1]

    @property
    def conversion_in(self):
        """Conversion from Resource to Birthed Resource"""
        return getattr(self.system, getattr(self, 'name')).process_in.conversion

    @property
    def conversion_out(self):
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
