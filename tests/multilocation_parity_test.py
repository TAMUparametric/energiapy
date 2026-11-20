"""The annual exporter must preserve the direct Energia model's equations."""

import numpy as np
import pytest

from tools.multilocation_parity.assembly import assemble, template
from tools.multilocation_parity.inputs import load_inputs
from tools.multilocation_parity.linear import independent


def canonical_rows(model):
    """Compare equations by semantic column identities, ignoring row order."""
    matrix = model.matrix.tocsr()
    return {
        (
            tuple(
                sorted(
                    (model.keys[j], round(float(v), 11))
                    for j, v in zip(
                        matrix.indices[matrix.indptr[i] : matrix.indptr[i + 1]],
                        matrix.data[matrix.indptr[i] : matrix.indptr[i + 1]],
                    )
                    if abs(v) > 1e-12
                )
            ),
            round(float(model.lower[i]), 11),
            round(float(model.upper[i]), 11),
        )
        for i in range(matrix.shape[0])
    }


@pytest.mark.parametrize("hours", [6, 24, 48])
def test_block_export_equals_direct_chronological_model(hours):
    data = {k: v[:hours] for k, v in load_inputs().items()}
    direct, _, _ = template(data)
    blocks = assemble(data)
    assert len(set(direct.keys)) == len(direct.keys)
    assert set(direct.keys) == set(blocks.keys)
    assert canonical_rows(direct) == canonical_rows(blocks)
    order = {key: j for j, key in enumerate(blocks.keys)}
    indices = [order[key] for key in direct.keys]
    np.testing.assert_allclose(direct.cost, blocks.cost[indices], rtol=0, atol=1e-9)
    np.testing.assert_array_equal(direct.col_lower, blocks.col_lower[indices])
    np.testing.assert_array_equal(direct.col_upper, blocks.col_upper[indices])


@pytest.mark.parametrize("demand", [True, False])
def test_short_window_matches_independent_balance_equations(demand):
    data = {k: v[:6] for k, v in load_inputs().items()}
    blocks = assemble(data, demand=demand)
    source = independent(data, demand=demand)
    x, actual = blocks.solve()
    _, expected = source.solve()
    assert actual["objective"] == pytest.approx(expected["objective"], rel=0, abs=1e-5)
    index = {key: j for j, key in enumerate(blocks.keys)}
    projected = x[[index[key] for key in source.keys]]
    rows = source.matrix @ projected
    assert max(0, np.max(source.lower - rows), np.max(rows - source.upper)) < 1e-6


def test_capacity_reductions_certify_the_original_energia_matrix():
    from tools.multilocation_parity.__main__ import check_metrics, project
    from tools.multilocation_parity.solver_start import feasible_budget

    data = {key: value[:48] for key, value in load_inputs().items()}
    reference = independent(data)
    budget = feasible_budget(reference, data)
    energia = assemble(data)
    x, metrics = energia.solve(objective_budget=budget)
    check_metrics(metrics)
    _, expected = reference.solve()
    assert metrics["objective"] == pytest.approx(expected["objective"], rel=0, abs=1e-5)
    project(energia, x, reference)
