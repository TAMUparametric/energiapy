# energiapy

[![Documentation Status](https://readthedocs.org/projects/energiapy/badge/)](https://energiapy.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/energiapy.svg)](https://pypi.org/project/energiapy)
[![Downloads](https://static.pepy.tech/personalized-badge/energiapy?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads)](https://pepy.tech/project/energiapy)


energiapy is a tool for the multiscale modeling and optimization of energy systems. energiapy uses a resource task network (RTN) based approach to formulate mathematical programs as pyomo instances. Models can be solved using solvers, and the results can be analyzed within the energiapy framework. 
Constituent functionalities have been built over the research conducted by the [Multiparameteric Optimization and Control (Pistikopoulos) Group](https://parametric.tamu.edu/).


## Installation

energiapy can be installed using the standard pip installation. It is recommended to install the package in a separate conda or pip environment. 

Create and activate a conda environment 

    conda create --name energiaenv python=3.10
    conda activate energiaenv

Or, create and activate a pip environment 

    python3.10 -m venv energiaenv
    .\energiaenv\Scripts\activate

Install energiapy

    pip install energiapy

energiapy is being developed as a PhD project, and is hence frequently updated. For the most updated (sometimes unstable) version use

    pip install git+https://github.com/TAMUparametric/energiapy

## Key Applications

1. Design of future energy systems (network design)
2. Scheduling under uncertainty
3. Life-cycle and environmental impact assessment
4. Techno-economic analysis 
5. System resiliency and reliability characterization

Models can also simultaneously assuage the above under an integrated paradigm.

## Modeling Approach

Model components are declared as energiapy objects. The suggested hierarchy is as follows:


![alt text](https://github.com/TAMUparametric/energiapy/blob/main/docs/hierarchy.png?raw=true)

1. **Temporal_scale:** The multiple temporal scales being considered
2. **Resource:** Resources can be in any quantifiable form such mass, energy, information
3. **Material:** Infrastructural materials are required for establishing tasks, and require resources if produced 
4. **Process:** Tasks/processes are set up by utilizing materials, and convert resources from on form to the other.
5. **Location:** Locations are essentially a set of process. Capacity, cost, and demand variability can also be introduced.
6. **Transport:** Modes of transportation translocate resources. Materials usage can also be provided.
7. **Network:** Networks connect locations using transport linkages. The distance and transport availability matrices need to be provided. 
8. **Scenario:** single location (using Location) or multi-location (using Network) scenarios can be generated at appropriate scales.

Scenarios can then be formulated as a pyomo instance with the formulate function by using a set of constraints, setting an objective, providing demand targets, etc. Sets and variables are defined implicitly. Bespoke constraints can be added using the pyomo syntax. The solve functionality using appropriate solvers provides a solution (Result), which can be exported, analyzed, or itself used to initialize models. 

## Select Features

Available constraints are able to model:

1. network design (using binaries)
2. resource flows
3. inventory balance
4. costing
5. emission (using global warming potential)
6. land use
7. mode based production (multiple resource inputs, nonlinear behavior modeling using piece-wise linear curves)
8. transportation
9. failure rates

A model can be optimized towards:

1. minimizing cost
2. minimizing emission
3. maximizing resource discharge

Large scenarios can be aggregated using the following available techniques:

1. agglomerative hierarchial clustering (AHC)
2. dynamic time warping (DTW)

Both the input data and solution output can be plotted with energiapy's own plot module:

1. input data: capacity, demand, cost factors
2. solution output: inventory, production, consumption, discharge/sales schedule; contribution towards costs (capital, variable and fixed operational), meeting demand.

Other (and optional) features include:

1. math utilities for calculating euclidean distances, generation connectivity matrices, etc.
2. generating dataframes with missing data fixed (weekends, public holidays) for time-series data such as resource price
3. function to fetch weather data at an appropriate resolution from [NREL NSRDB](https://nsrdb.nrel.gov/) for any county in the US
4. latex constraints writer for model documentation



