"""Bound Input attributes for all Defined Components
"""

from dataclasses import dataclass, field, fields

# from ...core.isalias.inps.isinp import IsBnd


@dataclass
class _Transact:
    """Exchange of Cash"""

    spend: dict = field(default=None)
    earn: dict = field(default=None)


@dataclass
class _Emit:
    """Exchange of Emissions"""

    emit: dict = field(default=None)
    sequester: dict = field(default=None)


@dataclass
class _Trade:
    """Exchange of Resources"""

    # Trade at Locations
    buy: dict = field(default=None)
    sell: dict = field(default=None)
    # Trade between Linkages
    # Linkages go in one direction
    receive: dict = field(default=None)
    ship: dict = field(default=None)
    # Lose at Location or between Linkage
    lose: dict = field(default=None)
    recover: dict = field(default=None)


@dataclass
class _Use:
    """Use of Resources"""

    use: dict = field(default=None)
    dispose: dict = field(default=None)


@dataclass
class _Setup:
    """Set up of Operation"""

    setup: dict = field(default=None)
    dismantle: dict = field(default=None)


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
