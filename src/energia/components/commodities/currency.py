"""Currency."""

from __future__ import annotations

from operator import is_
from typing import TYPE_CHECKING, Self

from ...modeling.parameters.conversion import Conversion
from .commodity import Commodity

if TYPE_CHECKING:
    from ...components.spatial.location import Location


class Currency(Commodity):
    """
    Same as Economic Impact (Eco).

    :param label: Label of the commodity, used for plotting. Defaults to None.
    :type label: str, optional
    :param name: Name of the commodity, used for indexing. Defaults to None.
    :type name: str, optional

    :ivar model: The model to which the component belongs.
    :vartype model: Model
    :ivar name: Set when the component is assigned as a Model attribute.
    :vartype name: str
    :ivar constraints: List of constraints associated with the component.
    :vartype constraints: list[str]
    :ivar domains: List of domains associated with the component.
    :vartype domains: list[Domain]
    :ivar aspects: Aspects associated with the component with domains.
    :vartype aspects: dict[Aspect, list[Domain]]
    :ivar conversions: List of conversions associated with the commodity. Defaults to [].
    :vartype conversions: list[Conversion]
    :ivar insitu: If the commodity only exists insitu, i.e., does not scale any domains
    :vartype insitu: bool, optional
    """

    locs: list[Location] | None = None

    def __init__(
        self,
        *locs: Location,
        label: str = "",
        citations: str = "",
        **kwargs,
    ):
        """Assign this currency to the supplied locations and their recorded descendants."""
        self.locs = list(locs)
        Commodity.__init__(self, label=label, citations=citations, **kwargs)

        # dictionary of exchange rates
        self.exchange: dict[Self, float] = {}

        if self.locs:
            for loc in self.locs:
                loc.currency = self
                for child in loc.alsohas:
                    child.currency = self

    def howmany(self, cash: Self):
        """
        Return the stored exchange rate relative to the supplied currency.

        .. admonition:: Example

            .. code-block:: python

                from energia import Currency, Model

                m = Model()
                m.usd, m.credit = Currency(), Currency()
                m.credit == 2 * m.usd
                assert m.credit.howmany(m.usd) == 2
                assert m.usd.howmany(m.credit) == 0.5
        """
        if is_(cash, self):
            return 1
        if cash in self.exchange:
            return self.exchange[cash]

        # # find a common currency
        # if list(self.conversion)[0] == list(cash.conversion)[0]:
        #     return (
        #         self.conversion[list(self.conversion)[0]]
        #         / cash.conversion[list(cash.conversion)[0]]
        #     )
        message = f"{cash} does not have an exchange rate set {self.name}"
        raise ValueError(message)

    def _compare_currency(self, other: Self) -> bool:
        """Compare two currencies for equality."""
        if is_(self, other):
            return True

        self.exchange[other] = 1.0
        return False

    def _set_exchange(self, other: Conversion) -> bool:
        """Set exchange rates between two currencies."""
        if not other.balance:
            message = "list index out of range"
            raise IndexError(message)
        currency: Self = next(iter(other.balance))
        rate: float = other.balance[currency]

        # set the exchange rate of self against other
        self.exchange[currency] = rate

        for ex in currency.exchange:
            if ex not in self.exchange:
                self.exchange[ex] = rate / currency.exchange[ex]

                if self not in ex.exchange:
                    ex.exchange[self] = ex.exchange[currency] / rate

                # if self not in ex.exchange:
                #     ex.exchange[self] = currency.exchange[ex] / rate

        # set the exchange rate of other against self
        currency.exchange[self] = 1 / rate
        return True

    def __eq__(self, other):
        """Set reciprocal rates from a conversion, or record a unit rate for a distinct currency."""
        if isinstance(other, Currency):
            return self._compare_currency(other)

        elif isinstance(other, Conversion):
            return self._set_exchange(other)

        return False
