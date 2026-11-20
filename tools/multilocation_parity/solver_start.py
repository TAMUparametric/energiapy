"""Exact solver reductions justified by a checked feasible annual design."""

import numpy as np

from .inputs import SOURCES


def store_profile(x, index, kind, site_component, values):
    """Assign an hourly physical profile using semantic column identities."""
    site, component = site_component
    x[[index[kind, site, component, t] for t in range(len(values))]] = values


def renewable_site(index, x, data, total, site):
    """Supply one site's share of the feasible renewable and electrolysis design."""
    for plant, resource in [("PV", "Solar"), ("WF", "Wind")]:
        factor = data[f"{site}_{plant}"]
        activity = data["demand"] / 0.38 * factor / total
        store_profile(x, index, "activity", (site, plant), activity)
        store_profile(x, index, "purchase", (site, resource), activity)
        capacity = np.max(
            np.divide(
                activity,
                factor,
                out=np.zeros(len(data["demand"])),
                where=factor > 0,
            ),
        )
        x[index["capacity", site, plant, -1]] = capacity
    awe = data["demand"] / 0.38 * (data[f"{site}_PV"] + data[f"{site}_WF"]) / total
    store_profile(x, index, "activity", (site, "AWE"), awe)
    store_profile(x, index, "purchase", (site, "H2O"), 0.1753 * awe)
    store_profile(x, index, "rail", (site, "H2"), 0.019 * awe)
    x[index["capacity", site, "AWE", -1]] = max(awe)
    x[index["rail_capacity", site, "H2", -1]] = max(awe) * 0.019


def feasible_budget(reference, data):
    """
    Build a storage-free renewable/AWE witness and verify every source row.

    All cost coefficients are nonnegative. Its cost bounds every paid capacity
    at an optimum; these are incumbent-derived bounds, not fitted archive values.
    """
    index = {key: j for j, key in enumerate(reference.keys)}
    x = np.zeros(len(index))
    total = sum(data[f"{site}_{plant}"] for site in SOURCES for plant in ("PV", "WF"))
    if np.any(total <= 0):
        message = (
            "The renewable-only starting design requires positive combined availability"
        )
        raise ValueError(message)

    for site in SOURCES:
        renewable_site(index, x, data, total, site)
    store_profile(x, index, "activity", ("NY", "H2FC"), data["demand"])
    store_profile(x, index, "release", ("NY", "Power"), data["demand"])
    x[index["capacity", "NY", "H2FC", -1]] = max(data["demand"])
    rows = reference.matrix @ x
    violation = max(
        0,
        np.max(reference.lower - rows),
        np.max(rows - reference.upper),
        np.max(reference.col_lower - x),
        np.max(x - reference.col_upper),
    )
    tolerance = 1e-8
    if violation > tolerance or np.any(reference.cost < 0):
        message = "Invalid feasible cost bound"
        raise AssertionError(message)
    return float(reference.cost @ x) * 1.01


def capacity_bound(model, matrix, column, key):
    """Find the tightest original one-variable upper-bound row."""
    candidates = [
        i
        for i in model.matrix[:, column].nonzero()[0]
        if matrix.indptr[i + 1] - matrix.indptr[i] == 1
        and matrix[i, column] == 1
        and np.isfinite(model.upper[i])
    ]
    if not candidates:
        message = f"No original bound for free capacity {key}"
        raise ValueError(message)
    return min(candidates, key=lambda i: model.upper[i])


def reduce_capacities(highs, model, budget):
    """
    Bound paid capacities by a feasible cost, and maximize free capacities.

    The latter are monotonically beneficial upper limits. Remember original
    bound rows so reduced costs can be lifted back into their row multipliers.
    """
    matrix = model.matrix.tocsr()
    changes = {}
    for j, key in enumerate(model.keys):
        if key[-1] != -1 or key[0] not in (
            "capacity",
            "store_capacity",
            "rail_capacity",
        ):
            continue
        if model.cost[j] > 0:
            highs.changeColBounds(
                j,
                model.col_lower[j],
                min(model.col_upper[j], budget / model.cost[j]),
            )
            continue
        maximum = model.col_upper[j]
        if not np.isfinite(maximum):
            row = capacity_bound(model, matrix, j, key)
            maximum = model.upper[row]
            changes[j] = row
        highs.changeColBounds(j, maximum, maximum)
    return changes
