"""Resource price intervals in the installed Gana/PPOPT workflow."""

import operator

import numpy as np
import pytest

from energia import Currency, Model, Periods, Process, Resource


def test_cost_of_two_units_over_price_interval():
    m = Model()
    m.labor = Resource(take=True, price=(7.86, 8.89))
    m.labor.release == 2
    m.cash.spend.obj()
    m.solve()
    assert len(m.program.solution.critical_regions) == 1
    spending = m.cash.spend.V()[0]
    for price, expected in [(7.86, 15.72), (8.375, 16.75), (8.89, 17.78)]:
        assert m.eval(price)[spending] == pytest.approx(expected)
        assert m.program.solution.evaluate_objective(np.array([[price]])) == pytest.approx(expected)


def test_optimal_supplier_changes_at_competing_price():
    m = Model()
    m.labor = Resource(take=True, price=(7.86, 8.89))
    m.contract = Resource(take=True, price=8.375)
    m.product = Resource(release_min=2)
    m.buy = Process(m.product == -m.labor)
    m.buy_contract = Process(m.product == -m.contract)
    m.buy.operate >= 0
    m.buy_contract.operate >= 0
    m.locate(m.buy, m.buy_contract)
    m.cash.spend.obj()
    m.solve()
    labor, contract = m.labor.consume.V()[0], m.contract.consume.V()[0]
    spending = m.cash.spend.V()[0]
    for price in [7.86, 8.374, 8.375, 8.376, 8.89]:
        values = m.eval(price)
        assert values[labor] + values[contract] == pytest.approx(2)
        assert values[spending] == pytest.approx(2 * min(price, 8.375))
        if price != 8.375:
            assert values[labor] == pytest.approx(2 if price < 8.375 else 0)


def test_hourly_prices_with_independent_intervals():
    m = Model()
    m.hour = Periods()
    m.shift = 2 * m.hour
    m.cash = Currency()
    m.power = Resource()
    m.power.consume(m.hour) >= 0
    m.power.release(m.hour) == [2, 3]
    m.cash.spend(m.power.consume, m.hour) == [(1, 3), (4, 6)]
    m.cash.spend.obj()
    m.solve()
    assert m.eval(2, 5)[m.cash.spend.V()[0]] == pytest.approx(19)


def test_repeat_binding_reuses_the_price_parameter():
    m = Model()
    m.labor = Resource(take=True, price=(7.86, 8.89))
    m.cash.spend(m.labor.consume) == (7.86, 8.89)
    with pytest.raises(ValueError, match="different price bounds"):
        m.cash.spend(m.labor.consume) == (8, 9)
    assert m.program.n_thetas == 1
    m.labor.release == 2
    m.cash.spend.obj()
    m.solve()
    assert m.eval(8.375)[m.cash.spend.V()[0]] == pytest.approx(16.75)


@pytest.mark.parametrize("compare", [operator.le, operator.ge], ids=["upper", "lower"])
def test_interval_price_requires_equality(compare):
    m = Model()
    m.labor = Resource(take=True)
    m.cash = Currency()
    with pytest.raises(ValueError, match="requires a spending equality"):
        compare(m.cash.spend(m.labor.consume), (1, 3))
    assert m.program.n_thetas == 0


@pytest.mark.parametrize(
    "original, replacement, error, expected_thetas",
    [
        (2, (1, 3), "fixed spending constraint", 0),
        ((1, 3), 2, "already has an uncertain price", 1),
    ],
    ids=["fixed-then-interval", "interval-then-fixed"],
)
def test_fixed_and_interval_prices_conflict(original, replacement, error, expected_thetas):
    m = Model()
    m.labor = Resource(take=True, price=original)
    with pytest.raises(ValueError, match=error):
        m.cash.spend(m.labor.consume) == replacement
    assert m.program.n_thetas == expected_thetas


def test_hourly_price_count_and_shared_interval():
    m = Model()
    m.hour = Periods()
    m.shift = 2 * m.hour
    m.cash = Currency()
    m.power = Resource()
    m.power.consume(m.hour) >= 0
    m.power.release(m.hour) == [2, 3]
    spending = m.cash.spend(m.power.consume, m.hour)
    with pytest.raises(ValueError, match="must match consumption coordinates"):
        spending == [(1, 3), (4, 6), (7, 9)]
    assert m.program.n_thetas == 0

    spending == (1, 3)
    assert m.program.n_thetas == 1
    m.cash.spend.obj()
    m.solve()
    total = m.cash.spend.V()[0]
    for price in [1, 2, 3]:
        assert m.eval(price)[total] == pytest.approx((2 + 3) * price)
