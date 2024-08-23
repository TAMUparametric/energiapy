"""Scenario Tests
"""

import pytest

from .test_fixtures import scenario_bare, scenario_def, scenario_notok


def test_scenario_model_blocks(scenario_bare, scenario_def, scenario_notok):
    """Model blocks should be initialized"""
    assert hasattr(scenario_bare, 'model') is True
    assert hasattr(scenario_bare.model, 'system') is True
    assert hasattr(scenario_bare.model, 'data') is True
    assert hasattr(scenario_bare.model, 'matrix') is True
    assert hasattr(scenario_bare.model, 'program') is True
    # With defaults
    assert hasattr(scenario_def, 'model') is True
    assert hasattr(scenario_def.model, 'system') is True
    assert hasattr(scenario_def.model, 'data') is True
    assert hasattr(scenario_def.model, 'matrix') is True
    assert hasattr(scenario_def.model, 'program') is True
    # Unchill Scenario
    assert hasattr(scenario_notok, 'model') is True
    assert hasattr(scenario_notok.model, 'system') is True
    assert hasattr(scenario_notok.model, 'data') is True
    assert hasattr(scenario_notok.model, 'matrix') is True
    assert hasattr(scenario_notok.model, 'program') is True


def test_scenario_bare_defaults(scenario_bare):
    """Bare Scenario should have no default values"""
    assert scenario_bare.def_scope is False
    assert scenario_bare.def_players is False
    assert scenario_bare.def_cash is False
    assert scenario_bare.def_land is False
    assert scenario_bare.default is False
    assert scenario_bare.ok_overwrite is True
    assert scenario_bare.ok_nobasis is True
    assert scenario_bare.ok_nolabel is True
    assert scenario_bare.ok_inconsistent is True
    assert scenario_bare.chill is True
    assert scenario_bare.m is None
    # These come from System Block
    assert scenario_bare.players == []
    assert scenario_bare.scales == []
    assert scenario_bare.resources == []
    assert scenario_bare.resources_stg == []
    assert scenario_bare.resources_trn == []
    assert scenario_bare.materials == []
    assert scenario_bare.emissions == []
    assert scenario_bare.processes == []
    assert scenario_bare.storages == []
    assert scenario_bare.operations == []
    assert scenario_bare.transits == []
    assert scenario_bare.locations == []
    assert scenario_bare.linkages == []
    assert scenario_bare.spatials == []
    assert scenario_bare.nodes == []
    assert scenario_bare.edges == []
    assert scenario_bare.sources == []
    assert scenario_bare.sinks == []
    assert scenario_bare.pairs == []
    # These come from Program Block
    assert scenario_bare.variables == []
    assert scenario_bare.constraints == []
    assert scenario_bare.parameters == []
    assert scenario_bare.dispositions == []
    # These come from Data Block
    assert scenario_bare.ms == []
    assert scenario_bare.constants == []
    assert scenario_bare.datasets == []
    assert scenario_bare.thetas == []
    # These should not be initialized in bare Scenario
    with pytest.raises(
        AttributeError, match="'System' object has no attribute '_cash'"
    ):
        _ = scenario_bare.cash
        _ = scenario_bare.commodities

    with pytest.raises(
        AttributeError, match="'System' object has no attribute '_land'"
    ):
        _ = scenario_bare.land

    with pytest.raises(
        AttributeError, match="'System' object has no attribute '_network'"
    ):
        _ = scenario_bare.network

    with pytest.raises(
        AttributeError, match="'System' object has no attribute '_horizon'"
    ):
        _ = scenario_bare.horizon


def test_scenario_def_defaults(scenario_def):
    """Default Scenario should have some Components initialized"""
    assert scenario_def.def_scope is True
    assert scenario_def.def_players is True
    assert scenario_def.def_cash is True
    assert scenario_def.def_land is True
    assert scenario_def.default is True
    assert scenario_def.m is None
    # These come from System Block
    assert [i.name for i in scenario_def.players] == [
        'consumer',
        'dm',
        'earth',
        'market',
    ]
    assert [i.name for i in scenario_def.scales] == ['t0']
    assert scenario_def.resources == []
    assert scenario_def.resources_stg == []
    assert scenario_def.resources_trn == []
    assert scenario_def.materials == []
    assert [i.name for i in scenario_def.emissions] == [
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
    assert scenario_def.processes == []
    assert scenario_def.storages == []
    assert scenario_def.operations == []
    assert scenario_def.transits == []
    assert scenario_def.locations == []
    assert scenario_def.linkages == []
    assert scenario_def.spatials == []
    assert scenario_def.nodes == []
    assert scenario_def.edges == []
    assert scenario_def.sources == []
    assert scenario_def.sinks == []
    assert scenario_def.pairs == []
    # These come from Program Block
    assert scenario_def.variables == []
    assert scenario_def.constraints == []
    assert scenario_def.parameters == []
    assert scenario_def.dispositions == []
    # These come from Data Block
    assert scenario_def.ms == []
    assert scenario_def.constants == []
    assert scenario_def.datasets == []
    assert scenario_def.thetas == []
    # These are default commodities
    assert scenario_def.cash.name == 'csh_def'
    assert scenario_def.land.name == 'lnd_def'
    assert [i.name for i in scenario_def.commodities] == [
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
    assert scenario_def.horizon.name == 'hrz_def'
    assert scenario_def.network.name == 'ntw_def'


def test_scenario_notok(scenario_notok):
    """Unchill Scenario enforces stuff strictly"""
    assert scenario_notok.ok_overwrite is False
    assert scenario_notok.ok_nobasis is False
    assert scenario_notok.ok_nolabel is False
    assert scenario_notok.ok_inconsistent is False
    assert scenario_notok.chill is False
