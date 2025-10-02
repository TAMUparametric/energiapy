<p align="center">
  <img src="https://github.com/TAMUparametric/energiapy/raw/main/docs/_static/logo2.jpg" width="75%">
</p>


[![Documentation Status](https://readthedocs.org/projects/energiapy/badge/)](https://energiapy.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/energiapy.svg)](https://pypi.org/project/energiapy)
[![Downloads](https://static.pepy.tech/personalized-badge/energiapy?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads)](https://pepy.tech/project/energiapy)
[![Python package](https://github.com/TAMUparametric/energiapy/actions/workflows/python-package.yml/badge.svg)](https://github.com/TAMUparametric/energiapy/actions/workflows/python-package.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/994d46ab40ac4f0ead5ed9d1ea1b0fab)](https://app.codacy.com/gh/TAMUparametric/energiapy/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

Energia is a tool for the data-driven multiscale modeling and optimization of energy systems under uncertainty. Users are directed to {cite}`kakodkar2022review` for an overview of the state-of-the-art in the field.
The component-driven methodology is inspired by the resource task network (RTN) methodology {cite}`barbosa_povoa_pantelides_1997` and constituent functionalities developed through the research conducted in
the [Multiparameteric Optimization and Control (Pistikopoulos) Group](https://parametric.tamu.edu/). The Tutorials and Examples sections are a good starting point.


:::{seealso}
[Gana](https://gana.readthedocs.io/en/latest/), an Algebraic Modeling Language (AML) for Multiscale Modeling and Optimization which serves as the backend
:::




# Components

```Model``` is the primary central object which aggregate components based on a broader
perspective of what they describe, namely Scope (```Time```, ```Space```), ```System``` , ```Consequence```, ```Problem```. 


**Scope** which defines the extent of the system under consideration, and the fidelity of data. 

1. ```Time```, with ```Periods``` and ```TemporalScales``` defining the discretization
2. ```Space```, with ```Location``` and ```Linkage``` serving as nodes and edges 

The most sparsely discretized ```Periods``` serves as the temporal ```horizon```, and the most encompassing ```Location``` (which are nested) is the ```network```

**Streams** which scale the domains of the system via operations.

3. ```Commodity``` which includes ```Resource```, and subsets ```Currency```, ```Land```, ```Emission```, ```Material```, etc.
4. ```Indicator``` categories such as ```Environ```, ```Social```, and ```Economic```

```Commodity```  streams belong to ```System```, whereas ```Indicators``` inform the ```Consequence```.

**Operational** components, decisions pertaining to which generate and direct ```Commodity``` streams. 

5. ```Process``` for commodity conversion
6. ```Transport``` to import and export certain commodities
7. ```Storage``` to charge and discharge inventory

```Storage``` is actually a combination of two ```Process``` objects (for charging and discharging) and ```Inventory``` space. 

**Game** components suggest ownership and strategic interactions between independent actors.

8. ```Player``` is an independent actor
9. ```Couple``` represents a link between two ```Player```s

**Aspect**s are the facets being modeled.

These generate variables:

10. ```State``` (in Energia) are restricted to operational conditions
11. ```Control``` or decision variables 
12. ```Stream```, also a ```State``` that quantify ```Commodity``` streams 
13. ```Impact``` which quantify ```Indicator``` streams 
14. ```Loss```, a general variable to describe loss and (or) degradation 

Note that users can choose to model sans ```Control``` variables and model ```State``` directly. 

**Constraints** 

Data provided either:

15. ```Bind``` or restrict any given ```Aspect```
or
16. ```Calculate``` a dependent ```Aspect``` such as  ```Stream```, ```Impact```, or ```Loss```  

Consistency is maintained by generating implicit constraints:

17. ```Balance``` for general resource balance 
and
18. ```Map``` to scale and sum streams across spatiotemporal domains

**Parameters**

No special parameter types exist of bind and calculations. However,:

19. ```Conversion``` serves as general parameter that dictates conversion efficiency and material use for setup

**Disposition** describes both the fidelity and specificity of a modeling element.

20. ```Domain``` is an ordered index set 

**Objectives**

Multiple objectives can be provided. Infact the lower and upperbounds of any ```Aspect``` with regards to a specific component within some spatiotemporal context 
can be determined. 


<!-- ![alt text](https://github.com/TAMUparametric/energiapy/blob/main/docs/hierarchy.png?raw=true) -->



# Application

Models can also simultaneously perform the following analyses under an integrated paradigm:

- Multiperiod Multiscale Design and Scheduling {cite}`kakodkar2023hydrogen,kakodkar2024multiperiod`
- Modeling the Material-Energy-Mobility Nexus {cite}`montano2025modeling,flores2025integrating`
- Carbon Accounting and Life Cycle Assessment Under Uncertainty {cite}`sousa2025integrating,de2025integrated`
- Robust Scheduling Using Multiparametric Programming {cite}`kakodkar2024robust`
- Resilience Analysis of Distributed Energy and Manufacturing Systems {cite}`vedant2024information`


# Select Features

Available constraints are able to model:

1. network design (with discrete choice)
2. resource flows
3. inventory balance
4. emission and costing calculations
5. environmental, social, and economic impact
6. material and land use for infrastructure development
7. nonlinear behavior modeling using piece-wise linear curves
8. transportation
9. failure and loss

Examples of objectives towards which the model can be optimized include:

1. minimizing cost
2. minimizing impact
3. maximizing resource discharge

Large scenarios can be aggregated using the following available techniques:

1. agglomerative hierarchial clustering (AHC)
2. dynamic time warping (DTW)

Both the input data and solution output can be illustrated, examples include:

1. input data: capacity, demand, cost factors
2. solution output: inventory, production, consumption, discharge/sales schedule; contribution towards costs (capital,
   variable and fixed operational), meeting demand.

Other (and optional) features include:

1. math utilities for calculating euclidean distances, generation connectivity matrices, etc.
2. generating dataframes with missing data fixed (weekends, public holidays) for time-series data such as resource price
3. function to fetch weather data at an appropriate resolution from [NREL NSRDB](https://nsrdb.nrel.gov/) for any county
   in the US
4. latex constraints writer for model documentation

Direct any communication to Rahul Kakodkar (cacodcar@gmail.com) 

# References
```{bibliography}
