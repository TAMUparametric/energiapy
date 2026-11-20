"""One-period process conversion coefficients."""

import pytest

from energia import Currency, Model, Process, Resource


@pytest.mark.parametrize(
    ("fuel_coefficient", "power_coefficient"),
    [(-5, 1), ([-5], [1])],
    ids=["scalar", "one-period"],
)
def test_one_period_fuel_conversion(
    fuel_coefficient, power_coefficient, solution_record
):
    model = Model()
    model.fuel, model.power = Resource(), Resource()
    model.usd = Currency()
    model.fuel.consume <= 10
    model.power.release >= 1
    model.plant = Process(model.power == fuel_coefficient * model.fuel)
    model.usd.spend(model.fuel.consume) == 3
    model.locate(model.plant)
    assert model.plant.balance[model.power] == power_coefficient
    model.usd.spend.opt()

    assert solution_record(model.program)["status"] == "optimal"
    assert model.fuel.consume.output(aslist=True) == pytest.approx([5])
    assert model.program.active_objective.X == pytest.approx(15)


def test_singleton_with_a_longer_series():
    model = Model()
    model.fuel, model.power, model.heat = Resource(), Resource(), Resource()
    conversion = [-5] * model.fuel + [1, 2] * model.power + model.heat
    conversion.balancer()

    assert dict(conversion) == {
        model.fuel: [-5],
        model.power: [1, 2],
        model.heat: [1, 1],
    }


def test_empty_coefficient_list():
    model = Model()
    model.fuel, model.power = Resource(), Resource()
    conversion = [] * model.fuel + model.power

    with pytest.raises(ValueError, match="empty coefficient list"):
        conversion.balancer()
