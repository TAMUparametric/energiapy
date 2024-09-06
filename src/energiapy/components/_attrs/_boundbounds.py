"""Bound Bound Input attributes for all Defined Components
"""

from dataclasses import dataclass, field

from ...core.isalias.inps.isinp import IsBnd


@dataclass
class _ProBounds:
    """Bounds for Process

    Attributes:
        setup (IsBnd): bound on how much capacity can be setup
        produce (IsBnd): bound on how much capacity can be utilized (operated)
    """

    produce: IsBnd = field(default=None)


@dataclass
class _StgBounds:
    """Bounds for Storage

    Attributes:
        setup (IsBnd): bound on how much capacity can be setup
        store (IsBnd): bound on how much capacity can be utilized (operated)
    """

    store: IsBnd = field(default=None)


@dataclass
class _TrnBounds:
    """Bounds for Transit

    Attributes:
        setup (IsBnd): bound on how much capacity can be setup
        transport (IsBnd): bound on how much capacity can be utilized (operated)
    """

    transport: IsBnd = field(default=None)
