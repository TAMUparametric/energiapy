"""energiapy was developed as a PhD project by Rahul Kakodkar

The project was supervised by Prof. Efstratios (Stratos) N. Pistikopoulos

It is licensed under the MIT License

The arrangment of the modules is as follows:

- inputs:

- values: Values of parameters

    These are the values of parameters, generated based on input:

    Value: base class
    contains name, index, disposition, and bound

    Number: if float or int
    Numeric parameter value

    DataSet: if input is DataFrame
    Deterministic data providing matching some temporal scale

    M: if input is True
    big = True makes the number bigger than any Number, else smaller
    Predefined BigM and smallm can be passed

    Theta: if input is a tuple of upper and lower bound.
    Parametric variable
    Predefined Th can be passed

    Predefined values are update to provide name, index, disposition, and bound
    when aspect is defined

- elements: Problem elements

    These are the building blocks of the optimization problem

    rulebook:
    Contains rules for formulating the optimization problem


    Parameter:
    Initialized using aspect

    Variable
    Generated as needed by parameter

    Constraint:
    Provides a relationship between parameter and variables







- components: Model components

    divided under:

    operations, commodities, spatial

- core: Contains the base classes that are used throughout the package
- inputs: Contains the classes for the inputs to the optimization problem
-




__author__ = "Rahul Kakodkar"
__copyright__ = "Copyright 2022, Multi-parametric Optimization & Control Lab"
__credits__ = ["Rahul Kakodkar", "Efstratios N. Pistikopoulos"]
__license__ = "Open"
__version__ = "0.0.1"
__maintainer__ = "Rahul Kakodkar"
__email__ = "cacodcar@tamu.edu"
__status__ = "Production"


"""
