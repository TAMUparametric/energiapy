"""Energy system examples"""

from ...components.commodities.currency import Currency
from ...components.commodities.material import Material
from ...components.commodities.resource import Resource
from ...components.impact.categories import Environ
from ...components.measure.unit import Unit
from ...components.operations.process import Process
from ...components.operations.storage import Storage
from ...components.spatial.location import Location
from ...components.temporal.periods import Periods
from ...components.temporal.scales import TemporalScales
from ...represent.model import Model

# Shared inputs for the scheduling examples.
_WIND_LIMIT = 400
_SOLAR_LIMIT = 100
_MIN_CAPACITY = 10
_MAX_CAPACITY = 100
_WIND_OPERATING_COST = 49
_PV_OPERATING_COST = 90_000
_STORAGE_EFFICIENCY = 0.9
_INVENTORY_COST = 2_000


def scheduling():
    """A small scheduling example"""
    m = Model("scheduling")
    m.q = Periods()
    m.y = 4 * m.q
    m.usd = Currency()
    m.wind, m.power = Resource(), Resource()
    _ = m.wind.consume <= _WIND_LIMIT
    _ = m.power.release.prep(100) >= [0.6, 0.7, 1, 0.3]
    m.wf = Process()
    _ = m.wf(m.power) == -1 * m.wind
    _ = m.wf.operate.prep(200, norm=False) <= [0.9, 0.8, 0.5, 0.7]
    _ = m.usd.spend(m.wf.operate) == [4000, 4200, 4300, 3900]
    m.network.locate(m.wf)
    return m


def scheduling_w_attrs():
    """A small scheduling example with attributes"""
    m = Model("scheduling")
    m.q = Periods()
    m.y = 4 * m.q
    m.usd = Currency()
    m.wind = Resource(consume_max=_WIND_LIMIT)
    m.power = Resource(demand_nominal=100, demand=[0.6, 0.7, 1, 0.3])
    m.wf = Process(
        m.power == -1 * m.wind,
        operate_nominal=200,
        operate_normalize=False,
        operate_max=[0.9, 0.8, 0.5, 0.7],
        opex=[4000, 4200, 4300, 3900],
    )
    m.network.locate(m.wf)
    return m


def scheduling_wo_time():
    """A small scheduling example with attributes"""
    m = Model("scheduling")
    # m.q = Periods()
    # m.y = 4 * m.q
    m.usd = Currency()
    # TODO: does not work if order changed
    m.wind = Resource(consume_max=_WIND_LIMIT)
    m.power = Resource(demand_nominal=100, demand_min=[0.6, 0.7, 1, 0.3])
    # TODO:
    m.wf = Process(
        m.power == -1 * m.wind,
        operate_nominal=200,
        operate_normalize=False,
        operate_max=[0.9, 0.8, 0.5, 0.7],
        opex=[4000, 4200, 4300, 3900],
    )
    m.network.locate(m.wf)
    # TODO: solution error
    return m


