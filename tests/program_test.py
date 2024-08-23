"""Program Tests
"""

import pytest

from .test_fixtures import scenario_bare, scenario_def


def test_scenario_bare_program(scenario_bare, scenario_def):
    """Bare Scenario Model should have no default values"""
    assert scenario_bare.program.blocks == []
    assert scenario_bare.program.variables == []
    assert scenario_bare.program.constraints == []
    assert scenario_bare.program.parameters == []
    assert scenario_bare.program.dispositions == []


def test_scenario_def_program(scenario_def):
    """Default Scenario should have some Components initialized"""
    assert [i.name for i in scenario_def.program.blocks] == [
        'Program|lnd_def|',
        'Program|csh_def|',
        'Program|gwp|',
        'Program|ap|',
        'Program|epm|',
        'Program|epf|',
        'Program|ept|',
        'Program|pocp|',
        'Program|odp|',
        'Program|adpmn|',
        'Program|adpmt|',
        'Program|adpf|',
        'Program|wdp|',
        'Program|dm|',
        'Program|market|',
        'Program|consumer|',
        'Program|earth|',
    ]
    assert scenario_def.program.variables == []
    assert scenario_def.program.constraints == []
    assert scenario_def.program.parameters == []
    assert scenario_def.program.dispositions == []
