#!/usr/bin/env python
# coding: utf-8

# # Supermarket

# ## Problem Statement

# Given is a supermarket comprising of on-site energy conversion blocks and energy demands. The expected operating horizon of the supermarket is 20 years. The energy demands are listed in Table 1.
#
#
# |               | Lighting | Refrigeration | Space Heating |
# |---------------|----------|---------------|---------------|
# | Demand [kW]   | 200      | 1000          |100            |

# Primary energy resources include natural gas and biomass. Prices of the primary energy resources and grid electricity as well as their associated CO2 production is given in Table 2 – it should be noted that 1 [GJ] is approximately equal to 277.78 [KWh].
#
# |                    | Natural Gas | Biomass | Grid Electricity |
# |--------------------|-------------|---------|------------------|
# | Price [\$/GJ]      | 8.89        | 9.72    |36.11             |
# | CO$_2$ gen. [kg/PJ]| 56          | 100     | 90               |
#

# The on-site energy generation section involves two electricity generation technologies, one heat generation technology, and one co-production technology. The electrical efficiency (ηE), heating efficiency (ηH), minimum capacity if constructed (LB), maximum capacity if constructed (UB), capital cost (CAPEX), and operational cost (OPEX) are give in Table 3. Table 3: Technical and economic parameters of on-site energy generation technologies
#
# | Process            | ηE [%] | ηH [%] | LB [kW] | UB [kW] | Capex [$/kW] | Opex [$/ (kW·year)] |
# |--------------------|--------|--------|---------|---------|--------------|---------------------|
# | Biomass ST         |   68   |   0    |   100   | 10⁶     |    250       |        15           |
# | Natural Gas CHP    |   44   |  28    |   800   | 10⁶     |    500       |        15           |
# | Solar PV           |    9   |   0    |    10   |  300    |   2000       |       500           |
# | Wind Farm          |   22   |   0    |    10   |  500    |   2000       |      1200           |
#

# Two electricity driven energy conversion technologies and one heat driven energy conversion technologies is given in order to meet the demands of lighting, refrigeration, and space heating. The efficiency (or coefficient of performance, COP), types of energy input, types of utility output, capital cost and operational cost of these technologies are summarized in Table 4.
#
# |                      | Refrigeration      | LED         | Heating      |
# |----------------------|--------------------|-------------|--------------|
# | **Input [-]**        | Electricity        | Electricity | Heating      |
# | **Output [-]**       | Refrigeration      | Lighting    | Space Heating|
# | **Efficiency [%]**   | 300 (COP)          | 80          | 85           |
# | **Capex [$/kW]**     | 70                 | 10          | 30           |
# | **Opex [$/kW·year]** | 4                  | 1           | 3            |
#

# Determine system configurations for optimal cost, energy efficiency, and emission

# ## Import modules

# In[1]:


from energia import *

# ## Parameters

# In[2]:


resource_demand_dict = {
    'Lighting': [100, 200],
    'Refrigeration': [550, 1000],
    'Space Heating': [100, 200],
}

resource_dict = {
    'Price': {'Natural Gas': 8.89, 'Biomass': 9.72, 'Grid Electricity': 36.11},
    'CO2 Generation': {'Natural Gas': 56, 'Biomass': 100, 'Grid Electricity': 90},
}

generation_process_dict = {
    'Biomass ST': {'nE': 68, 'nH': 0, 'LB': 100, 'UB': 10**6, 'Capex': 250, 'Opex': 15},
    'Natural Gas CHP': {
        'nE': 44,
        'nH': 28,
        'LB': 800,
        'UB': 10**6,
        'Capex': 500,
        'Opex': 15,
    },
    'Solar PV': {'nE': 9, 'nH': 0, 'LB': 10, 'UB': 300, 'Capex': 2000, 'Opex': 500},
    'Wind Farm': {'nE': 22, 'nH': 0, 'LB': 10, 'UB': 500, 'Capex': 2000, 'Opex': 1200},
}

consumption_process_dict = {
    'Refrigeration': {'Efficiency': 300, 'Capex': 80, 'Opex': 85},
    'LED': {'Efficiency': 70, 'Capex': 10, 'Opex': 30},
    'Heating': {'Efficiency': 4, 'Capex': 1, 'Opex': 3},
}


# ## Model

# Declare the model

# In[3]:


m = Model('supermarket')

m.y10 = Periods(label='10 years')
m.y20 = 2 * m.y10


# ## Spatiotemporal Disposition

# We will conside a single temporal scale representing the 20 year horizon with no discretization. The only location being considered is the Supermarket
# It is <u>not</u> required. However, declaring one allows us to label the location.

# In[4]:


m.supermarket = Location()