def design_scheduling_w_gattr():
    """A small design and scheduling example"""
    m = Model("design_scheduling")
    m.q = Periods()
    m.y = 4 * m.q
    m.usd = Currency()
    m.declare(Resource, ["power", "wind", "solar"])
    _ = m.solar.consume(m.q) <= _SOLAR_LIMIT
    _ = m.wind.consume <= _WIND_LIMIT
    _ = m.power.release.prep(180) >= [0.6, 0.7, 0.8, 0.3]
    m.wf = Process()
    _ = m.wf(m.power) == -1 * m.wind
    _ = m.wf.capacity.x <= _MAX_CAPACITY
    _ = m.wf.capacity.x >= _MIN_CAPACITY
    _ = m.wf.operate.prep(norm=True) <= [0.9, 0.8, 0.5, 0.7]
    _ = m.wf.capacity[m.usd.spend] == 990637 + 3354
    _ = m.wf.operate[m.usd.spend] == _WIND_OPERATING_COST

    m.pv = Process()
    _ = m.pv(m.power) == -1 * m.solar
    _ = m.pv.capacity.x <= _MAX_CAPACITY
    _ = m.pv.capacity.x >= _MIN_CAPACITY
    _ = m.pv.operate.prep(norm=True) <= [0.6, 0.8, 0.9, 0.7]
    _ = m.pv.capacity[m.usd.spend] == 567000 + 872046
    _ = m.pv.operate[m.usd.spend] == _PV_OPERATING_COST

    m.lii = Storage()
    _ = m.lii(m.power) == _STORAGE_EFFICIENCY
    _ = m.lii.capacity.x <= _MAX_CAPACITY
    _ = m.lii.capacity.x >= _MIN_CAPACITY
    _ = m.lii.capacity[m.usd.spend] == 1302182 + 41432
    _ = m.lii.inventory[m.usd.spend] == _INVENTORY_COST

    m.network.locate(m.wf, m.pv, m.lii)

    return m


def design_scheduling():
    """
    A small design and scheduling example
    with functions for calculations instead of getattr
    """
    m = Model("design_scheduling")
    m.q = Periods()
    m.y = 4 * m.q
    m.usd = Currency()
    m.declare(Resource, ["power", "wind", "solar"])
    _ = m.solar.consume(m.q) <= _SOLAR_LIMIT
    _ = m.wind.consume <= _WIND_LIMIT
    _ = m.power.release.prep(180) >= [0.6, 0.7, 0.8, 0.3]

    m.wf = Process(m.power == -1 * m.wind)
    _ = m.wf.capacity.x <= _MAX_CAPACITY
    _ = m.wf.capacity.x >= _MIN_CAPACITY
    _ = m.wf.operate.prep(norm=True) <= [0.9, 0.8, 0.5, 0.7]
    _ = m.usd.spend(m.wf.capacity) == 990637 + 3354
    _ = m.usd.spend(m.wf.operate) == _WIND_OPERATING_COST

    m.pv = Process(m.power == -1 * m.solar)
    _ = m.pv.capacity.x <= _MAX_CAPACITY
    _ = m.pv.capacity.x >= _MIN_CAPACITY
    _ = m.pv.operate.prep(norm=True) <= [0.6, 0.8, 0.9, 0.7]
    _ = m.usd.spend(m.pv.capacity) == 567000 + 872046
    _ = m.usd.spend(m.pv.operate) == _PV_OPERATING_COST

    m.lii = Storage(m.power == _STORAGE_EFFICIENCY)
    _ = m.lii.capacity.x <= _MAX_CAPACITY
    _ = m.lii.capacity.x >= _MIN_CAPACITY
    _ = m.usd.spend(m.lii.capacity) == 1302182 + 41432
    _ = m.usd.spend(m.lii.inventory) == _INVENTORY_COST
    m.network.locate(m.wf, m.pv, m.lii)

    return m


def design_scheduling_w_attrs():
    """A small design and scheduling example with attributes"""

    m = Model()
    m.q = Periods()
    m.y = 4 * m.q
    m.usd = Currency()
    m.solar = Resource(consume_max=[_SOLAR_LIMIT] * 4)
    m.wind = Resource(consume_max=_WIND_LIMIT)
    m.power = Resource(demand_nominal=180, demand_min=[0.6, 0.7, 0.8, 0.3])
    m.wf = Process(
        m.power == -1.0 * m.wind,
        capacity_max=_MAX_CAPACITY,
        capacity_min=_MIN_CAPACITY,
        capacity_optional=True,
        operate_normalize=True,
        operate_max=[0.9, 0.8, 0.5, 0.7],
        capex=990637 + 3354,
        opex=_WIND_OPERATING_COST,
    )

    m.pv = Process(
        m.power == -1 * m.solar,
        capacity_max=_MAX_CAPACITY,
        capacity_min=_MIN_CAPACITY,
        capacity_report=True,
        operate_normalize=True,
        operate_max=[0.6, 0.8, 0.9, 0.7],
        capex=567000 + 872046,
        opex=_PV_OPERATING_COST,
    )
    m.lii = Storage(
        m.power == _STORAGE_EFFICIENCY,
        capacity_max=_MAX_CAPACITY,
        capacity_min=_MIN_CAPACITY,
        capacity_optional=True,
        capex=1302182 + 41432,
        inventory_cost=_INVENTORY_COST,
    )

    m.locate(m.wf, m.pv, m.lii)

    return m


