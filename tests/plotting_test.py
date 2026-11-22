"""Physical result selection shares Gana's rendering without model mutation."""

import json

import matplotlib as mpl
import numpy as np
import pytest
from gana.plotting import Plot, column
from matplotlib import pyplot as plt

from energia import Location, Model, Periods, Process, Resource, Unit
from energia.library.examples.energy import design_scheduling, scheduling
from energia.plotting import records


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close('all')


@pytest.fixture
def solved():
    m = scheduling()
    m.power.basis = Unit(label='MWh')
    m.usd.basis = Unit(label='USD')
    m.wf.label = 'Wind'
    m.usd.spend.opt()
    return m


def test_native_result_selection_does_not_declare_or_renumber(solved, tmp_path):
    m = solved
    before = tmp_path / 'before.json'
    after = tmp_path / 'after.json'
    m.program.export_solution(before)
    variable = m.program.operate._symbol_storage.owner
    native = (len(variable.states), len(variable.cache))
    domains = [(a, len(a.domains), len(a.indices)) for a in (m.operate, m.spend, m.produce)]
    plot = m.wf.operate(m.q).line()
    assert isinstance(plot, Plot)
    assert plot.data[0].values == (60, 70, 100, 30)
    assert plot.data[0].x == (0, 1, 2, 3)
    assert plot.data[0].unit == 'MWh'
    assert plot.data[0].label == 'Wind operate'
    assert native == (len(variable.states), len(variable.cache))
    assert all((len(a.domains), len(a.indices)) == (d, i) for a, d, i in domains)
    m.program.export_solution(after)
    assert json.loads(before.read_text()) == json.loads(after.read_text())


def test_model_and_sample_composition_have_identical_data_and_geometry(solved):
    m = solved
    a, b = m.wf.operate(m.q), m.power.release(m.q)
    one = m.bar(a, b).render()
    two = (a.bar() + b.bar()).render()
    assert [s.values for s in one.data] == [s.values for s in two.data]
    assert [(p.get_x(), p.get_height()) for p in one.axes[0].patches] == [
        (p.get_x(), p.get_height()) for p in two.axes[0].patches]
    assert one.axes[0].get_ylabel() == 'MWh'
    assert not one.axes[0].spines['top'].get_visible()
    assert one.theme_version == two.theme_version


def test_time_slices_keep_offsets_and_stacking_rejects_misalignment(solved):
    m = solved
    whole = m.wf.operate(m.q).line()
    sliced = m.wf.operate(m.q[1::2]).line()
    assert sliced.data[0].x == (1, 3)
    assert sliced.data[0].values == (70, 30)
    assert m.wf.operate(m.q[-1]).line().data[0].values == (30,)
    assert m.wf.operate(m.q[::-1][1:3]).line().data[0].x == (2, 1)
    (whole + sliced).render()
    with pytest.raises(ValueError, match='coordinate order'):
        m.stacked(m.wf.operate(m.q), m.power.release(m.q[1:])).render()
    with pytest.raises(ValueError, match='no registered result coordinates'):
        m.wf.operate(m.q[:0]).line()


def test_nested_time_coordinates_are_flattened_without_reweighting():
    m = Model()
    m.hour = Periods(weight=7)
    m.day = 3 * m.hour
    m.year = 2 * m.day
    m.plant = Process()
    m.plant.operate(m.hour) == [1, 2, 3, 4, 5, 6]
    m.plant.operate(m.hour).opt()
    plot = m.plant.operate(m.hour).line()
    assert plot.data[0].values == (1, 2, 3, 4, 5, 6)
    assert plot.data[0].x == tuple(range(6))
    assert len(set(plot.data[0].coordinates)) == 6
    assert m.plant.operate(m.hour[2:5]).line().data[0].values == (3, 4, 5)


def test_selected_flow_and_cost_keep_time_before_related_activity(solved):
    m = solved
    flow = m.power.produce(m.q, m.wf.operate).line()
    cost = m.usd.spend(m.q, m.wf.operate).bar()
    assert flow.data[0].values == (60, 70, 100, 30)
    assert flow.data[0].label == 'power produce / Wind'
    assert cost.data[0].values == (240000, 294000, 430000, 117000)
    assert sum(cost.data[0].values) == 1_081_000
    with pytest.raises(ValueError, match='matching units|different or unknown units'):
        m.line(m.wf.operate(m.q), m.usd.spend(m.q, m.wf.operate))
    column(flow, cost, sharex=True).render()


def test_ambiguous_unregistered_unsolved_and_reporting_selections_fail(solved):
    m = solved
    with pytest.raises(ValueError, match='Ambiguous'):
        m.wf.operate.line()
    with pytest.raises(ValueError, match='Ambiguous'):
        m.operate.line()
    with pytest.raises(ValueError, match='reporting binary'):
        m.wf.operate(m.q).x.line()
    with pytest.raises(ValueError, match='lagged'):
        m.wf.operate(-m.q).line()
    m.unused = Process()
    before = len(m.operate.domains)
    with pytest.raises(ValueError, match='No registered'):
        m.unused.operate(m.q).line()
    assert len(m.operate.domains) == before
    other = scheduling()
    with pytest.raises(ValueError, match='No stored solution'):
        other.wf.operate(other.q).line()
    with pytest.raises(ValueError, match='belong to this model'):
        m.line(other.wf.operate(other.q))
    with pytest.raises(TypeError, match='Sample or Aspect'):
        records([1, 2])


