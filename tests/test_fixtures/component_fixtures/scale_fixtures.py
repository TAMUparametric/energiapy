"""Fixtures to test Scale
"""

import pytest



@pytest.fixture()
def single_level_scale():
    """Single scale with 4 discertizations"""
    return TemporalScale(discretization_list=[4])


@pytest.fixture()
def scheduling_single_level_scale():
    """Strictly scheduling with single scale with 4 discertizations"""
    return TemporalScale(discretization_list=[4], scheduling_scale=0)

