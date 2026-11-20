"""Sparse LP utilities and independently written legacy balance equations."""

import hashlib
from dataclasses import dataclass

import numpy as np
from highspy import Highs, HighsLp, HighsModelStatus, HighsStatus, MatrixFormat
from scipy.sparse import coo_matrix, csc_matrix

from .inputs import DISTANCE, INSTALLED, LIMIT, PLANTS, SITES, SOURCES, STORE
from .solver_start import reduce_capacities


@dataclass
class Linear:
    matrix: csc_matrix
    lower: np.ndarray
    upper: np.ndarray
    cost: np.ndarray
    col_lower: np.ndarray
    col_upper: np.ndarray
    keys: list

    def solve(
        self,
        log_file=None,
        warm_basis=None,
        *,
        threads=0,
        objective_budget=None,
    ):
        lp = HighsLp()
        lp.num_col_ = self.matrix.shape[1]
        lp.num_row_ = self.matrix.shape[0]
        lp.col_cost_, lp.col_lower_, lp.col_upper_ = (
            self.cost,
            self.col_lower,
            self.col_upper,
        )
        lp.row_lower_, lp.row_upper_ = self.lower, self.upper
        lp.a_matrix_.format_ = MatrixFormat.kColwise
        lp.a_matrix_.start_ = self.matrix.indptr
        lp.a_matrix_.index_ = self.matrix.indices
        lp.a_matrix_.value_ = self.matrix.data
        h = Highs()
        h.setOptionValue("threads", threads)
        h.setOptionValue(
            "solver",
            "ipm" if objective_budget is not None and warm_basis is None else "simplex",
        )
        # Hand the barrier iterate to crossover early; the final simplex result
        # must still pass the original absolute feasibility and dual-gap checks.
        h.setOptionValue("ipm_optimality_tolerance", 1e-3)
        if log_file:
            h.setOptionValue("log_file", str(log_file))
        h.passModel(lp)
        lifted = (
            reduce_capacities(h, self, objective_budget)
            if objective_budget is not None
            else {}
        )
        if warm_basis is not None:
            if h.readBasis(str(warm_basis)) != HighsStatus.kOk:
                message = "Could not read the maximum-delivery basis"
                raise ValueError(message)
            h.setOptionValue("simplex_strategy", 4)
        h.run()
        if h.getModelStatus() != HighsModelStatus.kOptimal:
            raise RuntimeError(h.modelStatusToString(h.getModelStatus()))
        if log_file is not None:
            h.writeBasis(str(log_file.with_suffix(".basis")))
        sol = h.getSolution()
        x, y, z = (
            np.array(sol.col_value),
            np.array(sol.row_dual),
            np.array(sol.col_dual),
        )
        for column, row in lifted.items():
            y[row] += z[column]
            z[column] = 0
        return x, self.metrics(x, y, z)

    def metrics(self, x, y, z):
        """Recompute primal feasibility, dual stationarity and the objective gap."""
        rows = self.matrix @ x
        finite_sum = lambda a, b: float(a[np.isfinite(b)] @ b[np.isfinite(b)])
        dual = (
            finite_sum(np.maximum(y, 0), self.lower)
            + finite_sum(np.minimum(y, 0), self.upper)
            + finite_sum(np.maximum(z, 0), self.col_lower)
            + finite_sum(np.minimum(z, 0), self.col_upper)
        )
        fingerprint = hashlib.sha256()
        for array in (
            self.matrix.indptr,
            self.matrix.indices,
            self.matrix.data,
            self.lower,
            self.upper,
            self.cost,
            self.col_lower,
            self.col_upper,
        ):
            fingerprint.update(array.tobytes())
        return {
            "matrix_sha256": fingerprint.hexdigest(),
            "objective": float(self.cost @ x),
            "dual_bound": dual,
            "absolute_gap": abs(float(self.cost @ x) - dual),
            "row_violation": float(
                max(0, np.max(self.lower - rows), np.max(rows - self.upper)),
            ),
            "bound_violation": float(
                max(0, np.max(self.col_lower - x), np.max(x - self.col_upper)),
            ),
            "dual_sign_violation": float(
                max(
                    0,
                    np.max(np.maximum(y[~np.isfinite(self.lower)], 0), initial=0),
                    np.max(np.maximum(-y[~np.isfinite(self.upper)], 0), initial=0),
                    np.max(np.maximum(z[~np.isfinite(self.col_lower)], 0), initial=0),
                    np.max(np.maximum(-z[~np.isfinite(self.col_upper)], 0), initial=0),
                ),
            ),
            "dual_residual": float(np.max(abs(self.cost - self.matrix.T @ y - z))),
            "columns": len(self.cost),
            "rows": len(self.lower),
            "nonzeros": self.matrix.nnz,
        }


