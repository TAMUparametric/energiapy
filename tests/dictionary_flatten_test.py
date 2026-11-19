"""Regression tests for flattening nested dictionary paths."""

from energia.utils.dictionary import flatten


def test_flatten_preserves_prefix_and_nested_keys():
    values = {"site": {("power", "heat"): 5, "gas": 2}, "empty": {}}
    assert flatten(values, key=("model",)) == {
        ("model", "site", ("power", "heat")): 5,
        ("model", "site", "gas"): 2,
    }
