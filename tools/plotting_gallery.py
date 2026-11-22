"""Reproduce manuscript figures from the bundled design/scheduling example."""

import argparse
import json
from pathlib import Path

from gana.plotting import grid

from energia import Unit
from energia.library.examples.energy import design_scheduling


def figures():
    """Solve the documented example and return four detached Gana plots."""
    model = design_scheduling()
    model.wf.label, model.pv.label = "Wind", "Solar"
    model.usd.basis = Unit(label="USD")
    model.usd.spend.opt()
    q, y = model.q, model.y
    dispatch = model.line(
        model.wf.operate(q),
        model.pv.operate(q),
        title="Generation",
        ylabel="Operation (model units)",
        xlabel="Model period",
        ticks=[0, 1, 2, 3],
    )
    capacity = model.bar(
        model.wf.capacity(y),
        model.pv.capacity(y),
        title="Installed capacity",
        ylabel="Capacity (model units)",
        xlabel="Planning horizon",
        ticks=[0],
        tick_labels=["Design"],
    )
    storage = model.lii.inventory(q).line(
        title="Storage inventory",
        label="Inventory",
        ylabel="Inventory (model units)",
        xlabel="Model period",
        ticks=[0, 1, 2, 3],
    )
    cost = model.bar(
        model.usd.spend(y, model.wf.operate),
        model.usd.spend(y, model.pv.operate),
        title="Operating expenditure",
        ylabel="Cost (USD)",
        xlabel="Planning horizon",
        ticks=[0],
        tick_labels=["Operation"],
    )
    return {
        "dispatch": dispatch,
        "capacity": capacity,
        "inventory": storage,
        "cost": cost,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    plots = figures()
    for name, plot in plots.items():
        for suffix in ("pdf", "svg", "png"):
            plot.save(
                args.output / f"{name}.{suffix}",
                profile="print",
                fig_size=(3.5, 2.6),
                dpi=300,
            )
    gallery = grid(
        [[plots["dispatch"], plots["capacity"]], [plots["inventory"], plots["cost"]]],
    )
    for suffix in ("pdf", "svg", "png"):
        gallery.save(
            args.output / f"plotting-gallery.{suffix}",
            profile="print",
            fig_size=(7.2, 5.4),
            dpi=300,
        )
    data = {
        name: [
            {
                "label": s.label,
                "x": s.x,
                "values": s.values,
                "unit": s.unit,
                "n_sol": s.n_sol,
            }
            for s in plot.data
        ]
        for name, plot in plots.items()
    }
    (args.output / "plotting-data.json").write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
