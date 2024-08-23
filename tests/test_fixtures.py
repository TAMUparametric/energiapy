"""Test Fixtures
"""

import pytest

from src.energiapy.model.scenario import Scenario
from src.energiapy.components.scope.horizon import Horizon


@pytest.fixture
def scenario_bare():
    """Bare Scenario with no components"""
    return Scenario()


@pytest.fixture
def scenario_def():
    """Scenario with all default components"""
    return Scenario(default=True)


@pytest.fixture
def singlescale_horizon():
    """Single scale with 4 discertizations"""
    return Horizon(discretizations=[4])


@pytest.fixture
def multiscale_horizon():
    """Multiscale Horizon with 2 and 4 discertizations"""
    return Horizon(discretizations=[2, 4])

