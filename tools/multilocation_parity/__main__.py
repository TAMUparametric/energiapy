"""Verify the archived multi-location study and write independent audit evidence."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .assembly import assemble
from .inputs import DATA, HOURS, load_inputs
from .linear import independent
from .solver_start import feasible_budget

BLOCK_HOURS = 2
HERE = Path(__file__).parent
FEASIBILITY_TOLERANCE = 1e-6
OBJECTIVE_TOLERANCE = 0.001


def provenance():
    """Fail before solving if the original input bytes have changed."""
    manifest = json.loads((HERE / "provenance.json").read_text())
    for name, record in manifest["inputs"].items():
        actual = hashlib.sha256((DATA / name).read_bytes()).hexdigest()
        if actual != record["sha256"]:
            message = f"Input hash mismatch: {name}"
            raise ValueError(message)
    return manifest


def environment():
    """Record source and package versions without claiming a historical lock."""
    return {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in (
                "energiapy",
                "gana",
                "vaelchi",
                "highspy",
                "numpy",
                "scipy",
                "pandas",
            )
        },
        "script_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(HERE.glob("*.py"))
        },
        "energia_source_sha256": hashlib.sha256(
            b"".join(
                path.read_bytes()
                for path in sorted((HERE.parents[1] / "src/energia").rglob("*.py"))
            ),
        ).hexdigest(),
        "solver_options": {
            "delivery_solver": "simplex",
            "cost_solver": "ipm with crossover and verified capacity reductions",
            "threads": 1,
            "warm_basis_strategy": "primal",
            "ipm_crossover_threshold": 1e-3,
        },
    }


def require_close(actual, expected, tolerance, label):
    if abs(actual - expected) > tolerance:
        message = f"{label}: {actual} != {expected} (absolute tolerance {tolerance})"
        raise AssertionError(message)


def check_metrics(metrics):
    for key in (
        "row_violation",
        "bound_violation",
        "dual_residual",
        "dual_sign_violation",
    ):
        require_close(metrics[key], 0, FEASIBILITY_TOLERANCE, key)
    require_close(metrics["absolute_gap"], 0, OBJECTIVE_TOLERANCE, "Primal-dual gap")


def project(energia, x, reference):
    """Check every hourly physical variable against the independent equations."""
    indices = {key: j for j, key in enumerate(energia.keys)}
    projected = x[[indices[key] for key in reference.keys]]
    rows = reference.matrix @ projected
    violation = float(
        max(0, np.max(reference.lower - rows), np.max(rows - reference.upper)),
    )
    bounds = float(
        max(
            0,
            np.max(reference.col_lower - projected),
            np.max(projected - reference.col_upper),
        ),
    )
    require_close(violation, 0, FEASIBILITY_TOLERANCE, "Projected balance violation")
    require_close(bounds, 0, FEASIBILITY_TOLERANCE, "Projected bound violation")
    require_close(
        float(reference.cost @ projected),
        float(energia.cost @ x),
        OBJECTIVE_TOLERANCE,
        "Projected objective",
    )
    return projected, {"row_violation": violation, "bound_violation": bounds}


def write_dispatch(output, name, reference, x):
    """Keep readable hourly flows and capacities, including zero/idle options."""
    profiles = {}
    capacities = {}
    for key, value in zip(reference.keys, x):
        kind, site, component, t = key
        label = "/".join((kind, site, component))
        if t == -1:
            capacities[label] = float(value)
        else:
            profiles.setdefault(label, []).append(value)
    pd.DataFrame(profiles).to_csv(
        output / f"{name}-hourly.csv.gz",
        index_label="hour",
        float_format="%.17g",
        compression={"method": "gzip", "mtime": 0},
    )
    (output / f"{name}-capacities.json").write_text(
        json.dumps(capacities, indent=2) + "\n",
    )


def run_case(data, demand, output, basis_dir=None):
    name = "cost" if demand else "delivery"

    def basis(kind):
        if basis_dir is not None:
            path = basis_dir / f"{name}-{kind}.basis"
            return path if path.is_file() else None
        return None

    reference = independent(data, demand=demand)
    budget = feasible_budget(reference, data) if demand else None
    _, reference_metrics = reference.solve(
        output / f"{name}-independent.log",
        warm_basis=basis("independent"),
        threads=1,
        objective_budget=budget,
    )
    check_metrics(reference_metrics)
    energia = assemble(data, demand=demand)
    x, energia_metrics = energia.solve(
        output / f"{name}-energia.log",
        warm_basis=basis("energia"),
        threads=1,
        objective_budget=budget,
    )
    check_metrics(energia_metrics)
    projected, physical = project(energia, x, reference)
    require_close(
        energia_metrics["objective"],
        reference_metrics["objective"],
        OBJECTIVE_TOLERANCE,
        name,
    )
    write_dispatch(output, name, reference, projected)
    if len(data["demand"]) == HOURS:
        case = provenance()["case"]
        expected = case["archived_cost"] if demand else -case["archived_delivery"]
        require_close(
            energia_metrics["objective"],
            expected,
            case["archive_tolerance"],
            "Archived " + name,
        )
    return {
        "energia": energia_metrics,
        "independent": reference_metrics,
        "physical_projection": physical,
        "feasible_cost_bound": budget,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--hours", type=int, default=HOURS)
    parser.add_argument(
        "--basis-dir",
        type=Path,
        help="Optional previous solver bases; all LPs are still solved and verified.",
    )
    args = parser.parse_args()
    if args.hours < BLOCK_HOURS or args.hours > HOURS or args.hours % 2:
        parser.error("Choose an even number of hours between 2 and 8,760.")
    if args.output.resolve().is_relative_to(HERE.resolve()):
        parser.error("Choose an output directory outside the validation source.")
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = provenance()
    data = {key: value[: args.hours] for key, value in load_inputs().items()}
    report = {
        "hours": args.hours,
        "environment": environment(),
        "provenance": manifest,
        "cases": {},
    }
    for demand in (False, True):
        name = "cost" if demand else "delivery"
        report["cases"][name] = run_case(data, demand, args.output, args.basis_dir)
        (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["cases"], indent=2))


if __name__ == "__main__":
    main()
