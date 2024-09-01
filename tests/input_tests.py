"""Tests to verify whether inputs are being made consistent 
"""

import pytest

from src.energiapy.components.commodity.resource import Resource
from src.energiapy.components.scope.spatial.network import Network
from src.energiapy.components.scope.temporal.horizon import Horizon
from src.energiapy.components.scope.temporal.mode import X
from src.energiapy.core._handy._enums import _Dummy
from src.energiapy.environ.scenario import Scenario


@pytest.fixture
def scenario():
    """Scenario"""
    scn = Scenario()
    scn.hrz = Horizon(discretizations=[1])
    scn.ntw = Network(locs=['loca', 'locb'])
    scn.res = Resource()
    return scn


# handy


# personalized mode
@pytest.fixture
def x(scenario):
    return X(0).personalize(opn=scenario.res, attr='attr')


# Original Values
# These are user inputs

# -------- 0 layer Original ----------


@pytest.fixture
def val():
    """Value [Original]"""
    return 100


# Interim life cycle values


@pytest.fixture
def n_val():
    """N: Value"""
    return {_Dummy.N: 100}


@pytest.fixture
def n_t_val():
    """N: T: Value"""
    return {_Dummy.N: {_Dummy.T: 100}}


@pytest.fixture
def n_t_x_val():
    """N: T: X: Value"""
    return {_Dummy.N: {_Dummy.T: {_Dummy.X: 100}}}


# ----------- 1 layer originals with interim life cycles ------------


# [1]
@pytest.fixture
def mdeval():
    """Mode: Value [Original]"""
    return {X(0): 100}


@pytest.fixture
def n_mdeval():
    """N: Mode: Value"""
    return {_Dummy.N: {X(0): 100}}


@pytest.fixture
def n_t_mdeval():
    """N: T: Mode Value"""
    return {_Dummy.N: {_Dummy.T: {X(0): 100}}}


@pytest.fixture
def n_t_mdepval(x):
    """N: T: Mode Personalized Value"""
    return {_Dummy.N: {_Dummy.T: {x: 100}}}


# [2]
@pytest.fixture
def sptval(scenario):
    """Spatial Value [Original]"""
    return {scenario.loca: 100}


@pytest.fixture
def spt_t_val(scenario):
    """Spatial: T: Value"""
    return {scenario.loca: {_Dummy.T: 100}}


@pytest.fixture
def spt_t_x_val(scenario):
    """Spatial: T: X: Value"""
    return {scenario.loca: {_Dummy.T: {_Dummy.X: 100}}}


# [3]
@pytest.fixture
def tmpval(scenario):
    """Temporal: Value [Original]"""
    return {scenario.t0: 100}


@pytest.fixture
def n_tmpval(scenario):
    """N: Temporal: Value"""
    return {_Dummy.N: {scenario.t0: 100}}


@pytest.fixture
def n_tmp_x_val(scenario):
    """N: Temporal: X: Value"""
    return {_Dummy.N: {scenario.t0: {_Dummy.X: 100}}}


# ----- 2 layer Originals with interim life cycles ------
# [1]
@pytest.fixture
def tmpmdeval(scenario):
    """Temporal: Mode: Value [Original]"""
    return {scenario.t0: {X(0): 100}}


@pytest.fixture
def n_tmpmdeval(scenario):
    """N: Temporal: Value"""
    return {_Dummy.N: {scenario.t0: {X(0): 100}}}


# [2]
@pytest.fixture
def spttmpval(scenario):
    """Spatial: Temporal: Value [Original]"""
    return {scenario.loca: {scenario.t0: 100}}


@pytest.fixture
def spttmp_x_val(scenario):
    """Spatial: Temporal: X: Value"""
    return {scenario.loca: {scenario.t0: {_Dummy.X: 100}}}


# [3]
@pytest.fixture
def sptmdeval(scenario):
    """Spatial: Mode: Value [Original]"""
    return {scenario.loca: {X(0): 100}}


@pytest.fixture
def spt_t_mdeval(scenario):
    """Spatial: T: Mode Value"""
    return {scenario.loca: {_Dummy.T: {X(0): 100}}}


@pytest.fixture
def spt_t_mdepval(scenario, x):
    """Spatial: T: Mode Personalized Value"""
    return {scenario.loca: {_Dummy.T: {x: 100}}}


# ---- 3 layer Original ----


@pytest.fixture
def spttmpmdeval(scenario):
    """Spatial: Temporal: Mode: Value [Original]"""
    return {scenario.loca: {scenario.t0: {X(0): 100}}}


@pytest.fixture
def spttmpmdepval(scenario, x):
    """Spatial: Temporal: Mode Personalized: Value [Original]"""
    return {scenario.loca: {scenario.t0: {x: 100}}}


# all the originals need to be tested


def test_make_spatial(
    scenario,
    val,
    n_val,
    mdeval,
    n_mdeval,
    tmpval,
    n_tmpval,
    sptval,
    tmpmdeval,
    n_tmpmdeval,
    spttmpval,
    spttmpmdeval,
):
    """Test to check if spatial values are being made"""
    # Dummy Networks should be inserted for these
    assert scenario.res.make_spatial(val) == n_val
    assert scenario.res.make_spatial(mdeval) == n_mdeval
    assert scenario.res.make_spatial(tmpval) == n_tmpval
    assert scenario.res.make_spatial(sptval) == sptval  # left alone
    assert scenario.res.make_spatial(tmpmdeval) == n_tmpmdeval
    assert scenario.res.make_spatial(spttmpval) == spttmpval  # left alone
    assert scenario.res.make_spatial(spttmpmdeval) == spttmpmdeval  # left alone


# only values with spatial or inserted N can be inputed to test_make_temporal
# look at the rhs of test_make_spatial


def test_make_temporal(
    scenario,
    n_val,
    n_t_val,
    n_mdeval,
    n_t_mdeval,
    n_tmpval,
    sptval,
    spt_t_val,
    spttmpval,
    spttmpmdeval,
):
    """Test to check if spatiotemporal values are being made"""
    assert scenario.res.make_temporal(n_val) == n_t_val
    assert scenario.res.make_temporal(n_mdeval) == n_t_mdeval
    assert scenario.res.make_temporal(n_tmpval) == n_tmpval
    assert scenario.res.make_temporal(sptval) == spt_t_val
    assert scenario.res.make_temporal(spttmpval) == spttmpval  # left alone
    assert scenario.res.make_temporal(spttmpmdeval) == spttmpmdeval  # left alone


# only values with spatial temporal or inserted N and T can be inputed to test_make_modes
# look at the rhs of test_make_temporal


def test_make_modes(
    scenario,
    n_t_val,
    n_t_x_val,
    n_t_mdeval,
    n_t_mdepval,
    n_tmpval,
    n_tmp_x_val,
    spt_t_val,
    spt_t_x_val,
    spttmpval,
    spttmp_x_val,
    spttmpmdeval,
    spttmpmdepval,
):
    """Test to check if spatial temporal mode values are being made"""
    attr = 'attr'
    assert scenario.res.make_modes(n_t_val, attr=attr) == n_t_x_val
    assert scenario.res.make_modes(n_t_mdeval, attr=attr) == n_t_mdepval  # left alone
    assert scenario.res.make_modes(n_tmpval, attr=attr) == n_tmp_x_val
    assert scenario.res.make_modes(spt_t_val, attr=attr) == spt_t_x_val
    assert scenario.res.make_modes(spttmpval, attr=attr) == spttmp_x_val
    assert (
        scenario.res.make_modes(spttmpmdeval, attr=attr) == spttmpmdepval
    )  # left alone
