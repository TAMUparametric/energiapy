"""Energia formulation of the original lossless chronological study."""

from dataclasses import dataclass

from gana import inf

from energia import Location, Model, Periods, Process, Resource, Storage, Transport

from .inputs import DISTANCE, INSTALLED, LIMIT, PLANTS, SITES, SOURCES, STORE


@dataclass
class ResourceContext:
    """Resource declarations, profiles and collected calls for one model."""

    model: Model
    data: dict
    demand: bool
    refs: dict


def resource_flows(context, site, resource):
    """Bound one resource's purchase and release, retaining its physical calls."""
    m, data, demand, refs = context.model, context.data, context.demand, context.refs
    loc = getattr(m, site)
    obj = getattr(m, resource)
    purchase = obj.consume(loc, m.hour)
    _ = purchase <= (
        LIMIT if site in SOURCES and resource in ("Solar", "Wind", "H2O", "CH4") else 0
    )
    refs[("purchase", site, resource)] = list(purchase.V())
    release = obj.release(loc, m.hour)
    is_demand = site == "NY" and resource == "Power"
    _ = release >= (data["demand"].tolist() if is_demand and demand else 0)
    if not (is_demand or resource in ("CO2_Vent", "O2")):
        _ = release <= 0
    refs[("release", site, resource)] = list(release.V())
    return purchase


def add_resources(context, site, resources):
    """Declare permitted purchases, exports and the NY demand lower bounds."""
    cost = 0
    for resource in resources:
        purchase = resource_flows(context, site, resource)
        if resource == "H2O":
            cost += 0.001 * sum(purchase.V())
        if resource == "CH4":
            cost += sum(
                float(rate) * v for rate, v in zip(context.data["gas"], purchase.V())
            )
    return cost


def create_plant(m, battery, site, name):
    """Use the store's charge/discharge plants or declare a conversion process."""
    if name == "LiI":
        plant = battery.charge
    elif name == "LiI_discharge":
        plant = battery.discharge
    else:
        terms = [
            coefficient * getattr(m, resource)
            for resource, coefficient in PLANTS[name][2].items()
        ]
        balance = terms[0]
        for term in terms[1:]:
            balance = balance + term
        plant = Process(balance)
        setattr(m, f"{site}_{name}", plant)
    return plant


def add_site(m, data, refs, site):
    """Install the source technology set and chronological stores."""
    loc = getattr(m, site)
    cost = 0
    battery = Storage(m.Power == 1)
    setattr(m, f"{site}_battery", battery)
    _ = battery.capacity(loc, m.year) <= STORE
    _ = battery.inventory(loc, m.hour) <= 1
    refs[("store_capacity", site, "battery")] = list(battery.capacity(loc, m.year).V())
    refs[("inventory", site, "battery")] = list(battery.inventory(loc, m.hour).V())
    for name in INSTALLED[site]:
        fixed, variable, _ = PLANTS[name]
        plant = create_plant(m, battery, site, name)
        capacity = plant.capacity(loc, m.year)
        _ = capacity <= LIMIT
        activity = plant.operate(loc, m.hour)
        factor = data[f"{site}_{name}"].tolist() if name in ("PV", "WF") else 1
        _ = activity <= factor
        plant.locate(loc)
        refs[("capacity", site, name)] = list(capacity.V())
        refs[("activity", site, name)] = list(activity.V())
        cost += fixed * capacity.V()[0] + variable * sum(activity.V())
    battery.locate(loc)
    if site in SOURCES:
        reservoir = Storage(m.CO2_AQoff == 1)
        setattr(m, f"{site}_reservoir", reservoir)
        _ = reservoir.capacity(loc, m.year) <= STORE
        _ = reservoir.inventory(loc, m.hour) <= 1
        _ = reservoir.charge.capacity(loc, m.year) == LIMIT
        _ = reservoir.charge.operate(loc, m.hour) <= 1
        _ = reservoir.discharge.capacity(loc, m.year) == 0
        _ = reservoir.discharge.operate(loc, m.hour) <= 1
        reservoir.locate(loc)
        refs[("store_capacity", site, "CO2_AQoff")] = list(
            reservoir.capacity(loc, m.year).V(),
        )
        refs[("inventory", site, "CO2_AQoff")] = list(
            reservoir.inventory(loc, m.hour).V(),
        )
    return cost


def build(data, demand=True):
    m = Model("annual_parity")
    m.hour = Periods()
    m.year = len(data["demand"]) * m.hour
    m.declare(Location, SITES)
    resources = sorted(
        {
            r
            for _, _, conversion in PLANTS.values()
            for r in conversion
            if r != "battery"
        },
    )
    m.declare(Resource, resources)
    refs = {}
    cost = 0
    for site in SITES:
        cost += add_resources(ResourceContext(m, data, demand, refs), site, resources)
        cost += add_site(m, data, refs, site)
    m.rail = Transport()
    _ = m.rail(m.H2) == 1
    for site in SOURCES:
        m.Link(getattr(m, site), m.NY, dist=DISTANCE[site])
        link = getattr(m, site) - m.NY
        _ = m.rail.capacity(link, m.year) <= LIMIT
        flow = m.rail.operate(link, m.hour)
        _ = flow <= 1
        m.rail.locate(link)
        refs[("rail_capacity", site, "H2")] = list(m.rail.capacity(link, m.year).V())
        refs[("rail", site, "H2")] = list(flow.V())
        cost += DISTANCE[site] * 0.001667 * sum(flow.V())
    m.program.total_cost = inf(cost)
    return m, refs
