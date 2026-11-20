Case Studies
============

These standalone notebooks use the Energia 2.x API. Each includes its inputs
and uses Energia's solver entry points. Deterministic solves use ``Model.opt()``
with HiGHS by default. The multiparametric notebook uses ``Model.solve()`` and
PPOPT, whose solver dependencies are separate.

These are compact adaptations. Representative periods and illustrative costs
are identified in each notebook; their results are not full-data legacy parity
claims. See :doc:`validation` for the checked scope and corrections.

Supply chains and energy system design
--------------------------------------

.. toctree::
   :maxdepth: 1

   coffee
   lignin_supply_chain
   ivanov_network
   houston_design
   multilocation_hydrogen
   hydrogen_pathways
   materials_and_emissions
   renewable_production

Uncertainty and profile reduction
----------------------------------

.. toctree::
   :maxdepth: 1

   parametric_hydrogen
   chance_constrained_demand
   hydrogen_flexibility
   warped_profiles

.. toctree::
   :maxdepth: 1

   validation
