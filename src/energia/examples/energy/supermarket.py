"""Supermarket energy system example."""

from ...represent.model import Model
from ...components.commodity.resource import Resource
from ...components.commodity.misc import Cash
from ...components.operation.process import Process
from ...components.measure.unit import Unit
from ...components.spatial.location import Location


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

    m.usd = Cash(label='$')

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

    m.usd.spend.opt()

    m.co2_vent.release.opt()

    m._.lb(sum(m._.consume))
