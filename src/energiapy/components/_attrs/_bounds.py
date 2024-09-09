"""Bound Input attributes for all Defined Components
"""

from dataclasses import dataclass, field, fields

from ...core.isalias.inps.isinp import IsBnd


@dataclass
class _Transact:
    """Exchange of Cash"""

    spend: IsBnd = field(default=None)
    earn: IsBnd = field(default=None)


@dataclass
class _Emit:
    """Exchange of Emissions"""

    emit: IsBnd = field(default=None)
    sequester: IsBnd = field(default=None)


@dataclass
class _Trade:
    """Exchange of Resources"""

    # Trade at Locations
    buy: IsBnd = field(default=None)
    sell: IsBnd = field(default=None)
    # Trade between Linkages
    # Linkages go in one direction
    receive: IsBnd = field(default=None)
    ship: IsBnd = field(default=None)
    # Lose at Location or between Linkage
    lose: IsBnd = field(default=None)
    recover: IsBnd = field(default=None)


@dataclass
class _Use:
    """Use of Resources"""

    use: IsBnd = field(default=None)
    dispose: IsBnd = field(default=None)


@dataclass
class _Setup:
    """Set up of Operation"""

    setup: IsBnd = field(default=None)
    dismantle: IsBnd = field(default=None)


class _BoundAttrs:
    @staticmethod
    def bounds():
        """Returns all Bounds"""

        return [
            f.name
            for f in fields(_Transact)
            + fields(_Emit)
            + fields(_Trade)
            + fields(_Use)
            + fields(_Setup)
        ]
