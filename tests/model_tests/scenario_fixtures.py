"""Scenario Fixtures
"""

import pytest

from src.energiapy.model.scenario import Scenario


@pytest.fixture
def scenario_bare():
    """Scenario with no components"""
    return Scenario()


@pytest.fixture
def scenario_default():
    """Scenario with default components"""
    return Scenario(default=True)
