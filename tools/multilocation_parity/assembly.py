"""Expand an exported two-hour Energia model into a chronological annual LP.

Only known hourly input coefficients change. Investment columns are shared,
charged once, and all five inventories link across adjacent blocks.
"""

import numpy as np
from gana.backends.highs import build as export
from scipy.sparse import coo_matrix, csc_matrix

from .energia_model import build
from .inputs import SOURCES
from .linear import Linear

TEMPLATE_DEMAND = 40.0


def auxiliary_key(variable):
    indices = [str(i) for i in variable.index]
    hour = next((int(i[5:-1]) for i in indices if i.startswith("hour[")), -1)
    identity = "|".join(
        [variable.name.split("[")[0]]
        + [i for i in indices if not i.startswith(("hour[", "year["))],
    )
    return ("aux", identity, "", hour)


def variable_keys(lp, program, refs):
    """Identify physical and shared columns without depending on column order."""
    cols = {name: j for j, name in enumerate(lp.col_names_)}
    variables = {cols[v.mps()]: v for v in program.variables if v.mps() in cols}
    semantic = physical_keys(cols, refs)
    keys = [semantic.get(j, auxiliary_key(variables[j])) for j in range(lp.num_col_)]
    global_cols = [
        j
        for j, v in variables.items()
        if not any(str(i).startswith("hour[") for i in v.index)
    ]
    return keys, global_cols, semantic


def physical_keys(cols, refs):
    """Map the declared physical aspects to exported columns."""
    semantic = {}
    for key, members in refs.items():
        for t, v in enumerate(members):
            semantic[cols[v.mps()]] = (*key, -1 if "capacity" in key[0] else t)
    return semantic


def template(data):
    model, refs = build(data)
    highs = export(model.program, model.program._native_export())
    lp = highs.getLp()
    a = csc_matrix(
        (lp.a_matrix_.value_, lp.a_matrix_.index_, lp.a_matrix_.start_),
        shape=(lp.num_row_, lp.num_col_),
    )
    keys, global_cols, semantic = variable_keys(lp, model.program, refs)
    linear = Linear(
        a,
        np.array(lp.row_lower_),
        np.array(lp.row_upper_),
        np.array(lp.col_cost_),
        np.array(lp.col_lower_),
        np.array(lp.col_upper_),
        keys,
    )
    return linear, global_cols, semantic


def one_row(a, first, second):
    candidates = a[:, first].nonzero()[0]
    if second is not None:
        candidates = np.intersect1d(candidates, a[:, second].nonzero()[0])
    if len(candidates) != 1:
        message = f"Ambiguous coefficient row: {first}, {second}, {candidates}"
        raise ValueError(message)
    return int(candidates[0])


def weather_coefficients(a, ar, by_key, row_map):
    """Locate the renewable capacity coefficients to change in every block."""
    patches = []
    for site in SOURCES:
        for plant in ("PV", "WF"):
            cap = by_key["capacity", site, plant, -1]
            for t in range(2):
                act = by_key["activity", site, plant, t]
                r = one_row(a, act, cap)
                pos = np.flatnonzero((ar.row == row_map[r]) & (ar.col == cap))
                if len(pos) != 1:
                    message = "Missing capacity-factor coefficient"
                    raise ValueError(message)
                patches.append((int(pos[0]), f"{site}_{plant}", t))
    return patches


def load_rows(base, a, by_key, row_map):
    """Locate the NY demand lower bounds in the template."""
    demand_rows = []
    for t in range(2):
        col = by_key["release", "NY", "Power", t]
        candidates = [
            i for i in a[:, col].nonzero()[0] if base.upper[i] == -TEMPLATE_DEMAND
        ]
        if len(candidates) != 1:
            message = "Missing demand lower-bound row"
            raise ValueError(message)
        demand_rows.append(row_map[candidates[0]])
    return demand_rows


def inventory_links(base, a, by_key, row_map):
    """Connect the first inventory balance to the previous block's last hour."""
    carry = []
    for key, j in by_key.items():
        if key[0] == "inventory" and key[3] == 0:
            candidates = [
                i
                for i in a[:, j].nonzero()[0]
                if base.lower[i] == base.upper[i] and a[i, j] == -1
            ]
            if len(candidates) != 1:
                message = "Missing first-hour inventory balance"
                raise ValueError(message)
            carry.append((row_map[candidates[0]], by_key[(*key[:3], 1)]))
    return carry


