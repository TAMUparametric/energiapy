"""
Expand an exported two-hour Energia model into a chronological annual LP.

Only known hourly input coefficients change. Investment columns are shared,
charged once, and all five inventories link across adjacent blocks.
"""

from dataclasses import dataclass

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
    highs = export(model.program, None)
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


@dataclass
class BlockLayout:
    """Shared and hourly indices for one exported chronological block."""

    base: Linear
    globals: list
    local: list
    mapping: np.ndarray
    global_rows: list
    hourly_rows: np.ndarray
    by_key: dict
    row_map: dict


def vectors(layout, data, demand):
    """Repeat hourly bounds and costs, but charge the shared investment once."""
    demand_rows = load_rows(
        layout.base,
        layout.base.matrix.tocsr(),
        layout.by_key,
        layout.row_map,
    )
    blocks = len(data["demand"]) // 2
    nl = len(layout.local)
    lower = np.tile(layout.base.lower[layout.hourly_rows], (blocks, 1))
    upper = np.tile(layout.base.upper[layout.hourly_rows], (blocks, 1))
    for t, row in enumerate(demand_rows):
        upper[:, row] = -data["demand"][t::2] if demand else 0
    cost = np.concatenate(
        [
            layout.base.cost[layout.globals],
            np.tile(layout.base.cost[layout.local], blocks),
        ],
    )
    for site in (*SOURCES, "NY"):
        for t in range(2):
            j = layout.by_key["purchase", site, "CH4", t]
            cost[layout.mapping[j] + np.arange(blocks) * nl] = data["gas"][t::2]
    if not demand:
        cost[:] = 0
        for t in range(2):
            j = layout.by_key["release", "NY", "Power", t]
            cost[layout.mapping[j] + np.arange(blocks) * nl] = -1
    keys = [layout.base.keys[j] for j in layout.globals]
    keys += [
        (*layout.base.keys[j][:3], layout.base.keys[j][3] + 2 * b)
        for b in range(blocks)
        for j in layout.local
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


def hourly_triplets(layout, data):
    """Expand each hourly coefficient, varying only the renewable profiles."""
    blocks, nl = len(data["demand"]) // 2, len(layout.local)
    a = layout.base.matrix.tocsr()
    ar = a[layout.hourly_rows].tocoo()
    patches = weather_coefficients(a, ar, layout.by_key, layout.row_map)
    values = np.tile(ar.data, (blocks, 1))
    for pos, key, t in patches:
        values[:, pos] = -data[key][t::2]
    row_indices = np.arange(blocks)[:, None] * len(layout.hourly_rows) + ar.row
    col_indices = np.tile(layout.mapping[ar.col], (blocks, 1))
    col_indices[:, np.isin(ar.col, layout.local)] += np.arange(blocks)[:, None] * nl
    return [row_indices.ravel()], [col_indices.ravel()], [values.ravel()]


def expand_matrix(layout, data):
    """Add chronological carry-over and shared investment rows to hourly rows."""
    blocks, nl, nr = (
        len(data["demand"]) // 2,
        len(layout.local),
        len(layout.hourly_rows),
    )
    rr, cc, vv = hourly_triplets(layout, data)
    a = layout.base.matrix.tocsr()
    carry = inventory_links(layout.base, a, layout.by_key, layout.row_map)
    for row, col in carry:
        rr.append(np.arange(1, blocks) * nr + row)
        cc.append(layout.mapping[col] + np.arange(blocks - 1) * nl)
        vv.append(np.ones(blocks - 1))
    ag = a[layout.global_rows].tocoo()
    rr.append(ag.row + blocks * nr)
    cc.append(layout.mapping[ag.col])
    vv.append(ag.data)
    return coo_matrix(
        (np.concatenate(vv), (np.concatenate(rr), np.concatenate(cc))),
        shape=(
            blocks * nr + len(layout.global_rows),
            len(layout.globals) + blocks * nl,
        ),
    ).tocsc()


def block_layout(data):
    """Prepare the reusable mapping from the two-hour exported template."""
    base_data = {
        key: np.full(2, TEMPLATE_DEMAND if key == "demand" else 0.5) for key in data
    }
    base, globals_, semantic = template(base_data)
    by_key = {key: j for j, key in semantic.items()}
    local, mapping, global_rows, hourly_rows = partition(base.matrix.tocsr(), globals_)
    row_map = {int(r): i for i, r in enumerate(hourly_rows)}
    return BlockLayout(
        base,
        globals_,
        local,
        mapping,
        global_rows,
        hourly_rows,
        by_key,
        row_map,
    )


def assemble(data, demand=True):
    """Build one simultaneous LP with every hour and shared investment decision."""
    n = len(data["demand"])
    if n % 2:
        message = "The block exporter requires an even number of hours"
        raise ValueError(message)
    layout = block_layout(data)
    lower, upper, cost, keys = vectors(layout, data, demand)
    return Linear(
        expand_matrix(layout, data),
        np.concatenate([lower.ravel(), layout.base.lower[layout.global_rows]]),
        np.concatenate([upper.ravel(), layout.base.upper[layout.global_rows]]),
        cost,
        np.concatenate(
            [
                layout.base.col_lower[layout.globals],
                np.tile(layout.base.col_lower[layout.local], n // 2),
            ],
        ),
        np.concatenate(
            [
                layout.base.col_upper[layout.globals],
                np.tile(layout.base.col_upper[layout.local], n // 2),
            ],
        ),
        keys,
    )
