"""Test Horizon
"""

import pytest

from src.energiapy.components.scope.horizon import Horizon


@pytest.fixture
def singlescale_horizon():
    """Single scale with 4 discertizations"""
    return Horizon(discretizations=[4])


@pytest.fixture
def multiscale_scale():
    """Strictly scheduling with single scale with 4 discertizations"""
    return Horizon(discretizations=[4])
