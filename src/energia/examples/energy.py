"""Energy system examples"""

from ..components.commodity.misc import Currency
from ..components.commodity.resource import Resource
from ..components.operation.process import Process
from ..components.temporal.periods import Periods
from ..represent.model import Model
from ..components.operation.storage import Storage
from ..components.temporal.scales import TemporalScales
from ..components.impact.categories import Environ
from ..components.commodity.misc import Material
from ..components.spatial.location import Location
from ..components.measure.unit import Unit


def scheduling():
    """A small scheduling example"""
    m = Model('scheduling')

    # ## Time
    #
    # We have 4 quarter which form a year

    m.q = Periods()
    m.y = 4 * m.q

    # The horizon ($\overset{\ast}{t} = argmin_{n \in N} |\mathcal{T}_{n}|$) is determined by Energia implicitly. Check it by printing Model.Horizon

    m.horizon

    # ## Space
    #
    # If nothing is provided, a default location is created. The created single location will serve as the de facto network
    #
    # In single location case studies, it may be easier to skip providing a location all together

    m.network

    # ## Resources
    #
    # In the Resource Task Network (RTN) methodology all commodities are resources. In this case, we have a few general resources (wind, power) and a monetary resource (USD).

    m.usd = Currency()
    m.power, m.wind = Resource(), Resource()

    # ### Setting Bounds
    #
    # The first bound is set for over the network and year, given that no spatiotemporal disposition is provided:
    #
    # $\mathbf{cons}_{wind, network, year_0} \leq 400$
    #
    # For the second bound, given that a nominal is given, the list is treated as multiplicative factor. The length matches with the quarterly scale. Thus:
    #
    # $\mathbf{rlse}_{power, network, quarter_0} \geq 60$
    #
    # $\mathbf{rlse}_{power, network, quarter_1} \geq 70$
    #
    # $\mathbf{rlse}_{power, network, quarter_2} \geq 100$
    #
    # $\mathbf{rlse}_{power, network, quarter_3} \geq 30$
    #

    m.wind.consume <= 400
    m.power.release.prep(100) >= [0.6, 0.7, 1, 0.3]

    # Check the model anytime, using m.show(), or object.show()
    #
    # The first constraint is a general resource balance, generated for every resource at every spatiotemporal disposition at which an aspect regarding it is defined.
    #
    # Skip the True in .show() for a more concise set notation based print

    # ## Process

    # There are multiple ways to model this.
    #
    # Whats most important, however, is the resource balance. The resource in the brackets is the basis resource. For a negative basis, multiply the resource by the negative factor or just use negation if that applies.

    m.wf = Process()
    m.wf(m.power) == -1 * m.wind

    # Now set bounds on the extent to which the wind farm can operate. We are actually writing the following constraint:
    #
    # $\mathbf{opr} <= \phi \cdot \mathbf{cap}$
    #
    # However, we know the capacity, so it is treated as a parameter.
    #
    # Note that the incoming values are normalized by default. Use norm = False to avoid that

    m.wf.operate.prep(200, norm=False) <= [0.9, 0.8, 0.5, 0.7]

    # Add a cost to the process operation. This implies that the cost of operating is variable in every quarter. In general:
    #
    # $\dot{\mathbf{v}} == \theta \cdot \mathbf{v}$

    m.wf.operate[m.usd.spend] == [4000, 4200, 4300, 3900]

    # Note that printing can be achieved via the aspect [operate, spend, etc.] or the object

    # ## Locating the process
    #
    # The production streams are only generated once the process is places in some location. In this study, the only location is available is the default network.

    m.network.locate(m.wf)

    # Alternatively,

    # m.wf.locate(m.network)

    # # The Model
    #
    # The model consists of the following:
    #
    # 1. A general resource balances for wind in (network, year) and power in (network, quarter)
    # 2. Bounds on wind consumption [upper] and power release [lower], and wf operation [upper]
    # 3. Conversion constraints, giving produced and expended resources based on operation
    # 4. Calculation of spending USD in every quarter
    # 5. Mapping constraints for operate: q -> y and spend: q -> y (generated after objective is set)

    return m


