<p align="center">
  <img src="https://github.com/TAMUparametric/energiapy/raw/main/docs/_static/logo2.jpg" width="75%">
</p>


[![Documentation Status](https://readthedocs.org/projects/energiapy/badge/)](https://energiapy.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/energiapy.svg)](https://pypi.org/project/energiapy)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/energiapy.svg)](https://pypi.org/project/energiapy/)
[![Downloads](https://static.pepy.tech/personalized-badge/energiapy?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads)](https://pepy.tech/project/energiapy)
[![CI](https://github.com/TAMUparametric/energiapy/actions/workflows/energia.yml/badge.svg)](https://github.com/TAMUparametric/energiapy/actions/workflows/energia.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/994d46ab40ac4f0ead5ed9d1ea1b0fab)](https://app.codacy.com/gh/TAMUparametric/energiapy/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![codecov](https://codecov.io/gh/TAMUparametric/energiapy/branch/main/graph/badge.svg)](https://codecov.io/gh/TAMUparamteric/energiapy)
[![DOI](https://zenodo.org/badge/600269309.svg)](https://doi.org/10.5281/zenodo.17478608)



Energia is a decision-making tool. Models can be constructed by providing data regarding bounds on commodity streams and operations. Spatial specificity and time-series input of varying sizes renders multiscale models. Their analysis yields insight into the interactions between different decisions. The term 'streams' is applied broadly. pre-categorized streams are broadly classified into commodities (resource, currency, emission, land, material, land, etc.) and impact (economic, environmental, social).

Operation types current include process, storage, and transportation.  A process is a catch-all for power generation, dense energy carrier (DEC) or chemical production. Storage involves charging and discharging which can both be configured individually. Transportation networks can involve multiple linkages between locations. Operational parameters include material and land use, impact, conversion efficiency. Construction can also be modeled as capacity sizing problems.

Broadly, Energia can be applied towards the multiscale modeling and optimization of energy systems under uncertainty. Risk analysis can be performed using various approaches such as scenario analysis, stochastic and robust programming, and multiparametric programming. The general class of problems is currently multiparametric mixed integer non-linear programming (mpMILP). Non-linear programs (mpMINLPs) can be modeled using piece-wise linearization. The multiscale nature of models affords simultaneous design and scheduling. Further Comprehensive resource balances allow cost optimization, carbon accounting, social life cycle analysis, and other forms of impact analysis. 

Notably, impact is ascertained as a function of decisions. The trade-offs between minimizing or maximizing different impact streams can be determined as pareto fronts. Outputs such as stream contributions, production levels, capacities as a function of time and space can also be exported and illustrated. Additionally, scenario reduction via clustering, and integer cuts can be utilized to manage computational tractability. 


<!-- ![alt text](https://github.com/TAMUparametric/energiapy/blob/main/docs/hierarchy.png?raw=true) -->


# Features 

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

Clustering submodules include:

1. agglomerative hierarchial clustering (AHC)
2. dynamic time warping (DTW)
3. k-means

Both the input data and solution output can be illustrated, examples include:

1. input data: capacity, demand, cost factors
2. solution output: inventory, production, consumption, discharge/sales schedule; contribution towards costs (capital,
   variable and fixed operational), meeting demand.

Callable external packages are available for:

1. Integration with high-fidelity process modeling modules such as  
2. Filling missing data (weekends, public holidays) for time-series data such as resource price
3. Fetch weather data at an appropriate resolution from [NREL NSRDB](https://nsrdb.nrel.gov/) for any county
   in the US

Libraries have pre-loaded sets of:

1. Components such as SI and miscellaneous units, currencies, time units, environmental indicators. 
2. Example and test problems across various applicative domains
3. Recipes for decision-making, instructions for calculations, and attribute aliases. 


Note that some of these functionalities are available in [Energia<2.0.0](https://github.com/TAMUparametric/energiapy/tree/v1.0.7) and are being ported to the 2.0 interface. 



