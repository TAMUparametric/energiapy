"""
Chronology-constrained aggregation of aligned time series.

Port of energiapy 1.0.7's aggregation/ahc.py (0604a26e): standardize
profiles, apply adjacent-period Ward clustering, and select observed profiles.
"""

# PORTED from v1.0.7 by OpenAI Codex (GPT-6)
from dataclasses import dataclass
from numbers import Integral
from typing import Literal

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray
from scipy.sparse import diags
from sklearn.cluster import AgglomerativeClustering
from sklearn.neighbors import NearestCentroid
from sklearn.preprocessing import StandardScaler


# Authored by OpenAI Codex (GPT-6).
@dataclass
class AHCResult:
    """
    Representative profiles and their mapping to the original periods.

    ``labels`` maps every original period to a row in ``representatives``.
    ``representative_indices`` identifies those periods in the original input.
    ``weights`` counts represented periods, not timesteps or elapsed hours.
    Representatives have shape (clusters, period_length, features) in original
    units. Nearest-centroid selection orders clusters chronologically. Legacy selection
    orders by selected period and can select outside a cluster or repeat a
    representative, preserving historical behavior. Errors are sums of squared
    distances in standardized profile
    space: to centroids (``inertia``) and to selected profiles
    (``reconstruction_error``). Each parent is standardized independently.
    """

    labels: NDArray[np.int64]
    representative_indices: NDArray[np.int64]
    weights: NDArray[np.int64]
    representatives: NDArray[np.float64]
    inertia: float
    reconstruction_error: float
    selection: str = "legacy"

    def reconstruct(self) -> NDArray[np.float64]:
        """Expand representatives to (original timesteps, features)."""
        return self.representatives[self.labels].reshape(
            -1, self.representatives.shape[-1],
        )