def design_scheduling_material():

    m = Model("design_scheduling_material")
    m.q = Periods()
    m.y = 4 * m.q
    m.usd = Currency()

    m.declare(Resource, ["power", "wind", "solar"])
    _ = m.solar.consume(m.q) <= _SOLAR_LIMIT
    _ = m.wind.consume <= _WIND_LIMIT
    _ = m.power.release.prep(180) >= [0.6, 0.7, 0.8, 0.3]

    m.wf = Process()
    _ = m.wf(m.power) == -1 * m.wind
    _ = m.wf.capacity.x <= _MAX_CAPACITY
    _ = m.wf.capacity.x >= _MIN_CAPACITY
    _ = m.wf.operate.prep(norm=True) <= [0.9, 0.8, 0.5, 0.7]
    _ = m.usd.spend(m.wf.capacity) == 990637 + 3354
    _ = m.usd.spend(m.wf.operate) == _WIND_OPERATING_COST

    m.pv = Process()
    _ = m.pv(m.power) == -1 * m.solar
    _ = m.pv.capacity.x <= _MAX_CAPACITY
    _ = m.pv.capacity.x >= _MIN_CAPACITY
    _ = m.pv.operate.prep(norm=True) <= [0.6, 0.8, 0.9, 0.7]
    _ = m.usd.spend(m.pv.capacity) == 567000 + 872046
    _ = m.usd.spend(m.pv.operate) == _PV_OPERATING_COST

    m.lii = Storage()
    _ = m.lii(m.power) == _STORAGE_EFFICIENCY
    _ = m.lii.capacity.x <= _MAX_CAPACITY
    _ = m.lii.capacity.x >= _MIN_CAPACITY
    _ = m.usd.spend(m.lii.capacity) == 1302182 + 41432
    _ = m.usd.spend(m.lii.inventory) == _INVENTORY_COST

    m.cement = Material()
    cement_limit = 1_000_000
    cement_price = 17
    _ = m.cement.consume <= cement_limit
    _ = m.usd.spend(m.cement.consume) == cement_price
    for plant, cement in ((m.wf, 400), (m.pv, 560), (m.lii, 300)):
        _ = m.cement.use(plant.capacity) == cement

    m.gwp = Environ()
    for plant, emissions in ((m.wf, 1000), (m.pv, 2000), (m.lii, 3000)):
        _ = m.gwp.emit(plant.capacity) == emissions
    cement_emissions = 0.9
    _ = m.gwp.emit(m.cement.consume) == cement_emissions

    m.network.locate(m.wf, m.pv, m.lii)

    return m