class Balances:
    """Independent physical equations with sparse triplet storage."""

    def __init__(self, data, demand, indices, *, cost, lower, upper):
        self.data, self.demand, self.indices = data, demand, indices
        self.cost, self.lower, self.upper = cost, lower, upper
        self.rr, self.cc, self.vv, self.lo, self.up = [], [], [], [], []

    def row(self, terms, lb, ub):
        i = len(self.lo)
        for key, value in terms:
            if value:
                self.rr.append(i)
                self.cc.append(self.indices[key])
                self.vv.append(value)
        self.lo.append(lb)
        self.up.append(ub)

    def resources(self, s, t, resources):
        """Balance each resource, including purchases and previous inventory."""
        for resource in resources:
            terms = [
                (("activity", s, p, t), PLANTS[p][2].get(resource, 0))
                for p in INSTALLED[s]
            ]
            if s in SOURCES and resource in ("Solar", "Wind", "CH4", "H2O"):
                key = ("purchase", s, resource, t)
                terms.append((key, 1))
                self.upper[self.indices[key]] = LIMIT
                if self.demand:
                    self.cost[self.indices[key]] = (
                        self.data["gas"][t]
                        if resource == "CH4"
                        else (0.001 if resource == "H2O" else 0)
                    )
            if resource == "H2":
                terms += [
                    (("rail", src, "H2", t), 1 if s == "NY" else -1)
                    for src in (SOURCES if s == "NY" else (s,))
                ]
            if resource == "Power" and s == "NY":
                key = ("release", s, resource, t)
                terms.append((key, -1))
                self.lower[self.indices[key]] = (
                    self.data["demand"][t] if self.demand else 0
                )
                if not self.demand:
                    self.cost[self.indices[key]] = -1
            if resource in ("battery", "CO2_AQoff"):
                key = ("inventory", s, resource, t)
                terms.append((key, -1))
                if t:
                    terms.append((("inventory", s, resource, t - 1), 1))
                self.row(
                    [(key, 1), (("store_capacity", s, resource, -1), -1)],
                    -np.inf,
                    0,
                )
            self.row(terms, 0, 0)

    def hour(self, t):
        """Add activity limits, resource balances and rail limits for one hour."""
        for s in SITES:
            for p in INSTALLED[s]:
                key = ("activity", s, p, t)
                rate = self.data[f"{s}_{p}"][t] if p in ("PV", "WF") else 1
                self.row([(key, 1), (("capacity", s, p, -1), -rate)], -np.inf, 0)
                if self.demand:
                    self.cost[self.indices[key]] = PLANTS[p][1]
            resources = (
                (
                    "Power",
                    "H2",
                    "Solar",
                    "Wind",
                    "CH4",
                    "H2O",
                    "CO2",
                    "CO2_AQoff",
                    "battery",
                )
                if s in SOURCES
                else ("Power", "H2", "battery")
            )
            self.resources(s, t, resources)
        for s in SOURCES:
            key = ("rail", s, "H2", t)
            self.row([(key, 1), (("rail_capacity", s, "H2", -1), -1)], -np.inf, 0)
            if self.demand:
                self.cost[self.indices[key]] = DISTANCE[s] * 0.001667


def independent(data, demand=True):
    """Eliminate zero/unavailable flows and accounting auxiliaries algebraically."""
    n = len(data["demand"])
    global_keys = [("capacity", s, p) for s in SITES for p in INSTALLED[s]]
    global_keys += [
        ("store_capacity", s, r)
        for s in SITES
        for r in (("battery", "CO2_AQoff") if s in SOURCES else ("battery",))
    ]
    global_keys += [("rail_capacity", s, "H2") for s in SOURCES]
    hourly = [("activity", s, p) for s in SITES for p in INSTALLED[s]]
    hourly += [
        ("purchase", s, r) for s in SOURCES for r in ("Solar", "Wind", "CH4", "H2O")
    ]
    hourly += [("release", "NY", "Power")]
    hourly += [
        ("inventory", s, r)
        for s in SITES
        for r in (("battery", "CO2_AQoff") if s in SOURCES else ("battery",))
    ]
    hourly += [("rail", s, "H2") for s in SOURCES]
    keys = [(*key, -1) for key in global_keys] + [
        (*key, t) for t in range(n) for key in hourly
    ]
    indices = {key: i for i, key in enumerate(keys)}
    cost = np.zeros(len(keys))
    upper = np.full(len(keys), np.inf)
    lower = np.zeros(len(keys))
    for key in global_keys:
        j = indices[(*key, -1)]
        upper[j] = STORE if key[0] == "store_capacity" else LIMIT
        if key[0] == "capacity" and demand:
            cost[j] = PLANTS[key[2]][0]
    rows = Balances(data, demand, indices, cost=cost, lower=lower, upper=upper)
    for t in range(n):
        rows.hour(t)
    a = coo_matrix(
        (rows.vv, (rows.rr, rows.cc)),
        shape=(len(rows.lo), len(keys)),
    ).tocsc()
    return Linear(a, np.array(rows.lo), np.array(rows.up), cost, lower, upper, keys)
