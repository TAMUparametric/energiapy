Small Energy Systems MILP Example
==============================
A simple problem with three processes

- Solar PV with varying capacity factor
- Wind Farm with varying capacity factor
- Lithium-ion battery storage

and varying demand.

The problem is modeled over two scales

- 0, network scale with 1 time period
- 1, scheduling and demand scales with 4 time periods

**Import modules**

.. code-block:: python

    import pandas 
    from energiapy.components.temporal_scale import Temporal_scale
    from energiapy.components.resource import Resource
    from energiapy.components.process import Process, ProcessMode
    from energiapy.components.location import Location
    from energiapy.components.scenario import Scenario
    from energiapy.components.result import Result 
    from energiapy.model.formulate import formulate, Constraints, Objective
    from energiapy.plot import plot
    from energiapy.model.solve import solve

**Input Data**

Factors are normalized, and can be used to account for:

- variable resource demand (demand_factor)
- intermittent resource availability (capacity factor)
- varying resource purchase cost (cost factor)

.. code-block:: python

    demand_factor = pandas.DataFrame(data={'Power': [0.6, 1, 0.8, 0.3]})
    capacity_factor_pv = pandas.DataFrame(data={'PV': [0.6, 0.8, 0.9, 0.7]})
    capacity_factor_wf = pandas.DataFrame(data={'WF': [0.9, 0.8, 0.5, 0.7]})

**Declare temporal scale**

Consider four seasons in a year.

Network decisions are taken annually (scale level 0)

Scheduling decisions are taken seasonally (scale level 1)

.. code-block:: python
    
    scales = Temporal_scale(discretization_list= [1, 4])

**Declare resources**

Resources can be declared with attributes such as maximum consumption (cons_max), resource price (price), maximum allowed inventory (store_max)

As also whether they can be discharged (sell), have to meet demand (demand)

.. code-block:: python

    Solar = Resource(name='Solar', cons_max=100, basis='MW', label='Solar Power')

    Wind = Resource(name='Wind', cons_max= 100, basis='MW', label='Wind Power')

    Power = Resource(name='Power', basis='MW', demand = True, block = 'bla', label='Power generated', varying = True)

**Declare processes**

Processes consume resources and can be of three type:

- storage, if storage = some_resource 
- single mode, as with the processes defined here wherein a conversions are provided
- multi mode, if a multiconversion dict is provided

.. code-block:: python

    LiI = Process(name='LiI', storage= Power, capex = 1302182, fopex= 41432, vopex = 2000,  prod_max=100, label='Lithium-ion battery', basis = 'MW')

    WF = Process(name='WF', conversion={Wind: -1, Power: 1},capex=990637, fopex=3354, vopex=4953, prod_max=100, label='Wind mill array', varying= True, basis = 'MW')

    PV = Process(name='PV', conversion={Solar: -1, Power: 1}, capex=567000, fopex=872046, vopex=90000, prod_max=100, varying = True, label = 'Solar PV', basis = 'MW')

**Declare location**

Locations are essentially a set of processes, the required resources are collected implicitly.

Location-wise capacity, demand, and cost factors can be provided. 

The scales of the capacity and demand data need to be provided as well.

.. code-block:: python

    place = Location(name='place', processes= {LiI, PV, WF}, demand_factor = {Power: demand_factor}, capacity_factor= {PV: capacity_factor_pv, WF:capacity_factor_wf}, capacity_scale_level= 1, demand_scale_level = 1, scales=scales, label='some place')

*plot varying factors*

Plotting functions in energiapy.plot can be used to plot the factors

.. code-block:: python

    plot.capacity_factor(location= place, process= PV, fig_size= (9,5), color= 'orange')
    plot.demand_factor(location= place, resource= Power, fig_size= (9,5), color= 'red')

.. image:: capacity_factor_pv.png 

.. image:: demand_factor_pw.png 


**Declare scenario**

The combination of parameter data, locations, and transportation options generates a scenario. 

Scenarios are data sets that can be fed to models for analysis. 

In this case we are generating a scenario for the location houston. The scales need to be consistent.

The demand, network, scheduling, and expenditure scales need to be provided. They all default to 0.

.. code-block:: python

    case = Scenario(name= 'case', network= place, network_scale_level= 0, demand_scale_level = 1, scheduling_scale_level= 1, scales= scales, label= 'small scenario')

**Formulate MILP**

Models can be formulated using different constraints and objectives.

milp is a pyomo instance, additional constraints can be provided in a bespoke manner

.. code-block:: python

    milp = formulate(scenario= case, demand = 200, constraints={Constraints.cost, Constraints.inventory, Constraints.production, Constraints.resource_balance}, \
        objective= Objective.cost)

**Solve**

To solve the model, the solve requires a scenario and a modeling instance to be provided. 

Also a solver needs to be chosen.

.. code-block:: python

    results = solve(scenario = case, instance= milp, solver= 'gurobi', name=f"MILP")

**Results**

Models can be summarized as shown below:

.. code-block:: python

    results.model_summary()

*Plot results*

Some handy plotting functions such as schedule can plot the production, consumption, sales, inventory schedules. 

In the example below, the production schedule for the windfarm (WF), and the inventory levels for stored power is shown. 

.. code-block:: python

    plot.schedule(results= results, y_axis= 'P', component= 'WF', location = 'place', fig_size= (9,5), color = 'blue')
    plot.schedule(results= results, y_axis= 'Inv', component= 'Power_stored', location = 'place', fig_size= (9,5), color = 'green')

.. image:: sch_wf.png 

.. image:: sch_pow.png 


All inputs are stored in results.component

All outputs are stored in results.output

Values can be accessed as shown below

.. code-block:: python

    results.output['X_P']
    results.output['Cap_P']