def design_scheduling_material_modes():
    """Design and scheduling considering materials and emissions from them"""
    m = Model("design_scheduling")
    m.scales = TemporalScales([1, 4], ["y", "q"])
    m.usd = Currency()
    m.gwp = Environ()
    m.declare(
        Material,
        [
            "lir",
            "lib",
            "steel",
            "concrete",
            "glass",
            "si_mono",
            "si_poly",
        ],
    )

    m.declare(Resource, ["power", "wind", "solar"])
    _ = m.solar.consume >= 0
    _ = m.wind.consume >= 0
    _ = m.power.release.prep(180) >= [0.6, 0.7, 0.8, 0.3]

    steel_price = 670
    for material, emissions in ((m.lir, 9600), (m.lib, 2800), (m.steel, 2121.152427)):
        _ = m.gwp.emit(material.consume) == emissions
    _ = m.usd.spend(m.steel.consume) == steel_price
    for material, emissions in (
        (m.concrete, 120.0378),
        (m.glass, 1118.5),
        (m.si_mono, 122239.1),
        (m.si_poly, 98646.7),
    ):
        _ = m.gwp.emit(material.consume) == emissions

    m.wf = Process()
    _ = m.wf.capacity.x <= _MAX_CAPACITY
    _ = m.wf.capacity.x >= _MIN_CAPACITY
    _ = m.wf.operate.prep(norm=True) <= [0.9, 0.8, 0.5, 0.7]
    _ = m.wf.construction == [
        -109.9 * m.steel - 398.7 * m.concrete,
        -249.605 * m.steel - 12.4 * m.concrete,
    ]

    _ = m.wf(m.power) == {
        m.wf.construction.modes[0]: -2.857 * m.wind,
        m.wf.construction.modes[1]: -2.3255 * m.wind,
    }

    _ = m.usd.spend(m.wf.capacity, m.wf.construction.modes) == [
        1292000 + 29200,
        3192734 + 101498,
    ]

    _ = m.usd.spend(m.wf.operate) == _WIND_OPERATING_COST

    m.pv = Process()
    _ = m.pv.construction == [
        -70 * m.glass - 7 * m.si_mono,
        -70 * m.glass - 7 * m.si_poly,
    ]

    _ = m.pv(m.power) == {
        m.pv.construction.modes[0]: -5 * m.solar,
        m.pv.construction.modes[1]: -6.67 * m.solar,
    }
    _ = m.pv.capacity.x <= _MAX_CAPACITY
    _ = m.pv.capacity.x >= _MIN_CAPACITY
    _ = m.pv.operate.prep(norm=True) <= [0.6, 0.8, 0.9, 0.7]

    _ = m.usd.spend(m.pv.capacity) == 567000 + 872046
    _ = m.usd.spend(m.pv.operate) == _PV_OPERATING_COST

    m.lii = Storage()
    _ = m.lii(m.power) == _STORAGE_EFFICIENCY
    _ = m.lii.construction == [
        -0.137 * m.lib - 1.165 * m.steel,
        -0.137 * m.lir - 1.165 * m.steel,
    ]
    _ = m.lii.capacity.x <= _MAX_CAPACITY
    _ = m.lii.capacity.x >= _MIN_CAPACITY

    _ = m.usd.spend(m.lii.capacity) == 1302182 + 41432
    _ = m.usd.spend(m.lii.inventory) == _INVENTORY_COST

    m.network.locate(m.wf, m.pv, m.lii)
    return m


def supermarket():
    """A supermarket energy system example

    Optimize for cost:
        m.usd.spend.opt()

    Optimize for CO2 emissions:
        m.co2_vent.release.opt()

    Maximize efficiency:
        m._.lb(sum(m._.consume))
    """
    m = Model("supermarket")
    _supermarket_resources(m)
    _supermarket_generation(m)
    _supermarket_consumption(m)

    # Locations serve as aggregations of scenarios

    m.supermarket.locate(
        m.st,
        m.chp,
        m.pv,
        m.wf,
        m.grid,
        m.refrigerator,
        m.led,
        m.heater,
    )

    # Various constraints are need for the formulating the mathematical programming model. Here we include the cost, production, resource balance, demand, inventory, and network constraints.

    return m


