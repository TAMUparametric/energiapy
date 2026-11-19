"""Behavior of modeling selections and domain queries."""

import pytest

from energia import Location, Model, Periods, Process, Resource
from energia.modeling.indices.domain import Domain


def test_problem_lists_domains_for_each_registered_aspect():
    model = Model()
    assert model.problem.get(keys="domains", values="aspects") == {}

    model.hour, model.site, model.power = Periods(), Location(), Resource()
    supply = model.power.consume(model.site, model.hour)
    demand = model.power.release(model.site, model.hour)
    _ = supply <= 10
    _ = demand >= 1

    domains = model.problem.get(keys="streams", values="domains")
    assert domains[model.consume] == [supply.domain.tup]
    assert domains[model.release] == [demand.domain.tup]
    assert supply.domain.isroot
    assert not supply.domain("commodity", "location").isroot


def test_problem_rejects_unknown_collection():
    with pytest.raises(ValueError, match="keys must be one of"):
        Model().problem.get(keys="unknown")


def test_domain_requires_a_primary_index():
    with pytest.raises(ValueError, match="at least one primary index"):
        _ = Domain(location=Location(), periods=Periods()).primary


def test_operate_rejects_a_resource_as_its_primary_index():
    model = Model()
    model.fuel, model.plant = Resource(), Process()
    assert model.operate(model.plant).domain.primary is model.plant
    with pytest.raises(ValueError, match="fuel.*not recognized as an index"):
        model.operate(model.fuel)
