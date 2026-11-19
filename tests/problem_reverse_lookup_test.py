"""Domain-to-aspect queries on the registrations made by model constraints."""

import pytest

from energia import Currency, Location, Model, Periods, Process, Resource


def test_reverse_lookup_groups_shared_domains_and_filters_aspect_families():
    m = Model()
    m.hour, m.site = Periods(), Location()
    m.power, m.fuel, m.plant = Resource(), Resource(), Process()
    supply = m.power.consume(m.site, m.hour)
    demand = m.power.release(m.site, m.hour)
    fuel = m.fuel.consume(m.site, m.hour)
    operation = m.plant.operate(m.site, m.hour)
    _ = supply <= 10
    _ = demand >= 1
    _ = fuel <= 4
    _ = operation <= 2

    # The two independent selections share a domain. A second bound must
    # not add the same aspect a second time.
    _ = supply >= 1
    streams = m.problem.get(keys="domains", values="streams")
    assert set(streams[supply.domain]) == {m.consume, m.release}
    assert len(streams[demand.domain]) == 2
    assert streams[fuel.domain] == [m.consume]
    assert operation.domain not in streams

    aspects = m.problem.get(keys="domains", values="aspects")
    assert set(aspects) == set(m.problem.domains)
    assert m.operate in aspects[operation.domain]
    assert m.problem.get(keys="domains", values="states")[operation.domain] == [
        m.operate
    ]


def test_reverse_lookup_preserves_a_domain_with_a_dependent_sample():
    m = Model()
    m.hour, m.site = Periods(), Location()
    m.plant, m.usd = Process(), Currency()
    operation = m.plant.operate(m.site, m.hour)
    _ = operation <= 2
    cost = m.usd.spend(operation, m.site, m.hour)
    _ = cost == 3

    assert cost.domain.samples == [operation]
    assert m.spend in m.problem.get(keys="domains", values="aspects")[cost.domain]
    assert cost.domain.tup in m.problem.get()[m.spend]


def test_domain_to_domain_query_returns_registered_domains():
    m = Model()
    assert m.problem.get(keys="domains") == {}
    m.hour, m.site, m.power = Periods(), Location(), Resource()
    supply = m.power.consume(m.site, m.hour)
    _ = supply <= 10

    assert m.problem.get(keys="domains")[supply.domain] == [supply.domain]
    with pytest.raises(ValueError, match="values"):
        m.problem.get(keys="domains", values="unknown")
