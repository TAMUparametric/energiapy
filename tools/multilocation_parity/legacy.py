"""Run the pinned historical implementation in a separate legacy environment.

Set PYTHONPATH to c78c8902a7b45be4ed6d56a47341286271e855bf/src. No
legacy library equations are patched; only redundant binary choices are fixed.
"""

import argparse
import hashlib
import inspect
import json
from pathlib import Path

import numpy as np
from energiapy.components.location import Location
from energiapy.components.network import Network
from energiapy.components.scenario import Scenario
from energiapy.components.temporal_scale import TemporalScale
from energiapy.components.transport import Transport
from energiapy.model.constraints.resource_balance import (
    constraint_specific_location_discharge,
)
from energiapy.model.formulate import Constraints, Objective, formulate
from highspy import Highs, HighsModelStatus, HighsVarType
from scipy.sparse import csc_matrix

from .inputs import load_inputs
from .legacy_definitions import definitions


def location(site, names, namespace, *, scales, times, data):
    """Apply full-year normalized factors to a historical location."""
    loc = Location(
        name=site,
        processes={namespace[name] for name in names},
        scales=scales,
        demand_scale_level=2,
        capacity_scale_level=2,
        price_scale_level=1,
    )
    # Set already-normalized mappings after Location initialization so a
    # short window is not renormalized to its own maximum.
    loc.demand_factor = {
        "Power": {
            time: float(data["demand"][t] / 80) if site == "NY" else 0
            for t, time in enumerate(times)
        },
    }
    loc.capacity_factor = (
        {
            p: {time: float(data[f"{site}_{p}"][t]) for t, time in enumerate(times)}
            for p in ("PV", "WF")
        }
        if site != "NY"
        else None
    )
    loc.price_factor = {
        "CH4": {
            (0, t // 24): float(data["gas"][t]) for t in range(len(data["demand"]))
        },
    }
    return loc


def scenario(hours):
    """Execute the original resource/process definitions, with full-year factors."""
    data = {key: value[:hours] for key, value in load_inputs().items()}
    scales = TemporalScale([1, hours // 24, 24] if hours % 24 == 0 else [1, 1, hours])
    namespace = definitions()
    times = scales.scale_iter(scale_level=2)
    locations = {}
    for site, names in [
        ("HO", ["LiI", "PV", "WF", "SMRH", "AWE", "AQoff_SMR"]),
        ("SD", ["LiI", "PV", "WF", "SMRH", "AWE", "AQoff_SMR"]),
        ("NY", ["LiI", "H2FC"]),
    ]:
        loc = location(site, names, namespace, scales=scales, times=times, data=data)
        locations[site] = loc
    rail = Transport(
        name="Train_H2",
        resources={namespace["H2"]},
        trans_max=10**6,
        trans_loss=0.03,
        trans_cost=0.001667,
    )
    network = Network(
        name="Network",
        source_locations=[locations["HO"], locations["SD"]],
        sink_locations=[locations["NY"]],
        distance_matrix=[[2366], [2620]],
        transport_matrix=[[[rail]], [[rail]]],
    )
    power = namespace["Power"]
    case = Scenario(
        name="parity",
        network=network,
        scales=scales,
        purchase_scale_level=1,
        scheduling_scale_level=2,
        network_scale_level=0,
        demand_scale_level=2,
        demand={
            locations["NY"]: {power: 80},
            locations["HO"]: {power: 0},
            locations["SD"]: {power: 0},
        },
    )
    return case, locations, power


def verify_source():
    """Reject a different historical library revision before interpreting results."""
    manifest = json.loads((Path(__file__).parent / "provenance.json").read_text())
    root = Path(inspect.getfile(formulate)).parents[1]
    digest = hashlib.sha256(
        b"".join(
            path.relative_to(root).as_posix().encode() + b"\0" + path.read_bytes()
            for path in sorted(root.rglob("*.py"))
        ),
    ).hexdigest()
    if digest != manifest["legacy_implementation"]["source_sha256"]:
        message = "Historical implementation source hash mismatch"
        raise ValueError(message)
    return manifest, digest


SCALED_TOLERANCE = 1e-6


def solve_case(case, locations, power, objective, *, output, digest):
    """Solve one original formulation and verify its scaled row residuals."""
    m = formulate(
        scenario=case,
        constraints={
            Constraints.COST,
            Constraints.INVENTORY,
            Constraints.PRODUCTION,
            Constraints.RESOURCE_BALANCE,
            Constraints.TRANSPORT,
            Constraints.MODE,
            Constraints.NETWORK,
        },
        objective=objective,
        objective_resource=power,
    )
    for site in ("HO", "SD"):
        setattr(
            m,
            f"no_power_export_{site}",
            constraint_specific_location_discharge(
                instance=m,
                network_scale_level=0,
                bounds={power: 0},
                location=locations[site],
            ),
        )
    path = output / f"{objective.name}.lp"
    m.write(str(path), io_options={"symbolic_solver_labels": True})
    h = Highs()
    h.setOptionValue("threads", 1)
    h.setOptionValue("presolve", "off")
    h.readModel(str(path))
    lp = h.getLp()
    integers = [
        j for j, kind in enumerate(lp.integrality_) if kind == HighsVarType.kInteger
    ]
    # This case has a single mode, zero minimum capacities, and no binary
    # objective costs. Setting every availability binary to one is feasible
    # and leaves the projection onto the continuous physical variables exact.
    for j in integers:
        h.changeColBounds(j, 1, 1)
        h.changeColIntegrality(j, HighsVarType.kContinuous)
    h.run()
    if h.getModelStatus() != HighsModelStatus.kOptimal:
        raise RuntimeError(h.modelStatusToString(h.getModelStatus()))
    x = np.asarray(h.getSolution().col_value)
    a = csc_matrix(
        (lp.a_matrix_.value_, lp.a_matrix_.index_, lp.a_matrix_.start_),
        shape=(lp.num_row_, lp.num_col_),
    )
    row = a @ x
    violation = float(
        max(
            0,
            np.max(np.asarray(lp.row_lower_) - row),
            np.max(row - np.asarray(lp.row_upper_)),
        ),
    )
    scale = np.maximum(1, abs(a) @ abs(x))
    residual = np.maximum.reduce(
        [
            np.zeros(lp.num_row_),
            np.asarray(lp.row_lower_) - row,
            row - np.asarray(lp.row_upper_),
        ],
    )
    scaled_violation = float(np.max(residual / scale))
    if scaled_violation > SCALED_TOLERANCE:
        message = "Historical model has excessive scaled residual"
        raise AssertionError(message)
    return {
        "objective": h.getObjectiveValue(),
        "max_row_violation": violation,
        "max_scaled_row_violation": scaled_violation,
        "implementation_sha256": digest,
        "binary_completion": "all one",
        "binaries": len(integers),
    }


def compare_results(report, comparison, hours, manifest):
    """Compare like-for-like short windows with the current Energia result."""
    current = json.loads(comparison.read_text())
    if current["hours"] != hours:
        message = "Historical and current checks must use the same hours"
        raise ValueError(message)
    for objective, name, sign in [
        ("COST", "cost", 1),
        ("MAX_DISCHARGE", "delivery", -1),
    ]:
        error = abs(
            report[objective]["objective"]
            - sign * current["cases"][name]["energia"]["objective"],
        )
        if error > manifest["case"]["archive_tolerance"]:
            message = f"Historical/current objective mismatch: {name}: {error}"
            raise AssertionError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--hours", type=int, default=6)
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest, digest = verify_source()
    case, locations, power = scenario(args.hours)
    report = {}
    for objective in (Objective.COST, Objective.MAX_DISCHARGE):
        report[objective.name] = solve_case(
            case,
            locations,
            power,
            objective,
            output=args.output,
            digest=digest,
        )
    if args.compare is not None:
        compare_results(report, args.compare, args.hours, manifest)
    (args.output / "legacy.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