# Authored by OpenAI Codex (GPT-6).
def _positive_integer(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        raise ValueError(f"{name} must be a positive integer")  # noqa: TRY003 - Keep actionable input-validation messages.
    return int(value)


# PORTED from v1.0.7 by OpenAI Codex (GPT-6)
def _legacy_selection(scaled, assignments):
    """
    Reproduce 0604a26e's centroid labeling and global distance lookup.

    Keep pandas ordering and Python distance summation as in the historical
    code. This compatibility policy deliberately retains its selection quirks;
    error metrics are still calculated from the actual cluster memberships.
    """
    frame = pd.DataFrame(scaled)
    centroids = NearestCentroid().fit(scaled, assignments).centroids_
    frame["cluster_no"] = assignments
    distances = []
    for centroid, label in zip(centroids, frame["cluster_no"].unique()):
        for point in scaled[assignments == label]:
            distances.append(sum((a - b) ** 2 for a, b in zip(point, centroid)))
    frame["ED"] = distances
    selected = pd.DataFrame({
        "label": frame["cluster_no"].value_counts().index.values,
    })
    selected["representative"] = [
        int(frame.index[frame["ED"] == frame.loc[
            frame["cluster_no"] == label, "ED",
        ].min()][0])
        for label in selected["label"]
    ]
    selected = selected.sort_values("representative")
    return [
        (np.flatnonzero(assignments == label), int(representative))
        for label, representative in selected.itertuples(index=False, name=None)
    ]


# Authored by OpenAI Codex (GPT-6).
def _validated_series(data):
    """Convert aligned input series and reject empty or nonfinite values."""
    if not data:
        raise ValueError("provide at least one time series")  # noqa: TRY003 - Keep actionable input-validation messages.
    series = [np.asarray(values, dtype=float) for values in data]
    if any(values.ndim != 1 or not values.size for values in series):
        raise ValueError("each time series must be nonempty and one-dimensional")  # noqa: TRY003 - Keep actionable input-validation messages.
    if any(len(values) != len(series[0]) for values in series):
        raise ValueError("time series must have equal lengths")  # noqa: TRY003 - Keep actionable input-validation messages.
    if any(not np.isfinite(values).all() for values in series):
        raise ValueError("time series must contain only finite values")  # noqa: TRY003 - Keep actionable input-validation messages.
    return series


# Authored by OpenAI Codex (GPT-6).
def _prepare_profiles(data, periods, period_length, parent_length, selection):
    """Validate aggregation dimensions and build complete parent profiles."""
    periods = _positive_integer(periods, "periods")
    period_length = _positive_integer(period_length, "period_length")
    if selection not in ("nearest_centroid", "legacy"):
        raise ValueError("selection must be 'nearest_centroid' or 'legacy'")  # noqa: TRY003 - Keep actionable input-validation messages.
    series = _validated_series(data)
    if len(series[0]) % period_length:
        raise ValueError("time series must contain complete periods")  # noqa: TRY003 - Keep actionable input-validation messages.
    profiles = np.column_stack(series).reshape(-1, period_length, len(series))
    count = len(profiles)
    parent_length = count if parent_length is None else _positive_integer(
        parent_length, "parent_length",
    )
    if count % parent_length:
        raise ValueError("time series must contain complete parent groups")  # noqa: TRY003 - Keep actionable input-validation messages.
    if periods > parent_length:
        raise ValueError("periods cannot exceed the original periods per parent")  # noqa: TRY003 - Keep actionable input-validation messages.
    return profiles, periods, parent_length


# PORTED from v1.0.7 by OpenAI Codex (GPT-6)
def _cluster_parent(block, periods, selection):
    """Standardize one parent and cluster with linear temporal adjacency."""
    parent_length = len(block)
    if selection == "legacy":
        # Match historical feature-major arithmetic order as well as values.
        block = block.transpose(0, 2, 1)
    scaled = StandardScaler().fit_transform(block.reshape(parent_length, -1))
    if periods == 1:
        assignments = np.zeros(parent_length, dtype=np.int64)
    elif periods == parent_length and selection != "legacy":
        assignments = np.arange(parent_length)
    else:
        connectivity = diags(
            [np.ones(parent_length - 1), np.ones(parent_length - 1)],
            offsets=[-1, 1], shape=(parent_length, parent_length), format="csr",
        )
        assignments = AgglomerativeClustering(
            n_clusters=periods, linkage="ward", connectivity=connectivity,
            compute_full_tree=True if selection == "legacy" else "auto",
        ).fit_predict(scaled)
    return scaled, assignments


# Authored by OpenAI Codex (GPT-6).
def _cluster_choices(scaled, assignments, periods, selection):
    """Order clusters and supply historical representatives when requested."""
    if selection == "legacy" and periods > 1:
        return _legacy_selection(scaled, assignments)
    # Cluster ids from sklearn are arbitrary; order by first original member.
    clusters = [np.flatnonzero(assignments == c) for c in np.unique(assignments)]
    clusters.sort(key=lambda members: members[0])
    return [(members, None) for members in clusters]


# Authored by OpenAI Codex (GPT-6).
def _representative_statistics(scaled, members, representative):
    """Select the earliest nearest member if needed and compute cluster errors."""
    centroid = scaled[members].mean(axis=0)
    distances = ((scaled[members] - centroid) ** 2).sum(axis=1)
    if representative is None:
        # Members are chronological, so the first numerical tie is the earliest.
        tied = np.flatnonzero(np.isclose(
            distances, distances.min(), rtol=1e-12, atol=1e-12,
        ))
        representative = members[tied[0]]
    inertia = float(distances.sum())
    reconstruction_error = float(
        ((scaled[members] - scaled[representative]) ** 2).sum(),
    )
    return representative, inertia, reconstruction_error


# PORTED from v1.0.7 by OpenAI Codex (GPT-6)
def ahc(
    *data: ArrayLike,
    periods: int,
    period_length: int = 1,
    parent_length: int | None = None,
    selection: Literal["nearest_centroid", "legacy"] = "legacy",
) -> AHCResult:
    """
    Cluster aligned one-dimensional series into representative periods.

    :param data: One or more finite numeric series with equal lengths. Features
        retain their argument order; inputs are aligned positionally.
    :param periods: Number of representative periods **per parent group**.
    :param period_length: Timesteps in each original period, e.g. 24 for days
        sampled hourly. All periods must be complete and equally long.
    :param parent_length: Original periods per independent parent group, e.g.
        365 days per year. Defaults to all periods in one group. All parent
        groups must be complete; clustering never crosses their boundaries.
    :param selection: Defaults to ``legacy``. ``nearest_centroid`` selects the nearest cluster member,
        breaking numerical ties with the earliest period. ``legacy`` reproduces
        historical centroid-label association and representative lookup, including
        possible repeated or out-of-cluster representatives. Both policies retain
        the corrected error metrics. For a single cluster, where the historical
        NearestCentroid call cannot run, use nearest-member selection.

    Each feature/timestep column is standardized across periods within its
    parent group, matching the legacy profile scaling. Ward linkage uses a
    linear adjacency graph (no wraparound). Legacy representative selection is
    the default; nearest-centroid selection is an explicit alternative.
    Inputs are not modified. This function does not construct a reduced model.
    """
    profiles, periods, parent_length = _prepare_profiles(
        data, periods, period_length, parent_length, selection,
    )
    count = len(profiles)
    labels = np.empty(count, dtype=np.int64)
    selected, weights = [], []
    inertia = reconstruction_error = 0.0
    for start in range(0, count, parent_length):
        # Scaling and clustering stay within each parent's chronological boundary.
        scaled, assignments = _cluster_parent(
            profiles[start : start + parent_length], periods, selection,
        )
        choices = _cluster_choices(scaled, assignments, periods, selection)
        for members, preset_representative in choices:
            representative, cluster_inertia, cluster_error = _representative_statistics(
                scaled, members, preset_representative,
            )
            # Translate parent-local positions into the full input's mapping.
            labels[start + members] = len(selected)
            selected.append(start + representative)
            weights.append(len(members))
            inertia += cluster_inertia
            reconstruction_error += cluster_error

    indices = np.asarray(selected, dtype=np.int64)
    return AHCResult(
        labels=labels, representative_indices=indices,
        weights=np.asarray(weights, dtype=np.int64),
        representatives=profiles[indices].copy(),
        inertia=inertia, reconstruction_error=reconstruction_error,
        selection=selection,
    )
