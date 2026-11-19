import pandas as pd
import pytest

from energia.utils.math import normalize
from energia.utils.scaling import scaling


@pytest.mark.parametrize(
    "method, expected",
    [
        ("max", [(0.05, 0.06), (0.01, 1)]),
        ("min_max", [(4 / 99, 5 / 99), (0, 1)]),
    ],
)
def test_interval_endpoints_share_one_scale(method, expected):
    assert normalize([(5, 6), (1, 100)], method) == expected


@pytest.mark.parametrize(
    "values, method, expected",
    [
        ([0, 0], "max", [0, 0]),
        ([5, 5], "max", [1, 1]),
        ([5, 5], "min_max", [0, 0]),
        ([(5, 5), (5, 5)], "min_max", [(0, 0), (0, 0)]),
        ([(-8, -4), (-4, -2)], "max", [(2, 4), (1, 2)]),
        ([-4, 0], "max", [-1, 0]),
        ([[2, 4], [0, 0]], "max", [[0.5, 1], [0, 0]]),
        ([], "min_max", []),
    ],
)
def test_normalize_profiles(values, method, expected):
    assert normalize(values, method) == expected


def test_normalize_rejects_reversed_bounds_and_unknown_method():
    with pytest.raises(ValueError, match="lower bound"):
        normalize([(5, 2)])
    with pytest.raises(ValueError, match="unknown"):
        normalize([1, 2], "unknown")


@pytest.mark.parametrize(
    "method, expected",
    [
        ("max", [[0.5, 1.0], [1.0, 1.0]]),
        ("minmax", [[0.0, 0.0], [1.0, 0.0]]),
        ("standard", [[-1.0, 0.0], [1.0, 0.0]]),
    ],
)
def test_scaling_preserves_axes_and_scales_each_column(method, expected):
    dates = pd.date_range("2026-01-01", periods=2, name="date")
    columns = pd.Index(["power", "constant"], name="series")
    frame = pd.DataFrame([[2, 5], [4, 5]], index=dates, columns=columns)
    original = frame.copy()
    result = scaling(frame, method)
    pd.testing.assert_frame_equal(result, pd.DataFrame(expected, index=dates, columns=columns))
    pd.testing.assert_frame_equal(frame, original)


def test_max_scaling_handles_zero_maximum_per_column():
    frame = pd.DataFrame({"zero": [0, 0], "negative": [-4, 0]})
    expected = pd.DataFrame({"zero": [0.0, 0.0], "negative": [-1.0, 0.0]})
    pd.testing.assert_frame_equal(scaling(frame, "max"), expected)


def test_scaling_preserves_missing_values_and_mixed_column_labels():
    frame = pd.DataFrame({1: pd.Series([2, pd.NA], dtype="Int64"), "wind": [4, 6]})
    expected = pd.DataFrame({1: [0.0, float("nan")], "wind": [0.0, 1.0]})
    pd.testing.assert_frame_equal(scaling(frame, "minmax"), expected)


def test_scaling_rejects_unknown_method():
    with pytest.raises(ValueError, match="unknown"):
        scaling(pd.DataFrame({"power": [1, 2]}), "unknown")
