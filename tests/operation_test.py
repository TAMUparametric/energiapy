import pytest

from energia import Linkage, Location, Model, Periods, Process, Resource, Storage, Transport


@pytest.fixture
def model():
    m = Model()
    m.hour = Periods()
    m.day = 3 * m.hour
    m.site, m.other = Location(), Location()
    m.power = Resource()
    return m


@pytest.mark.parametrize("hourly", [False, True])
def test_process_operating_bound_uses_local_time_or_horizon(model, hourly):
    m = model
    m.plant = Process()
    m.fuel = Resource()
    m.plant(m.power) == -m.fuel
    m.plant.capacity(m.site, m.day) == 10
    if hourly:
        m.plant.operate(m.site, m.hour) >= 0

    m.site.locate(m.plant)

    period = m.hour if hourly else m.day
    assert m.scenario[m.operate][m.plant][m.site] == {period: {"ub": 1}}


def test_first_transport_placement_bounds_activity_on_link(model):
    m = model
    m.route = Linkage(source=m.site, sink=m.other)
    m.truck = Transport()
    m.truck(m.power) == 1

    m.truck.locate(m.route)

    assert m.scenario[m.operate][m.truck][m.route] == {m.day: {"ub": 1}}


def test_first_storage_placement_bounds_charge_and_discharge(model):
    m = model
    m.battery = Storage(m.power == 0.9)

    m.battery.locate(m.site)

    for process in (m.battery.charge, m.battery.discharge):
        assert m.scenario[m.operate][process][m.site] == {m.day: {"ub": 1}}


def test_process_conversion_properties(model):
    m = model
    m.plant = Process()
    m.fuel = Resource()
    lag = -m.day
    m.plant(m.power, lag=lag) == -m.fuel
    assert m.plant.basis is m.power
    assert m.plant.balance is m.plant.production.balance
    assert m.plant.lag is lag

    m.plant.production = None
    assert m.plant.basis is None
    assert m.plant.balance is None
    assert m.plant.lag is None
