"""Different Pre-Set Conversions"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .conversion import Conversion

if TYPE_CHECKING:
    from ...components.commodities.commodity import Commodity
    from ...components.operations.operation import Operation
    from ...components.operations.storage import Storage
    from ...components.spatial.linkage import Linkage
    from ...components.spatial.location import Location
    from ...components.temporal.lag import Lag
    from ...components.temporal.modes import Modes
    from ...components.temporal.periods import Periods
    from ...represent.model import Model
    from ..indices.sample import Sample


class Production(Conversion):
    """Process Production"""

    def __init__(
        self,
        operation: Operation | Storage | None = None,
        resource: Commodity | None = None,
        balance: dict[Commodity, float | list[float]] | None = None,
        hold: int | float | None = None,
        symbol: str = "η",
        use_max_time: bool = False,
    ):
        Conversion.__init__(
            self,
            operation=operation,
            aspect="operate",
            add="produce",
            sub="expend",
            resource=resource,
            balance=balance,
            hold=hold,
            attr_name="production",
            symbol=symbol,
            use_max_time=use_max_time,
        )


class Construction(Conversion):
    """Operation Construction Conversion"""

    def __init__(
        self,
        operation: Operation | Storage | None = None,
        aspect: str = "capacity",
        resource: Commodity | None = None,
        balance: dict[Commodity, float | list[float]] | None = None,
        hold: int | float | None = None,
        symbol: str = "γ",
        use_max_time: bool = True,
    ):
        Conversion.__init__(
            self,
            operation=operation,
            aspect=aspect,
            add="dispose",
            sub="use",
            resource=resource,
            balance=balance,
            hold=hold,
            attr_name="construction",
            symbol=symbol,
            use_max_time=use_max_time,
        )


class Transportation(Conversion):
    """Transport Conversion"""

    def __init__(
        self,
        operation: Operation | Storage | None = None,
        resource: Commodity | None = None,
        balance: dict[Commodity, float | list[float]] | None = None,
        hold: int | float | None = None,
        symbol: str = "τ",
        use_max_time: bool = False,
    ):
        Conversion.__init__(
            self,
            operation=operation,
            aspect="operate",
            add="ship_in",
            sub="ship_out",
            resource=resource,
            balance=balance,
            hold=hold,
            attr_name="transportation",
            symbol=symbol,
            use_max_time=use_max_time,
        )

    # overwrite, since transportation balance is slightly different
    def write(self, space: Linkage, time: Periods | Lag, modes: Modes | None = None):
        """Writes equations for conversion balance"""

        res = list(self)[0]

        par = self[res]

        eff = par if isinstance(par, list) else [par]

        decision = getattr(self.operation, self.aspect)

        ship_in = getattr(res, self.add)
        ship_out = getattr(res, self.sub)

        if modes:
            lhs = decision(space, modes, time)
            rhs_in = ship_in(decision, space.source, modes, time)
            rhs_out = ship_out(decision, space.sink, modes, time)

        else:
            lhs = decision(space, time)
            rhs_in = ship_in(decision, space.source, time)
            rhs_out = ship_out(decision, space.sink, time)

        _ = lhs[rhs_in] == eff
        _ = lhs[rhs_out] == [-i for i in eff]
