"""Scenario Tests
"""

import pytest
from src.energiapy.model.scenario import Scenario


def test_scenario_creation():
    s = Scenario(name='TestScenario')
    assert s.name == 'TestScenario'
    assert s.m is None


def test_scenario_default_components():
    s = Scenario(default=True)
    assert hasattr(s.system, 'network')
    assert hasattr(s.system, 'horizon')
    assert hasattr(s.system, 'land')
    assert hasattr(s.system, 'cash')


def test_scenario_overwrite_component():
    s = Scenario()
    s.network = 'NewNetwork'
    assert s.system.network == 'NewNetwork'


def test_scenario_unique_components():
    s = Scenario()
    s.cash = 'NewCash'
    assert s.cash == 'NewCash'
    s.cash = 'AnotherCash'
    assert s.cash == 'NewCash'  # Overwriting should not be allowed


def test_scenario_eqns():
    s = Scenario()
    eqns = list(s.eqns())
    assert len(eqns) == 0


def test_scenario_eqns_at_component():
    s = Scenario()
    s.network = 'NewNetwork'
    eqns = list(s.eqns(at_cmp=s.network))
    assert len(eqns) == 0


def test_scenario_eqns_at_disposition():
    s = Scenario()
    eqns = list(s.eqns(at_disp='SomeDisposition'))
    assert len(eqns) == 0
