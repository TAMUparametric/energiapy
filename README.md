<p align="center">
  <img src="https://github.com/TAMUparametric/energiapy/raw/main/docs/_static/logo2.jpg" width="75%">
</p>


[![Documentation Status](https://readthedocs.org/projects/energiapy/badge/)](https://energiapy.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/energiapy.svg)](https://pypi.org/project/energiapy)
[![Downloads](https://static.pepy.tech/personalized-badge/energiapy?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads)](https://pepy.tech/project/energiapy)
[![Python package](https://github.com/TAMUparametric/energiapy/actions/workflows/python-package.yml/badge.svg)](https://github.com/TAMUparametric/energiapy/actions/workflows/python-package.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/994d46ab40ac4f0ead5ed9d1ea1b0fab)](https://app.codacy.com/gh/TAMUparametric/energiapy/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![DOI](https://zenodo.org/badge/600269309.svg)](https://doi.org/10.5281/zenodo.17478608)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/energiapy.svg)](https://pypi.org/project/energiapy/)
[![codecov](https://codecov.io/gh/TAMUparametric/energiapy/branch/main/graph/badge.svg)](https://codecov.io/gh/TAMUparamteric/energiapy)

Energia is a tool for the data-driven multiscale modeling and optimization of energy systems under uncertainty. Users are directed to {cite}`kakodkar2022review` for an overview of the state-of-the-art in the field.
The component-driven methodology is inspired by the resource task network (RTN) methodology {cite}`barbosa_povoa_pantelides_1997` and constituent functionalities developed through the research conducted in
the [Multiparameteric Optimization and Control (Pistikopoulos) Group](https://parametric.tamu.edu/). The Tutorials and Examples sections are a good starting point.



<!-- ![alt text](https://github.com/TAMUparametric/energiapy/blob/main/docs/hierarchy.png?raw=true) -->



# Applications

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

