"""Solve a one-period supply model using the installed Energia distribution."""

from math import isclose

from gurobipy import GRB

from energia import Currency, Model, Periods, Process, Resource


def main() -> None:
    model = Model("wheel_smoke")
    model.period = Periods()
    model.usd = Currency()
    model.feed = Resource()
    model.power = Resource()
    _ = model.feed.consume >= 0
    _ = model.power.release >= 5
    model.supply = Process()
    _ = model.supply(model.power) == -model.feed
    _ = model.usd.spend(model.supply.operate) == 2
    model.network.locate(model.supply)
    model.usd.spend.opt()

    formulation = next(reversed(model.program.formulations.values()))
    assert formulation.Status == GRB.OPTIMAL, formulation.Status
    supplied, = model.produce.output(aslist=True)
    assert isclose(supplied, 5), supplied
    assert isclose(model.program.active_objective.X, 10), model.program.active_objective.X


if __name__ == "__main__":
    main()
