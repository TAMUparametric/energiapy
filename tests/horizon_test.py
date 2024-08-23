"""Horizon Test
"""

import pytest
from pandas import DataFrame
from .test_fixtures import (
    horizon_singlescale,
    horizon_singlescale_scale_0,
    horizon_singlescale_scale_1,
    horizon_multiscale,
    horizon_multiscale_scale_0,
    horizon_multiscale_scale_1,
    horizon_multiscale_scale_2,
    horizon_multiscale_un,
    horizon_multiscale_un_scale_0,
    horizon_multiscale_un_scale_1,
    horizon_multiscale_un_scale_2,
    horizon_multiscale_nmd,
    horizon_multiscale_nmd_scale_0,
    horizon_multiscale_nmd_scale_1,
    horizon_multiscale_nmd_scale_2,
    scenario_bare,
)

a = DataFrame({'a': list(range(2))})
b = DataFrame({'b': list(range(8))})


def test_horizon_singlescale(
    horizon_singlescale, horizon_singlescale_scale_0, horizon_singlescale_scale_1
):
    """Single scale Horizon"""
    assert hasattr(horizon_singlescale, '_model') is True
    assert horizon_singlescale.nested is True
    assert horizon_singlescale.is_nested is True
    assert horizon_singlescale.is_multiscale is False
    assert horizon_singlescale.name_scales == ['t0', 't1']
    assert getattr(horizon_singlescale, '_discretization_list') == [1, 4]
    assert horizon_singlescale.n_scales == 2
    assert horizon_singlescale.n_indices == [1, 4]
    assert horizon_singlescale.indices == {
        horizon_singlescale_scale_0: [(0,)],
        horizon_singlescale_scale_1: [(0, 0), (0, 1), (0, 2), (0, 3)],
    }


def test_horizon_multiscale(
    horizon_multiscale,
    horizon_multiscale_scale_0,
    horizon_multiscale_scale_1,
    horizon_multiscale_scale_2,
):
    """Multiscale Horizon with 2 and 4 discertizations"""
    assert hasattr(horizon_multiscale, '_model') is True
    assert horizon_multiscale.nested is True
    assert horizon_multiscale.is_nested is True
    assert horizon_multiscale.is_multiscale is True
    assert horizon_multiscale.name_scales == ['t0', 't1', 't2']
    assert getattr(horizon_multiscale, '_discretization_list') == [1, 2, 4]
    assert horizon_multiscale.n_scales == 3
    assert horizon_multiscale.n_indices == [1, 2, 8]
    assert horizon_multiscale.indices == {
        horizon_multiscale_scale_0: [(0,)],
        horizon_multiscale_scale_1: [(0, 0), (0, 1)],
        horizon_multiscale_scale_2: [
            (0, 0, 0),
            (0, 0, 1),
            (0, 0, 2),
            (0, 0, 3),
            (0, 1, 0),
            (0, 1, 1),
            (0, 1, 2),
            (0, 1, 3),
        ],
    }
    assert horizon_multiscale.match_scale(a) == horizon_multiscale_scale_1
    assert horizon_multiscale.match_scale(b) == horizon_multiscale_scale_2


def test_horizon_multiscale_un(
    horizon_multiscale_un,
    horizon_multiscale_un_scale_0,
    horizon_multiscale_un_scale_1,
    horizon_multiscale_un_scale_2,
):
    """Not Nested Multiscale Horizon with 2 and 4 discertizations"""
    assert hasattr(horizon_multiscale_un, '_model') is True
    assert horizon_multiscale_un.nested is False
    assert horizon_multiscale_un.is_nested is False
    assert horizon_multiscale_un.is_multiscale is True
    assert horizon_multiscale_un.name_scales == ['t0', 't1', 't2']
    assert getattr(horizon_multiscale_un, '_discretization_list') == [1, 2, 8]
    assert horizon_multiscale_un.n_scales == 3
    assert horizon_multiscale_un.n_indices == [1, 2, 8]
    assert horizon_multiscale_un.indices == {
        horizon_multiscale_un_scale_0: [(0, 0)],
        horizon_multiscale_un_scale_1: [(0, 0), (0, 4)],
        horizon_multiscale_un_scale_2: [
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (0, 6),
            (0, 7),
        ],
    }
    assert horizon_multiscale_un.match_scale(a) == horizon_multiscale_un_scale_1
    assert horizon_multiscale_un.match_scale(b) == horizon_multiscale_un_scale_2


def test_horizon_multiscale_nmd(
    horizon_multiscale_nmd,
    horizon_multiscale_nmd_scale_0,
    horizon_multiscale_nmd_scale_1,
    horizon_multiscale_nmd_scale_2,
):
    """Multiscale Horizon with 2 and 4 discertizations"""
    assert hasattr(horizon_multiscale_nmd, '_model') is True
    assert horizon_multiscale_nmd.nested is True
    assert horizon_multiscale_nmd.is_nested is True
    assert horizon_multiscale_nmd.is_multiscale is True
    assert horizon_multiscale_nmd.name_scales == ['ph', 'a', 'b']
    assert getattr(horizon_multiscale_nmd, '_discretization_list') == [1, 2, 4]
    assert horizon_multiscale_nmd.n_scales == 3
    assert horizon_multiscale_nmd.n_indices == [1, 2, 8]
    assert horizon_multiscale_nmd.indices == {
        horizon_multiscale_nmd_scale_0: [(0,)],
        horizon_multiscale_nmd_scale_1: [(0, 0), (0, 1)],
        horizon_multiscale_nmd_scale_2: [
            (0, 0, 0),
            (0, 0, 1),
            (0, 0, 2),
            (0, 0, 3),
            (0, 1, 0),
            (0, 1, 1),
            (0, 1, 2),
            (0, 1, 3),
        ],
    }
    assert horizon_multiscale_nmd.match_scale(a) == horizon_multiscale_nmd_scale_1
    assert horizon_multiscale_nmd.match_scale(b) == horizon_multiscale_nmd_scale_2
