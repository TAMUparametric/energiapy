import logging
import operator

import pytest

from energia import Location, Model, Periods, Resource, Storage


@pytest.fixture
def model():
    m = Model()
    m.hour = Periods()
    m.day = 3 * m.hour
    m.site, m.other = Location(), Location()
    m.power = Resource()
    m.battery = Storage(m.power == 0.9)
    m.battery.charge.operate(m.site, m.hour) >= 0
    m.battery.discharge.operate(m.site, m.hour) >= 0
    return m


@pytest.mark.parametrize(
    ("bind", "limit"), [(operator.le, 100), (operator.le, 0), (operator.eq, 60)]
)
def test_locate_recognizes_existing_storage_capacity(model, caplog, bind, limit):
    m = model
    capacity = m.battery.capacity(m.site, m.day)
    bind(capacity, limit)
    bound_spaces = m.invcapacity.bound_spaces[m.battery.stored].copy()
    caplog.set_level(logging.INFO, logger="energia")

    fingerprints = []
    for _ in range(2):
        m.site.locate(m.battery)
        capacity.opt(maximize=True)
        fingerprints.append(m.program.formulation.Fingerprint)
        assert capacity.output(aslist=True) == [limit]
        assert m.invcapacity.bound_spaces[m.battery.stored] == bound_spaces
    assert fingerprints[0] == fingerprints[1]
    assert "Assumed battery capacity unbounded" not in caplog.text


@pytest.mark.parametrize(
    "existing", ["none", "lower", "other_site", "other_period", "other_storage"]
)
def test_locate_declares_missing_horizon_capacity(model, caplog, existing):
    m = model
    if existing == "lower":
        m.battery.capacity(m.site, m.day) >= 12
    elif existing == "other_site":
        m.battery.capacity(m.other, m.day) <= 100
    elif existing == "other_period":
        m.battery.capacity(m.site, m.hour) <= 100
    elif existing == "other_storage":
        m.reserve = Storage(m.power == 0.8)
        m.reserve.capacity(m.site, m.day) <= 100

    caplog.set_level(logging.INFO, logger="energia")
    m.site.locate(m.battery)
    assert "Assumed battery capacity unbounded in (site, day)" in caplog.text
    assert any(
        domain.space is m.site and domain.time is m.day
        for domain in m.invcapacity.domains
    )