def _supermarket_resources(m):
    """Declare supplies, prices, and end-use demands."""
    resource_demand_dict = {
        "Lighting": 200,
        "Refrigeration": 1000,
        "Space Heating": 100,
    }

    prices = {"Natural Gas": 8.89, "Biomass": 9.72, "Grid Electricity": 36.11}

    m.supermarket = Location()

    m.GJ = Unit(label="Giga Joules")
    m.PJ = 10**6 * m.GJ
    m.kW = Unit(label="kilo Watts")
    m.tons = Unit(label="US Tons")

    # Resources can be declared along with thier attributes such as maximum allowed consumption, dischargeablity, base price, etc.

    m.usd = Currency(label="$")

    m.biomass = Resource(basis=m.GJ, label="Biomass")
    m.biomass.consume.V()
    _ = m.biomass.consume[m.usd.spend] == prices["Biomass"]

    m.gridpower = Resource(basis=m.GJ, label="Grid Electricity")
    m.gridpower.consume.V()
    _ = m.gridpower.consume[m.usd.spend] == prices["Grid Electricity"]

    m.ng = Resource(basis=m.GJ, label="Natural gas")
    m.ng.consume.V()
    _ = m.ng.consume[m.usd.spend] == prices["Natural Gas"]

    m.power = Resource(basis=m.kW, label="Electrical Power")
    m.heat = Resource(basis=m.kW, label="Heat Power")

    _ = m.co2_vent = Resource(basis=m.tons, label="Carbon dioxide")
    m.co2_vent.release.V()

    m.solar = Resource(basis=m.GJ, label="Solar energy")
    m.solar.consume.V()
    _ = m.wind = Resource(basis=m.GJ, label="Wind energy")
    m.wind.consume.V()

    m.lighting = Resource(basis=m.kW, label="Lighting")
    _ = m.lighting.release >= resource_demand_dict["Lighting"]

    m.refrigeration = Resource(basis=m.kW, label="Refrigeration")
    _ = m.refrigeration.release >= resource_demand_dict["Refrigeration"]

    m.heating = Resource(basis=m.kW, label="Heating")
    _ = m.heating.release >= resource_demand_dict["Space Heating"]


