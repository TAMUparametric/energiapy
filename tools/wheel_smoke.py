"""Solve a one-period supply model using the installed Energia distribution."""

from math import isclose

from gurobipy import GRB

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

    status = model.program.formulation.Status
    if status != GRB.OPTIMAL:
        raise AssertionError(status)
    (supplied,) = model.produce.output(aslist=True)
    if not isclose(supplied, demand):
        raise AssertionError(supplied)
    objective = model.program.active_objective.X
    if not isclose(objective, demand * unit_cost):
        raise AssertionError(objective)


if __name__ == "__main__":
    main()
