import pytest

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


# TODO: "wo_time" not ready yet
@pytest.mark.parametrize("m", ["attrs", "plain"], indirect=True)
def test_small_1L_1T_1O_LP(m):
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
    assert m.spend.output(aslist=True) == pytest.approx(
        [240000.0, 294000.0, 430000.0, 117000.0, 1081000.0], rel=1e-9
    )
    assert m.produce.output(aslist=True) == pytest.approx(
        [60.0, 70.0, 100.0, 30.0], rel=1e-9
    )


@pytest.mark.parametrize("m", ["attrs", "plain"], indirect=True)
def test_attrs(m):
    _cons = m.program.constraint_sets
    m.wind.cons == [_cons[-1], _cons[1], _cons[0]]
    assert not m.wind == m.wf

    c = m.wind - m.power
    c.__dict__ == {
        'resource': None,
        'operation': None,
        'symbol': 'η',
        'aspect': '',
        'add': '',
        'sub': '',
        'balance': {m.wind: 1, m.power: -1},
        'hold': None,
        'expect': None,
        'lag': None,
        'attr_name': '',
        'use_max_time': False,
    }

    d = -m.power
    d.__dict__ == {
        'resource': None,
        'operation': None,
        'symbol': 'η',
        'aspect': '',
        'add': '',
        'sub': '',
        'balance': {m.power: -1},
        'hold': None,
        'expect': None,
        'lag': None,
        'attr_name': '',
        'use_max_time': False,
    }
