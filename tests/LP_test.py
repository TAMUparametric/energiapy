import pytest
from gurobipy import GRB

# from energia import Currency, Model, Periods, Process, Resource

from energia.library.examples.energy import (
    scheduling,
    scheduling_w_attrs,
    scheduling_wo_time,
)


@pytest.fixture
def m(request):
    if request.param == "attrs":
        _m = scheduling_w_attrs()
    elif request.param == "plain":
        _m = scheduling()
    elif request.param == "wo_time":
        _m = scheduling_wo_time()
    else:
        raise ValueError(f"Unknown model type: {request.param}")
    _m.usd.spend.opt()
    return _m


@pytest.mark.parametrize("m", ["attrs", "plain", "wo_time"], indirect=True)
def test_small_1L_1T_1O_LP(m):
    assert m.program.formulation.Status == GRB.OPTIMAL
    assert m.program.formulation.ObjVal == pytest.approx(1_081_000)
    assert len(m.periods) == 2
    assert m.locations == [m.network]
    assert m.resources == [m.wind, m.power]
    assert m.currencies == [m.usd]
    assert m.processes == [m.wf]
    assert m.consume.output(aslist=True) == pytest.approx([260.0], rel=1e-9)
    assert m.release.output(aslist=True) == pytest.approx(
        [60.0, 70.0, 100.0, 30.0], rel=1e-9
    )
    assert m.operate.output(aslist=True) == pytest.approx(
        [60.0, 70.0, 100.0, 30.0, 260.0], rel=1e-9
    )
    assert m.wf.operate(m.time.densest).output(aslist=True) == pytest.approx(
        [60, 70, 100, 30]
    )
    assert m.wf.operate(m.horizon).output(aslist=True) == pytest.approx([260])
    assert m.spend.output(aslist=True) == pytest.approx(
        [240000.0, 294000.0, 430000.0, 117000.0, 1081000.0], rel=1e-9
    )
    assert m.produce.output(aslist=True) == pytest.approx(
        [60.0, 70.0, 100.0, 30.0], rel=1e-9
    )


@pytest.mark.parametrize("m", ["attrs", "plain"], indirect=True)
def test_attrs(m):
    assert sorted(con.pname for con in m.wind.cons) == [
        "consume_wind_l0_y_ub",
        "expend_wind_l0_y_operate_wf_calc",
        "wind_l0_y_grb",
    ]
    assert not m.wind == m.wf

    assert (m.wind - m.power).balance == {m.wind: 1, m.power: -1}
    assert (-m.power).balance == {m.power: -1}
