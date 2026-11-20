"""Solve a one-period supply model using the installed Energia distribution."""

import json
from math import isclose
from pathlib import Path
from tempfile import TemporaryDirectory

from energia import Currency, Model, Periods, Process, Resource


def main() -> None:
    demand = 5
    unit_cost = 2
    model = Model("wheel_smoke")
    model.period = Periods()
    model.usd = Currency()
    model.feed = Resource()
    model.power = Resource()
    _ = model.feed.consume >= 0
    _ = model.power.release >= demand
    model.supply = Process()
    _ = model.supply(model.power) == -model.feed
    _ = model.usd.spend(model.supply.operate) == unit_cost
    model.network.locate(model.supply)
    model.usd.spend.opt()

    with TemporaryDirectory() as directory:
        path = Path(directory) / "solution.json"
        model.save(as_type="json", path=path)
        status = json.loads(path.read_text())["status"]
    if status != "optimal":
        raise AssertionError(status)
    (supplied,) = model.produce.output(aslist=True)
    if not isclose(supplied, demand):
        raise AssertionError(supplied)
    objective = model.program.active_objective.X
    if not isclose(objective, demand * unit_cost):
        raise AssertionError(objective)


if __name__ == "__main__":
    main()
