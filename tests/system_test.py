"""System Tests
"""

import pytest

from .test_fixtures import scenario_bare, scenario_def


def test_scenario_bare_system_defaults(scenario_bare):
    """Bare Scenario System should have no default values"""
    assert scenario_bare.system.players == []
    assert scenario_bare.system.scales == []
    assert scenario_bare.system.resources == []
    assert scenario_bare.system.resources_stg == []
    assert scenario_bare.system.resources_trn == []
    assert scenario_bare.system.materials == []
    assert scenario_bare.system.emissions == []
    assert scenario_bare.system.processes == []
    assert scenario_bare.system.storages == []
    assert scenario_bare.system.transits == []
    assert scenario_bare.system.operations == []
    assert scenario_bare.system.locations == []
    assert scenario_bare.system.linkages == []
    assert scenario_bare.system.spatials == []
    assert scenario_bare.system.nodes == []
    assert scenario_bare.system.edges == []
    assert scenario_bare.system.sources == []
    assert scenario_bare.system.sinks == []
    assert scenario_bare.system.pairs == []

    # These should not be initialized in bare Scenario System
    with pytest.raises(
        AttributeError, match="'System' object has no attribute '_cash'"
    ):
        _ = scenario_bare.system.cash
        _ = scenario_bare.system.commodities

    with pytest.raises(
        AttributeError, match="'System' object has no attribute '_land'"
    ):
        _ = scenario_bare.system.land

    with pytest.raises(
        AttributeError, match="'System' object has no attribute '_network'"
    ):
        _ = scenario_bare.system.network

    with pytest.raises(
        AttributeError, match="'System' object has no attribute '_horizon'"
    ):
        _ = scenario_bare.system.horizon


def test_scenario_def_system_defaults(scenario_def):
    """Default Scenario should have some Components initialized"""
    assert [i.name for i in scenario_def.system.players] == [
        'consumer',
        'dm',
        'earth',
        'market',
    ]
    assert [i.name for i in scenario_def.system.scales] == ['t0']
    assert scenario_def.system.resources == []
    assert scenario_def.system.resources_stg == []
    assert scenario_def.system.resources_trn == []
    assert scenario_def.system.materials == []
    assert [i.name for i in scenario_def.system.emissions] == [
        'adpf',
        'adpmn',
        'adpmt',
        'ap',
        'epf',
        'epm',
        'ept',
        'gwp',
        'odp',
        'pocp',
        'wdp',
    ]
    assert scenario_def.system.processes == []
    assert scenario_def.system.storages == []
    assert scenario_def.system.operations == []
    assert scenario_def.system.transits == []
    assert scenario_def.system.locations == []
    assert scenario_def.system.linkages == []
    assert scenario_def.system.spatials == []
    assert scenario_def.system.nodes == []
    assert scenario_def.system.edges == []
    assert scenario_def.system.sources == []
    assert scenario_def.system.sinks == []
    assert scenario_def.system.pairs == []
    # These are default commodities
    assert scenario_def.system.cash.name == 'csh_def'
    assert scenario_def.system.land.name == 'lnd_def'
    assert [i.name for i in scenario_def.system.commodities] == [
        'adpf',
        'adpmn',
        'adpmt',
        'ap',
        'epf',
        'epm',
        'ept',
        'gwp',
        'odp',
        'pocp',
        'wdp',
        'csh_def',
        'lnd_def',
    ]
    # These are defuault scopes
    assert scenario_def.system.horizon.name == 'hrz_def'
    assert scenario_def.system.network.name == 'ntw_def'