def design_scheduling():
    """A small design and scheduling example"""
    m = Model('design_scheduling')
    m.q = Periods()
    m.y = 4 * m.q
    m.usd = Currency()
    m.declare(Resource, ['power', 'wind', 'solar'])
    m.solar.consume(m.q) <= 100
    m.wind.consume <= 400
    m.power.release.prep(180) >= [0.6, 0.7, 0.8, 0.3]

    m.wf = Process()
    m.wf(m.power) == -1 * m.wind
    m.wf.capacity.x <= 100
    m.wf.capacity.x >= 10
    m.wf.operate.prep(norm=True) <= [0.9, 0.8, 0.5, 0.7]
    m.wf.capacity[m.usd.spend] == 990637 + 3354
    m.wf.operate[m.usd.spend] == 49

    m.pv = Process()
    m.pv(m.power) == -1 * m.solar
    m.pv.capacity.x <= 100
    m.pv.capacity.x >= 10
    m.pv.operate.prep(norm=True) <= [0.6, 0.8, 0.9, 0.7]
    m.pv.capacity[m.usd.spend] == 567000 + 872046
    m.pv.operate[m.usd.spend] == 90000

    m.lii = Storage()
    m.lii(m.power) == 1 / 0.9
    m.lii.capacity.x <= 100
    m.lii.capacity.x >= 10
    m.lii.capacity[m.usd.spend] == 1302182 + 41432
    m.lii.inventory[m.usd.spend] == 2000

    m.network.locate(m.wf, m.pv, m.lii)

    return m