def _supermarket_generation(m):
    """Bind generator efficiencies, emissions, capacities, and costs."""
    co2_factors = {"Natural Gas": 56, "Biomass": 100, "Grid Electricity": 90}
    generation_process_dict = {
        "Biomass ST": {
            "nE": 68,
            "nH": 0,
            "LB": 100,
            "UB": 10**6,
            "Capex": 250,
            "Opex": 15,
        },
        "Natural Gas CHP": {
            "nE": 44,
            "nH": 28,
            "LB": 800,
            "UB": 10**6,
            "Capex": 500,
            "Opex": 15,
        },
        "Solar PV": {"nE": 9, "nH": 0, "LB": 10, "UB": 300, "Capex": 2000, "Opex": 500},
        "Wind Farm": {
            "nE": 22,
            "nH": 0,
            "LB": 10,
            "UB": 500,
            "Capex": 2000,
            "Opex": 1200,
        },
    }

    m.st = Process(label="Biomass ST")
    _ = (
        m.st(-m.biomass)
        == (277.78 * generation_process_dict["Biomass ST"]["nE"] / 100) * m.power
        + m.co2_vent * co2_factors["Biomass"]
    )
    # using x sets a binary, making the setting up of the process optional
    _ = m.st.capacity.x >= generation_process_dict["Biomass ST"]["LB"]
    _ = m.st.capacity.x <= generation_process_dict["Biomass ST"]["UB"]
    _ = (
        m.st.capacity[m.usd.spend]
        == generation_process_dict["Biomass ST"]["Capex"] * 0.05
    )
    _ = m.st.operate[m.usd.spend] == generation_process_dict["Biomass ST"]["Opex"]

    m.chp = Process(label="Biomass ST")
    _ = (
        m.chp(-m.ng)
        == (277.78 * generation_process_dict["Natural Gas CHP"]["nE"] / 100) * m.power
        + (277.78 * generation_process_dict["Natural Gas CHP"]["nH"] / 100) * m.heat
        + m.co2_vent * co2_factors["Natural Gas"]
    )
    # using x sets a binary, making the setting up of the process optional
    _ = m.chp.capacity.x >= generation_process_dict["Natural Gas CHP"]["LB"]
    _ = m.chp.capacity.x <= generation_process_dict["Natural Gas CHP"]["UB"]
    _ = (
        m.chp.capacity[m.usd.spend]
        == generation_process_dict["Natural Gas CHP"]["Capex"] * 0.05
    )
    _ = m.chp.operate[m.usd.spend] == generation_process_dict["Natural Gas CHP"]["Opex"]

    m.pv = Process(label="Solar PV")
    _ = (
        m.pv(-m.solar)
        == (277.78 * generation_process_dict["Solar PV"]["nE"] / 100) * m.power
    )
    _ = m.pv.capacity.x <= generation_process_dict["Solar PV"]["UB"]
    _ = m.pv.capacity.x >= generation_process_dict["Solar PV"]["LB"]
    _ = (
        m.pv.capacity[m.usd.spend]
        == generation_process_dict["Solar PV"]["Capex"] * 0.05
    )
    _ = m.pv.operate[m.usd.spend] == generation_process_dict["Solar PV"]["Opex"]

    m.wf = Process(label="Wind Farm")
    _ = (
        m.wf(-m.wind)
        == (277.78 * generation_process_dict["Wind Farm"]["nE"] / 100) * m.power
    )
    _ = m.wf.capacity.x <= generation_process_dict["Wind Farm"]["UB"]
    _ = m.wf.capacity.x >= generation_process_dict["Wind Farm"]["LB"]
    _ = (
        m.wf.capacity[m.usd.spend]
        == generation_process_dict["Wind Farm"]["Capex"] * 0.05
    )
    _ = m.wf.operate[m.usd.spend] == generation_process_dict["Wind Farm"]["Opex"]

    m.grid = Process(label="Grid Electricity")
    _ = (
        m.grid(-m.gridpower)
        == 277.78 * m.power + m.co2_vent * co2_factors["Grid Electricity"]
    )
    _ = m.grid.capacity <= 10**5  # no binary needed because no upper bound


def _supermarket_consumption(m):
    """Bind the refrigerator, lights, and heater to their end uses."""
    consumption_process_dict = {
        "Refrigeration": {"Efficiency": 300, "Capex": 80, "Opex": 85},
        "LED": {"Efficiency": 70, "Capex": 10, "Opex": 30},
        "Heating": {"Efficiency": 4, "Capex": 1, "Opex": 3},
    }

    m.refrigerator = Process(label="Refrigerator")
    _ = m.refrigerator.capacity <= 10**5
    _ = (
        m.refrigerator(-m.power)
        == (consumption_process_dict["Refrigeration"]["Efficiency"] / 100)
        * m.refrigeration
    )
    _ = (
        m.refrigerator.capacity[m.usd.spend]
        == consumption_process_dict["Refrigeration"]["Capex"] * 0.05
    )
    _ = (
        m.refrigerator.operate[m.usd.spend]
        == consumption_process_dict["Refrigeration"]["Opex"]
    )

    m.led = Process(label="LED")
    _ = (
        m.led(-m.power)
        == (consumption_process_dict["LED"]["Efficiency"] / 100) * m.lighting
    )
    _ = m.led.capacity[m.usd.spend] == consumption_process_dict["LED"]["Capex"] * 0.05
    _ = m.led.operate[m.usd.spend] == consumption_process_dict["LED"]["Opex"]

    m.heater = Process(label="Heater")
    _ = (
        m.heater(-m.heat)
        == (consumption_process_dict["Heating"]["Efficiency"] / 100) * m.heating
    )
    _ = (
        m.heater.capacity[m.usd.spend]
        == consumption_process_dict["Heating"]["Capex"] * 0.05
    )
    _ = m.heater.operate[m.usd.spend] == consumption_process_dict["Heating"]["Opex"]
