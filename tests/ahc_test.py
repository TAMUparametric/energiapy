"""Behavioral checks for chronology-constrained representative periods."""

import numpy as np
import pytest

from energia.surrogate.aggregation import ahc


def test_known_clusters_and_mapping():
    demand = np.array([10, 11, 12, 11, 20, 21, 22, 21])
    availability = [0.2, 0.3, 0.4, 0.3, 0.6, 0.7, 0.8, 0.7]
    result = ahc(demand, availability, periods=2, selection="nearest_centroid")
    np.testing.assert_array_equal(result.labels, [0, 0, 0, 0, 1, 1, 1, 1])
    np.testing.assert_array_equal(result.representative_indices, [1, 5])
    np.testing.assert_array_equal(result.weights, [4, 4])
    np.testing.assert_array_equal(result.reconstruct()[:, 0], [11] * 4 + [21] * 4)
    np.testing.assert_array_equal(demand, [10, 11, 12, 11, 20, 21, 22, 21])


def test_profile_reshape_and_identity():
    result = ahc(np.arange(12), np.arange(12) * 2, periods=4, period_length=3,
                 selection="nearest_centroid")
    assert result.representatives.shape == (4, 3, 2)
    np.testing.assert_array_equal(result.reconstruct()[:, 0], np.arange(12))
    np.testing.assert_array_equal(result.weights, np.ones(4))
    assert result.inertia == result.reconstruction_error == 0


def test_independent_parents_and_errors():
    # Each parent has standardized values [-1, 1]; earliest wins the tie.
    result = ahc([0, 2, 100, 104], periods=1, parent_length=2)
    np.testing.assert_array_equal(result.representative_indices, [0, 2])
    np.testing.assert_array_equal(result.labels, [0, 0, 1, 1])
    np.testing.assert_array_equal(result.weights, [2, 2])
    assert result.inertia == pytest.approx(4)
    assert result.reconstruction_error == pytest.approx(8)


def test_constant_and_single_period():
    result = ahc([5, 5, 5, 5], periods=1)
    np.testing.assert_array_equal(result.representative_indices, [0])
    assert result.weights[0] == 4
    assert result.inertia == result.reconstruction_error == 0
    single = ahc([5], periods=1)
    assert single.representative_indices[0] == 0
    assert single.weights[0] == 1


def test_contiguity_and_membership():
    # Similar observations separated in time cannot form disconnected clusters.
    values = [0, 100, 0, 100, 0, 100, 0, 100]
    result = ahc(values, periods=3, selection="nearest_centroid")
    for cluster, representative in enumerate(result.representative_indices):
        members = np.flatnonzero(result.labels == cluster)
        assert representative in members
        assert np.all(np.diff(members) == 1)
        assert result.weights[cluster] == len(members)
    assert result.weights.sum() == len(values)
    assert np.all(np.diff(result.representative_indices) > 0)


@pytest.mark.parametrize("parents", [1, 2])
def test_legacy_selection_and_corrected_errors(parents):
    # Frozen output of the unchanged 0604a26e historical function: it selects
    # day 2 for BOTH clusters, including its out-of-cluster lookup behavior.
    block = np.array([10, 11, 12, 11, 20, 21, 22, 21])
    values = np.concatenate([block + 100 * p for p in range(parents)])
    legacy = ahc(values, periods=2, parent_length=8)
    explicit_legacy = ahc(values, periods=2, parent_length=8, selection="legacy")
    np.testing.assert_array_equal(legacy.representative_indices,
                                  explicit_legacy.representative_indices)
    current = ahc(values, periods=2, parent_length=8, selection="nearest_centroid")
    np.testing.assert_array_equal(
        legacy.representative_indices,
        [index for p in range(parents) for index in (8 * p + 2, 8 * p + 2)],
    )
    np.testing.assert_array_equal(legacy.labels, current.labels)
    np.testing.assert_array_equal(legacy.weights, [4] * (2 * parents))
    np.testing.assert_array_equal(
        legacy.reconstruct()[:, 0],
        np.concatenate([np.full(8, 12 + 100 * p) for p in range(parents)]),
    )
    assert legacy.selection == "legacy"
    assert current.selection == "nearest_centroid"
    assert legacy.inertia == pytest.approx(parents * 4 / 25.5)
    assert legacy.inertia == pytest.approx(current.inertia)
    assert legacy.reconstruction_error == pytest.approx(parents * 332 / 25.5)


def test_legacy_single_cluster_fallback():
    # Historical NearestCentroid requires multiple classes; the documented
    # extension uses nearest-member selection for one cluster.
    result = ahc([0, 1, 2], periods=1, selection="legacy")
    np.testing.assert_array_equal(result.representative_indices, [1])
    single = ahc([5], periods=1, selection="legacy")
    np.testing.assert_array_equal(single.representative_indices, [0])
    assert single.reconstruction_error == 0


@pytest.mark.parametrize("data, kwargs", [
    ([], {"periods": 1}),
    ([[]], {"periods": 1}),
    ([[1, 2], [1]], {"periods": 1}),
    ([[float('nan')]], {"periods": 1}),
    ([[float('inf')]], {"periods": 1}),
    ([[[1, 2]]], {"periods": 1}),
    ([[1, 2]], {"periods": 0}),
    ([[1, 2]], {"periods": True}),
    ([[1, 2]], {"periods": 1.5}),
    ([[1, 2]], {"periods": 3}),
    ([[1, 2, 3]], {"periods": 1, "period_length": 2}),
    ([[1, 2]], {"periods": 1, "period_length": 0}),
    ([[1, 2, 3]], {"periods": 1, "parent_length": 2}),
    ([[1, 2]], {"periods": 1, "parent_length": 0}),
    ([[1, 2]], {"periods": 1, "selection": "unknown"}),
])
def test_invalid_input(data, kwargs):
    with pytest.raises(ValueError):
        ahc(*data, **kwargs)