def test_two_solutions_remain_detached(solved):
    m = solved
    first = m.wf.operate(m.q).line()
    m.program.minimum = m.program.operate(*m.operate.domains[0].I) >= [80, 90, 100, 80]
    m.opt()
    assert m.wf.operate(m.q).line(n_sol=1).data[0].values == (80, 90, 100, 80)
    assert first.data[0].values == (60, 70, 100, 30)
    assert first.data[0].n_sol == 0
    with pytest.raises(ValueError, match='No stored solution'):
        m.wf.operate(m.q).line(n_sol=10)


def test_locations_remain_separate_without_parent_double_counting():
    m = Model()
    m.q = Periods()
    m.y = 2 * m.q
    m.a, m.b = Location(), Location()
    m.plant = Process()
    m.plant.operate(m.a, m.q) == [2, 4]
    m.plant.operate(m.b, m.q) == [3, 5]
    m.plant.operate(m.a, m.q).opt()
    with pytest.raises(ValueError, match='Ambiguous'):
        m.plant.operate(m.q).line()
    plot = m.stacked(m.plant.operate(m.a, m.q), m.plant.operate(m.b, m.q))
    assert [s.values for s in plot.data] == [(2, 4), (3, 5)]
    assert len(plot.render().axes) == 1


@pytest.mark.parametrize('chart', ['line', 'scatter', 'bar', 'stacked', 'area', 'band', 'errorbar'])
def test_chart_bindings_share_gana_options(solved, chart):
    sample = solved.wf.operate(solved.q)
    options = {'lower': [50, 60, 90, 20], 'upper': [70, 80, 110, 40]} if chart == 'band' else {}
    if chart == 'errorbar':
        options = {'yerr': [1, 2, 3, 4]}
    result = getattr(sample, chart)(**options).render()
    assert result.data[0].values == (60, 70, 100, 30)
    assert len(result.axes) == 1


def test_interval_bounds_use_selected_physical_records(solved):
    m = solved
    band = m.wf.operate(m.q).band(lower=m.power.release(m.q), upper=[70, 80, 110, 40])
    assert band.data[0].lower == (60, 70, 100, 30)
    with pytest.raises(ValueError, match='coordinate order'):
        m.wf.operate(m.q).band(lower=m.power.release(m.q[1:]), upper=[70, 80, 110, 40])


def test_legacy_positional_options_and_immediate_draw(solved, monkeypatch):
    m = solved
    shown = []
    monkeypatch.setattr(plt, 'show', lambda: shown.append(True))
    result = m.wf.operate(m.q).line(9, (3.5, 2.5)).render()
    np.testing.assert_equal(result.figure.get_size_inches(), [3.5, 2.5])
    assert m.draw(m.wf.operate(m.q)).data[0].values == (60, 70, 100, 30)
    assert shown == [True]
    monkeypatch.setattr(m.program, 'draw', lambda **kw: kw)
    m.program.sol_types['mp'].append(9)
    assert m.draw(n_sol=9) == {'n_sol': 9}
    assert m.draw(m.wf.operate(m.q), n_sol=9) == {'n_sol': 9}


def test_manuscript_exports_preserve_dimensions_and_caller_style(solved, tmp_path):
    plot = solved.wf.operate(solved.q).line()
    before = mpl.rcParams.copy()
    for suffix in ('pdf', 'svg', 'png'):
        path = plot.save(tmp_path / f'dispatch.{suffix}', profile='print', fig_size=(3.5, 2.5), dpi=300)
        assert path.stat().st_size > 1000
    assert mpl.rcParams == before
    assert not plt.get_fignums()


def test_storage_inventory_and_capacity_are_not_summed_over_time():
    m = design_scheduling()
    m.usd.spend.opt()
    inventory = m.lii.inventory(m.q).line()
    capacity = m.lii.capacity(m.y).bar()
    assert inventory.data[0].values == tuple(m.lii.inventory(m.q).output(aslist=True))
    assert capacity.data[0].values == tuple(m.lii.capacity(m.y).output(aslist=True))
    column(inventory, capacity).render()


def test_modes_and_missing_columns_keep_distinct_records():
    m = Model()
    m.q = Periods()
    m.y = 2 * m.q
    m.plant, m.unused = Process(), Process()
    modes = m.Modes(size=2, sample=m.plant.operate(m.q))
    selected = m.plant.operate(m.q, modes)
    selected == [1, 2, 3, 4]
    m.unused.operate(m.q) >= 0
    selected.opt()
    plot = selected.line()
    assert [s.values for s in plot.data] == [(1, 3), (2, 4)]
    assert len({s.key for s in plot.data}) == 2
    missing = m.unused.operate(m.q).line()
    assert missing.data[0].values == (None, None)


def test_component_encodings_match_across_operation_and_capacity():
    m = design_scheduling()
    m.usd.spend.opt()
    wind = m.wf.operate(m.q).line()
    capacity = m.wf.capacity(m.y).bar()
    cost = m.usd.spend(m.y, m.wf.operate).bar()
    assert wind.data[0].key == capacity.data[0].key == cost.data[0].key


def test_scatter_can_use_another_selected_quantity(solved):
    m = solved
    result = m.wf.operate(m.q).scatter(x=m.power.release(m.q)).render()
    np.testing.assert_equal(result.axes[0].collections[0].get_offsets(),
                            [[60, 60], [70, 70], [100, 100], [30, 30]])