def design_scheduling_materials():
    """Design and scheduling considering materials and emissions from them"""
    m = Model('design_scheduling')
    m.scales = TemporalScales([1, 4], ['y', 'q'])
    m.usd = Currency()
    m.gwp = Environ()

    m.declare(Resource, ['power', 'wind', 'solar'])
    m.solar.consume == True
    m.wind.consume == True
    m.power.release.prep(180) >= [0.6, 0.7, 0.8, 0.3]

    m.declare(
        Material,
        [
            'lir',
            'lib',
            'steel',
            'concrete',
            'glass',
            'si_mono',
            'si_poly',
        ],
    )

    m.lir.consume[m.gwp.emit] == 9600
    m.lib.consume[m.gwp.emit] == 2800
    m.steel.consume[m.gwp.emit] == 2121.152427
    m.steel.consume[m.usd.spend] == 670

    m.concrete.consume[m.gwp.emit] == 120.0378
    m.glass.consume[m.gwp.emit] == 1118.5
    m.si_mono.consume[m.gwp.emit] == 122239.1
    m.si_poly.consume[m.gwp.emit] == 98646.7

    m.wf = Process()
    m.wf.fab[0] == 109.9 * m.steel + 398.7 * m.concrete
    m.wf.fab[1] == 249.605 * m.steel + 12.4 * m.concrete
    m.wf(m.power) == {
        m.wf.fab.modes[0]: -2.857 * m.wind,
        m.wf.fab.modes[1]: -2.3255 * m.wind,
    }
    m.wf.capacity.x <= 100
    m.wf.capacity.x >= 10
    m.wf.operate.prep(norm=True) <= [0.9, 0.8, 0.5, 0.7]
    m.wf.capacity(m.wf.fab.modes)[m.usd.spend] == [1292000 + 29200, 3192734 + 101498]
    m.wf.operate[m.usd.spend] == 49

    m.pv = Process()
    m.pv.fab[0] == 70 * m.glass + 7 * m.si_mono
    m.pv.fab[1] == 70 * m.glass + 7 * m.si_poly
    m.pv(m.power) == {
        m.pv.fab.modes[0]: -5 * m.solar,
        m.pv.fab.modes[1]: -6.67 * m.solar,
    }
    m.pv.capacity.x <= 100
    m.pv.capacity.x >= 10
    m.pv.operate.prep(norm=True) <= [0.6, 0.8, 0.9, 0.7]
    m.pv.capacity[m.usd.spend] == 567000 + 872046
    m.pv.operate[m.usd.spend] == 90000

    m.lii = Storage()
    m.lii(m.power) == 1 / 0.9
    m.lii.fab[0] == 0.137 * m.lib + 1.165 * m.steel
    m.lii.fab[1] == 0.137 * m.lir + 1.165 * m.steel
    m.lii.capacity.x <= 100
    m.lii.capacity.x >= 10
    m.lii.capacity[m.usd.spend] == 1302182 + 41432
    m.lii.inventory[m.usd.spend] == 2000

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
    resource_demand_dict = {
        'Lighting': 200,
        'Refrigeration': 1000,
        'Space Heating': 100,
    }

    resource_dict = {
        'Price': {'Natural Gas': 8.89, 'Biomass': 9.72, 'Grid Electricity': 36.11},
        'CO2 Generation': {'Natural Gas': 56, 'Biomass': 100, 'Grid Electricity': 90},
    }

    generation_process_dict = {
        'Biomass ST': {
            'nE': 68,
            'nH': 0,
            'LB': 100,
            'UB': 10**6,
            'Capex': 250,
            'Opex': 15,
        },
        'Natural Gas CHP': {
            'nE': 44,
            'nH': 28,
            'LB': 800,
            'UB': 10**6,
            'Capex': 500,
            'Opex': 15,
        },
        'Solar PV': {'nE': 9, 'nH': 0, 'LB': 10, 'UB': 300, 'Capex': 2000, 'Opex': 500},
        'Wind Farm': {
            'nE': 22,
            'nH': 0,
            'LB': 10,
            'UB': 500,
            'Capex': 2000,
            'Opex': 1200,
        },
    }

    consumption_process_dict = {
        'Refrigeration': {'Efficiency': 300, 'Capex': 80, 'Opex': 85},
        'LED': {'Efficiency': 70, 'Capex': 10, 'Opex': 30},
        'Heating': {'Efficiency': 4, 'Capex': 1, 'Opex': 3},
    }

    m = Model('supermarket')

    m.supermarket = Location()

    m.GJ = Unit(label='Giga Joules')
    m.PJ = 10**6 * m.GJ
    m.kW = Unit(label='kilo Watts')
    m.tons = Unit(label='US Tons')

    # Resources can be declared along with thier attributes such as maximum allowed consumption, dischargeablity, base price, etc.

    m.usd = Currency(label='$')

    m.biomass = Resource(basis=m.GJ, label='Biomass')
    m.biomass.consume == True
    m.biomass.consume[m.usd.spend] == resource_dict['Price']['Biomass']

    m.gridpower = Resource(basis=m.GJ, label='Grid Electricity')
    m.gridpower.consume == True
    m.gridpower.consume[m.usd.spend] == resource_dict['Price']['Grid Electricity']

    m.ng = Resource(basis=m.GJ, label='Natural gas')
    m.ng.consume == True
    m.ng.consume[m.usd.spend] == resource_dict['Price']['Natural Gas']

    m.power = Resource(basis=m.kW, label='Electrical Power')
    m.heat = Resource(basis=m.kW, label='Heat Power')

    m.co2_vent = Resource(basis=m.tons, label='Carbon dioxide')
    m.co2_vent.release == True

    m.solar = Resource(basis=m.GJ, label='Solar energy')
    m.solar.consume == True
    m.wind = Resource(basis=m.GJ, label='Wind energy')
    m.wind.consume == True

    m.lighting = Resource(basis=m.kW, label='Lighting')
    m.lighting.release >= resource_demand_dict['Lighting']

    m.refrigeration = Resource(basis=m.kW, label='Refrigeration')
    m.refrigeration.release >= resource_demand_dict['Refrigeration']

    m.heating = Resource(basis=m.kW, label='Heating')
    m.heating.release >= resource_demand_dict['Space Heating']

    m.st = Process(basis=m.PJ, label='Biomass ST')
    m.st(-m.biomass) == (
        277.78 * generation_process_dict['Biomass ST']['nE'] / 100
    ) * m.power + m.co2_vent * resource_dict['CO2 Generation']['Biomass']
    # using x sets a binary, making the setting up of the process optional
    m.st.capacity.x >= generation_process_dict['Biomass ST']['LB']
    m.st.capacity.x <= generation_process_dict['Biomass ST']['UB']
    m.st.capacity[m.usd.spend] == generation_process_dict['Biomass ST']['Capex'] * 0.05
    m.st.operate[m.usd.spend] == generation_process_dict['Biomass ST']['Opex']

    m.chp = Process(basis=m.PJ, label='Biomass ST')
    m.chp(-m.ng) == (
        277.78 * generation_process_dict['Natural Gas CHP']['nE'] / 100
    ) * m.power + (
        277.78 * generation_process_dict['Natural Gas CHP']['nH'] / 100
    ) * m.heat + m.co2_vent * resource_dict[
        'CO2 Generation'
    ][
        'Natural Gas'
    ]
    # using x sets a binary, making the setting up of the process optional
    m.chp.capacity.x >= generation_process_dict['Natural Gas CHP']['LB']
    m.chp.capacity.x <= generation_process_dict['Natural Gas CHP']['UB']
    m.chp.capacity[m.usd.spend] == generation_process_dict['Natural Gas CHP'][
        'Capex'
    ] * 0.05
    m.chp.operate[m.usd.spend] == generation_process_dict['Natural Gas CHP']['Opex']

    m.pv = Process(basis=m.kW, label='Solar PV')
    m.pv(-m.solar) == (
        277.78 * generation_process_dict['Solar PV']['nE'] / 100
    ) * m.power
    m.pv.capacity.x <= generation_process_dict['Solar PV']['UB']
    m.pv.capacity.x >= generation_process_dict['Solar PV']['LB']
    m.pv.capacity[m.usd.spend] == generation_process_dict['Solar PV']['Capex'] * 0.05
    m.pv.operate[m.usd.spend] == generation_process_dict['Solar PV']['Opex']

    m.wf = Process(basis=m.kW, label='Wind Farm')
    m.wf(-m.wind) == (
        277.78 * generation_process_dict['Wind Farm']['nE'] / 100
    ) * m.power
    m.wf.capacity.x <= generation_process_dict['Wind Farm']['UB']
    m.wf.capacity.x >= generation_process_dict['Wind Farm']['LB']
    m.wf.capacity[m.usd.spend] == generation_process_dict['Wind Farm']['Capex'] * 0.05
    m.wf.operate[m.usd.spend] == generation_process_dict['Wind Farm']['Opex']

    m.grid = Process(basis=m.PJ, label='Grid Electricity')
    m.grid(-m.gridpower) == 277.78 * m.power + m.co2_vent * resource_dict[
        'CO2 Generation'
    ]['Grid Electricity']
    m.grid.capacity <= 10**5  # no binary needed because no upper bound

    m.refrigerator = Process(basis=m.kW, label='Refrigerator')
    m.refrigerator.capacity <= 10**5
    m.refrigerator(-m.power) == (
        consumption_process_dict['Refrigeration']['Efficiency'] / 100
    ) * m.refrigeration
    m.refrigerator.capacity[m.usd.spend] == consumption_process_dict['Refrigeration'][
        'Capex'
    ] * 0.05
    m.refrigerator.operate[m.usd.spend] == consumption_process_dict['Refrigeration'][
        'Opex'
    ]

    m.led = Process(basis=m.kW, label='LED')
    m.led(-m.power) == (
        consumption_process_dict['LED']['Efficiency'] / 100
    ) * m.lighting
    m.led.capacity[m.usd.spend] == consumption_process_dict['LED']['Capex'] * 0.05
    m.led.operate[m.usd.spend] == consumption_process_dict['LED']['Opex']

    m.heater = Process(basis=m.kW, label='Heater')
    m.heater(-m.heat) == (
        consumption_process_dict['Heating']['Efficiency'] / 100
    ) * m.heating
    m.heater.capacity[m.usd.spend] == consumption_process_dict['Heating'][
        'Capex'
    ] * 0.05
    m.heater.operate[m.usd.spend] == consumption_process_dict['Heating']['Opex']

    # Locations serve as aggregations of scenarios

    m.supermarket.locate(
        m.st, m.chp, m.pv, m.wf, m.grid, m.refrigerator, m.led, m.heater
    )

    # Various constraints are need for the formulating the mathematical programming model. Here we include the cost, production, resource balance, demand, inventory, and network constraints.

    return m