# ## Units

# In[5]:


m.GJ = Unit(label='Giga Joules')
m.PJ = 10**6 * m.GJ
m.kW = Unit(label='kilo Watts')
m.tons = Unit(label='US Tons')


# ## Resources

# Resources can be declared along with thier attributes such as maximum allowed consumption, dischargeablity, base price, etc.

# In[6]:


m.usd = Currency(label='$')


# In[7]:


m.biomass = Resource(basis=m.GJ, label='Biomass')
m.biomass.consume == True
m.biomass.consume[m.usd.spend] == resource_dict['Price']['Biomass']


# ### Display the program

# show(True) will print constraints at every index

# In[8]:


m.show()


# In[9]:


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


# In[10]:


m.show()


# ## Processes

# Processes convert one resource to another with a particular conversion efficiency while incurring a cost for setup (capital expenditure) and operation (operational expenditure)

# In[11]:


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
m.pv(-m.solar) == (277.78 * generation_process_dict['Solar PV']['nE'] / 100) * m.power
m.pv.capacity.x <= generation_process_dict['Solar PV']['UB']
m.pv.capacity.x >= generation_process_dict['Solar PV']['LB']
m.pv.capacity[m.usd.spend] == generation_process_dict['Solar PV']['Capex'] * 0.05
m.pv.operate[m.usd.spend] == generation_process_dict['Solar PV']['Opex']


m.wf = Process(basis=m.kW, label='Wind Farm')
m.wf(-m.wind) == (277.78 * generation_process_dict['Wind Farm']['nE'] / 100) * m.power
m.wf.capacity.x <= generation_process_dict['Wind Farm']['UB']
m.wf.capacity.x >= generation_process_dict['Wind Farm']['LB']
m.wf.capacity[m.usd.spend] == generation_process_dict['Wind Farm']['Capex'] * 0.05
m.wf.operate[m.usd.spend] == generation_process_dict['Wind Farm']['Opex']

m.grid = Process(basis=m.PJ, label='Grid Electricity')
m.grid(-m.gridpower) == 277.78 * m.power + m.co2_vent * resource_dict['CO2 Generation'][
    'Grid Electricity'
]
m.grid.capacity <= 10**5  # no binary needed because no upper bound


# In[12]:


m.show(True)


# In[13]:


m.program.cons_int_cut = m.grid.capacity.X() + m.wf.capacity.X() == 1


# In[14]:


m.show(True)


# In[15]:


m.show()


# In[16]:


m.refrigerator = Process(basis=m.kW, label='Refrigerator')
m.refrigerator.capacity <= 10**5
m.refrigerator(-m.power) == (
    consumption_process_dict['Refrigeration']['Efficiency'] / 100
) * m.refrigeration
m.refrigerator.capacity[m.usd.spend] == consumption_process_dict['Refrigeration'][
    'Capex'
] * 0.05
m.refrigerator.operate[m.usd.spend] == consumption_process_dict['Refrigeration']['Opex']

m.led = Process(basis=m.kW, label='LED')
m.led(-m.power) == (consumption_process_dict['LED']['Efficiency'] / 100) * m.lighting
m.led.capacity[m.usd.spend] == consumption_process_dict['LED']['Capex'] * 0.05
m.led.operate[m.usd.spend] == consumption_process_dict['LED']['Opex']

m.heater = Process(basis=m.kW, label='Heater')
m.heater(-m.heat) == (
    consumption_process_dict['Heating']['Efficiency'] / 100
) * m.heating
m.heater.capacity[m.usd.spend] == consumption_process_dict['Heating']['Capex'] * 0.05
m.heater.operate[m.usd.spend] == consumption_process_dict['Heating']['Opex']


# ## Locate operations

# Locations serve as aggregations of scenarios

# In[17]:


m.supermarket.locate(m.st, m.chp, m.pv, m.wf, m.grid, m.refrigerator, m.led, m.heater)


# ## Formulation

# Various constraints are need for the formulating the mathematical programming model. Here we include the cost, production, resource balance, demand, inventory, and network constraints.

# In[18]:


m.show(category='Balance')


# ### Optimal Cost

# In[19]:


m.usd.spend.opt()


# In[20]:


m.show(True)


# In[21]:


m.usd.spend.output()


# In[22]:


m.show(category='Flow')


# In[23]:


m.capacity.output()


# In[24]:


m.release.output()


# In[25]:


m.operate.output()


# ### Optimal Emissions

# In[26]:


m.co2_vent.release.opt()


# ### Optimal Energy Efficiency

# In the formulation, the objective can be skipped and a bespoke objective can be introduced as shown below

# In[27]:


m._.lb(sum(m._.consume))


# In[28]:


m.solution
