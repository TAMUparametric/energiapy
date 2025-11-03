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
