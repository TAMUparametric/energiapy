"""Scenario Fixtures
"""

import pytest 

from src.energiapy.model.scenario import Scenario

@pytest.fixture
def scenario_bare():
    """Scenario with no components"""
    return Scenario()

@pytest.fixture 
def
