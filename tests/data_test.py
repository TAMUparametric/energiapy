"""Data Tests
"""

import pytest

from .test_fixtures import scenario_bare, scenario_def


def test_scenario_data(scenario_bare, scenario_def):
    """Both the bare and default Scenario Data Blocks
    should have no default values
    """
    assert scenario_bare.data.ms == []
    assert scenario_bare.data.constants == []
    assert scenario_bare.data.datasets == []
    assert scenario_bare.data.thetas == []
    assert scenario_def.data.ms == []
    assert scenario_def.data.constants == []
    assert scenario_def.data.datasets == []
    assert scenario_def.data.thetas == []
