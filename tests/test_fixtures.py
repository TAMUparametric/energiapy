"""Test Fixtures
"""

import pytest

from src.energiapy.components.spatial.network import Network
from src.energiapy.components.temporal.horizon import Horizon
from src.energiapy.environ.scenario import Scenario


@pytest.fixture
def scenario_bare():
    """Bare Scenario with no components"""
    return Scenario()


@pytest.fixture
def scenario_def():
    """Scenario with all default components"""
    return Scenario(default=True)


@pytest.fixture
def scenario_ok():
    """Chill Scenario"""
    s = Scenario()
    s.h = Horizon(discretizations=[4])
    s.n = Network()
    return s


@pytest.fixture
def scenario_notok():
    """Unchill Scenario"""
    s = Scenario(chill=False)
    s.h = Horizon(discretizations=[4])
    s.n = Network()
    return s


@pytest.fixture
def horizon_singlescale(scenario_bare):
    """Single scale with 4 discertizations"""

    scenario_bare.h = Horizon(discretizations=[4])
    return scenario_bare.horizon


@pytest.fixture
def horizon_singlescale_scale_0(horizon_singlescale):
    """t0 single scale"""
    return horizon_singlescale.scales[0]


@pytest.fixture
def horizon_singlescale_scale_1(horizon_singlescale):
    """t1 single scale"""
    return horizon_singlescale.scales[1]


@pytest.fixture
def horizon_multiscale(scenario_bare):
    """Multiscale Horizon with 2 and 4 discertizations"""
    scenario_bare.h = Horizon(discretizations=[2, 4])
    return scenario_bare.horizon


@pytest.fixture
def horizon_multiscale_scale_0(horizon_multiscale):
    """t0 multiscale"""
    return horizon_multiscale.scales[0]


@pytest.fixture
def horizon_multiscale_scale_1(horizon_multiscale):
    """t1 multiscale"""
    return horizon_multiscale.scales[1]


@pytest.fixture
def horizon_multiscale_scale_2(horizon_multiscale):
    """t2 multiscale"""
    return horizon_multiscale.scales[2]


@pytest.fixture
def horizon_multiscale_un(scenario_bare):
    """Not nested Multiscale Horizon with 2 and 8 discertizations"""
    scenario_bare.h = Horizon(discretizations=[2, 8], nested=False)
    return scenario_bare.horizon


@pytest.fixture
def horizon_multiscale_un_scale_0(horizon_multiscale_un):
    """t0 multiscaleun"""
    return horizon_multiscale_un.scales[0]


@pytest.fixture
def horizon_multiscale_un_scale_1(horizon_multiscale_un):
    """t1 multiscaleun"""
    return horizon_multiscale_un.scales[1]


@pytest.fixture
def horizon_multiscale_un_scale_2(horizon_multiscale_un):
    """t2 multiscaleun"""
    return horizon_multiscale_un.scales[2]


@pytest.fixture
def horizon_multiscale_nmd(scenario_bare):
    """Named Multiscale Horizon with 2 and 4 discertizations"""
    scenario_bare.h = Horizon(discretizations={'a': 2, 'b': 4})
    return scenario_bare.horizon


@pytest.fixture
def horizon_multiscale_nmd_scale_0(horizon_multiscale_nmd):
    """t0 multiscale"""
    return horizon_multiscale_nmd.scales[0]


@pytest.fixture
def horizon_multiscale_nmd_scale_1(horizon_multiscale_nmd):
    """t1 multiscale"""
    return horizon_multiscale_nmd.scales[1]


@pytest.fixture
def horizon_multiscale_nmd_scale_2(horizon_multiscale_nmd):
    """t2 multiscale"""
    return horizon_multiscale_nmd.scales[2]
