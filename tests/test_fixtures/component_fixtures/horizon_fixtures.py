"""Fixtures to test Horizon
"""

import pytest

from src.energiapy.components.scope.horizon import Horizon


@pytest.fixture()
def singlescale_horizon():
    """Single scale with 4 discertizations"""
    return Horizon(discretizations=[4])


@pytest.fixture()
def scheduling_single_level_scale():
    """Strictly scheduling with single scale with 4 discertizations"""
    return Horizon(discretizations=[4])


