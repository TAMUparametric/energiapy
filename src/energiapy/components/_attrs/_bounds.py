"""Bound Input attributes for all Defined Components
"""

from dataclasses import dataclass, field, fields

from ...core.isalias.inps.isinp import IsBnd


@dataclass
class _PlyBounds:
    """Bounds for Players"""

    has: IsBnd = field(default=None)
    needs: IsBnd = field(default=None)


@dataclass
class _CshBounds:
    """Bounds for Cash"""

    spend: IsBnd = field(default=None)
    earn: IsBnd = field(default=None)


@dataclass
class _EmnBounds:
    """Bounds for Emission"""

    emit: IsBnd = field(default=None)
    sequester: IsBnd = field(default=None)


@dataclass
class _UsdBounds:
    """Bounds for Land and Material (Used)"""

    use: IsBnd = field(default=None)
    dispose: IsBnd = field(default=None)


@dataclass
class _ResBounds:
    """Bounds for Resources"""

    # Trade at Locations
    buy: IsBnd = field(default=None)
    sell: IsBnd = field(default=None)
    # Trade between Linkages
    # Linkages go in one direction
    ship: IsBnd = field(default=None)
    # Lose at Location or between Linkage
    lose: IsBnd = field(default=None)
    recover: IsBnd = field(default=None)


@dataclass
class _OpnBounds:
    """Bounds for Operational Components"""

    setup: IsBnd = field(default=None)
    dismantle: IsBnd = field(default=None)


class _BoundAttrs:
    @staticmethod
    def bounds():
        """Returns all Bounds"""

        return sum(
            [
                [f.name for f in fields(bnds)]
                for bnds in [
                    _PlyBounds,
                    _CshBounds,
                    _EmnBounds,
                    _UsdBounds,
                    _ResBounds,
                    _OpnBounds,
                ]
            ],
            [],
        )