def vectors(
    base,
    *,
    hourly_rows,
    data,
    demand,
    globals_,
    local,
    mapping,
    by_key,
    demand_rows,
):
    """Repeat hourly bounds and costs, but charge the shared investment once."""
    blocks = len(data["demand"]) // 2
    nl = len(local)
    lower = np.tile(base.lower[hourly_rows], (blocks, 1))
    upper = np.tile(base.upper[hourly_rows], (blocks, 1))
    for t, row in enumerate(demand_rows):
        upper[:, row] = -data["demand"][t::2] if demand else 0
    cost = np.concatenate([base.cost[globals_], np.tile(base.cost[local], blocks)])
    for site in (*SOURCES, "NY"):
        for t in range(2):
            j = by_key["purchase", site, "CH4", t]
            cost[mapping[j] + np.arange(blocks) * nl] = data["gas"][t::2]
    if not demand:
        cost[:] = 0
        for t in range(2):
            j = by_key["release", "NY", "Power", t]
            cost[mapping[j] + np.arange(blocks) * nl] = -1
    keys = [base.keys[j] for j in globals_]
    keys += [
        (*base.keys[j][:3], base.keys[j][3] + 2 * b)
        for b in range(blocks)
        for j in local
    ]
    return lower, upper, cost, keys


def partition(a, globals_):
    """Separate shared investments and their bounds from hourly variables."""
    global_set = set(globals_)
    local = [j for j in range(a.shape[1]) if j not in global_set]
    ng, nl = len(globals_), len(local)
    mapping = np.empty(a.shape[1], dtype=int)
    mapping[globals_] = np.arange(ng)
    mapping[local] = ng + np.arange(nl)
    global_rows = [
        i
        for i in range(a.shape[0])
        if all(j in global_set for j in a.indices[a.indptr[i] : a.indptr[i + 1]])
    ]
    hourly_rows = np.setdiff1d(np.arange(a.shape[0]), global_rows)
    return local, mapping, global_rows, hourly_rows


def expand_matrix(a, data, *, local, mapping, global_rows, hourly_rows, patches, carry):
    """Replicate hourly equations and add chronological inventory links."""
    blocks, nl = len(data["demand"]) // 2, len(local)
    ng = a.shape[1] - nl
    ar = a[hourly_rows].tocoo()
    nr = len(hourly_rows)
    values = np.tile(ar.data, (blocks, 1))
    for pos, key, t in patches:
        values[:, pos] = -data[key][t::2]
    row_indices = np.arange(blocks)[:, None] * nr + ar.row
    col_indices = np.tile(mapping[ar.col], (blocks, 1))
    col_indices[:, np.isin(ar.col, local)] += np.arange(blocks)[:, None] * nl
    rr, cc, vv = [row_indices.ravel()], [col_indices.ravel()], [values.ravel()]
    for row, col in carry:
        rr.append(np.arange(1, blocks) * nr + row)
        cc.append(mapping[col] + np.arange(blocks - 1) * nl)
        vv.append(np.ones(blocks - 1))
    ag = a[global_rows].tocoo()
    rr.append(ag.row + blocks * nr)
    cc.append(mapping[ag.col])
    vv.append(ag.data)
    return coo_matrix(
        (np.concatenate(vv), (np.concatenate(rr), np.concatenate(cc))),
        shape=(blocks * nr + len(global_rows), ng + blocks * nl),
    ).tocsc()


def assemble(data, demand=True):
    n = len(data["demand"])
    if n % 2:
        message = "The block exporter requires an even number of hours"
        raise ValueError(message)
    base_data = {
        key: np.full(2, TEMPLATE_DEMAND if key == "demand" else 0.5) for key in data
    }
    base, globals_, semantic = template(base_data)
    a = base.matrix.tocsr()
    by_key = {key: j for j, key in semantic.items()}
    local, mapping, global_rows, hourly_rows = partition(a, globals_)
    row_map = {int(r): i for i, r in enumerate(hourly_rows)}
    patches = weather_coefficients(a, a[hourly_rows].tocoo(), by_key, row_map)
    demand_rows = load_rows(base, a, by_key, row_map)
    carry = inventory_links(base, a, by_key, row_map)
    matrix = expand_matrix(
        a,
        data,
        local=local,
        mapping=mapping,
        global_rows=global_rows,
        hourly_rows=hourly_rows,
        patches=patches,
        carry=carry,
    )
    lower, upper, cost, keys = vectors(
        base,
        hourly_rows=hourly_rows,
        data=data,
        demand=demand,
        globals_=globals_,
        local=local,
        mapping=mapping,
        by_key=by_key,
        demand_rows=demand_rows,
    )
    return Linear(
        matrix,
        np.concatenate([lower.ravel(), base.lower[global_rows]]),
        np.concatenate([upper.ravel(), base.upper[global_rows]]),
        cost,
        np.concatenate(
            [base.col_lower[globals_], np.tile(base.col_lower[local], n // 2)],
        ),
        np.concatenate(
            [base.col_upper[globals_], np.tile(base.col_upper[local], n // 2)],
        ),
        keys,
    )
