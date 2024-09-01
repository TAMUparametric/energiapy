"""Balance input attribures for Operational Components
"""

from dataclasses import dataclass, field

from ...core.isalias.inps.isblc import IsBlc, IsCnv


@dataclass
class _ProBalance:
    """Resource Balance for Process

    Attributes:
        conversion (IsCnv): Conversion balance

    """

    conversion: IsCnv = field(default=None)


@dataclass
class _StgBalance:
    """Resource Balance for Storage

    Attributes:
        invertory (IsBlc): Inventory balance

    """

    inventory: IsBlc = field(default=None)


@dataclass
class _TrnBalance:
    """Resource Balance for Transit

    Attributes:
        freight (IsBlc): Freight balance

    """

    freight: IsBlc = field(default=None)
