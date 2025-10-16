

.. _overview_components:

Overview
========


``Model`` is the primary central object which aggregate components based on a broader
perspective of what they describe, namely Scope (``Time``, ``Space``), ``System`` , ``Consequence``, ``Problem``. 


Scope
-----

These components define the extent of the system under consideration, and the fidelity of data. 

- ``Time``, with ``Periods`` and ``TemporalScales`` defining the discretization
- ``Space``, with ``Location`` and ``Linkage`` serving as nodes and edges 

The most sparsely discretized ``Periods`` serves as the temporal ``horizon``, and the most encompassing ``Location`` (which are nested) is the ``network``

Measurement
-----------

These provide a basis for measurement and conversion, scaling them appropriately.

- ``Unit`` can be defined in terms of other ``Unit`` s

Some commonly used units can be found in ``energia.library.components``, 
namely ``si_units`` which are subset of `SI Units <https://www.nist.gov/pml/owm/metric-si/si-units>`_ and ``misc_units`` which include some `US Customary Units <https://www.govinfo.gov/content/pkg/GOVPUB-C13-2aca3b6352009e0772f04a41c2011d3c/pdf/GOVPUB-C13-2aca3b6352009e0772f04a41c2011d3c.pdf>`_


Streams
-------

These quantify flow within the system, as well as interactions with the external environment.


- ``Commodity`` which includes ``Resource``, and subsets ``Currency``, ``Land``, ``Emission``, ``Material``, etc.
- ``Indicator`` categories such as ``Environ``, ``Social``, and ``Economic``

``Commodity``  streams belong to ``System``, whereas ``Indicators`` inform the ``Consequence``.

Operational
-----------

Decisions pertaining to these generate and direct ``Commodity`` streams. 

- ``Process`` for commodity conversion
- ``Transport`` to import and export certain commodities
- ``Storage`` to charge and discharge inventory

``Storage`` is actually a combination of two ``Process`` es (for charging and discharging) and an ``Inventory`` space. 

Game
-----

These suggest ownership and strategic interactions between independent actors (``Player`` s).

- ``Player`` is an independent actor
- ``Couple`` represents a link between two ``Player`` s

Aspect
------

The facets being modeled, categorized broadly into: 

- ``State`` (in Energia) are restricted to operational conditions
- ``Control`` or decision variables 
- ``Stream``, also a ``State`` that quantify ``Commodity`` streams 
- ``Impact`` which quantify ``Indicator`` streams 
- ``Loss``, a general variable to describe loss and (or) degradation 

Note that users can choose to model sans ``Control`` variables and model ``State`` directly. 
These are defined using ``Recipes`` which provide a structured way to define the context of an ``Aspect``.

Constraint
-----------


Data provided either:

- ``Bind`` or restrict any given ``Aspect``

or

- ``Calculate`` a dependent ``Aspect`` such as  ``Stream``, ``Impact``, or ``Loss``  

Consistency is maintained by generating implicit constraints:

- ``Balance`` for general resource balance 

and

- ``Map`` to scale and sum streams across spatiotemporal domains

Parameter
---------

No special parameter types exist of bind and calculations. However,:

- ``Conversion`` serves as general parameter that dictates conversion efficiency and material use for setup

Disposition 
-----------

Essentially ordered indices that describe both the fidelity and specificity of a modeling element.

- ``Domain`` is an ordered index set 

Objective
---------

Multiple objectives can be provided. Infact the lower and upperbounds of any ``Aspect`` with regards to a specific component within some spatiotemporal context 
can be determined. 