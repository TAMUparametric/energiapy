Case Studies
============

These standalone notebooks use the Energia 2.x API. Each includes its inputs
and uses Energia's solver entry points. Deterministic solves use ``Model.opt()``
with HiGHS by default. The multiparametric notebook uses ``Model.solve()`` and
PPOPT, whose solver dependencies are separate.

These are compact adaptations. Representative periods and illustrative costs
are identified in each notebook; their results are not full-data legacy parity
claims. See :doc:`validation` for the checked scope and corrections.

Each notebook ends with an interpreted plot of its existing inputs or solved
results. The figures use Gana's default theme and retain the model's units;
stocks, rates and costs occupy separate panels where their bases differ.

.. list-table:: Result plots
   :header-rows: 1
   :widths: 35 65

   * - Example
     - View
   * - :doc:`coffee`
     - Daily input and output quantities
   * - :doc:`lignin_supply_chain`
     - Signed annual cash flows and net cost
   * - :doc:`ivanov_network`
     - Disruption cost and emergency supply
   * - :doc:`houston_design`
     - Generation areas, external delivery and stored energy
   * - :doc:`multilocation_hydrogen`
     - Shipments by origin, with separate hydrogen and electricity panels
   * - :doc:`hydrogen_pathways`
     - Planning cost and residual emissions
   * - :doc:`materials_and_emissions`
     - Cost and embodied emissions at three solved designs
   * - :doc:`renewable_production`
     - Served/unmet production and purchased electricity
   * - :doc:`parametric_hydrogen`
     - Generation mix at two evaluated parameter realizations
   * - :doc:`chance_constrained_demand`
     - Demand intervals, a one-sided service threshold and reliability cost
   * - :doc:`hydrogen_flexibility`
     - Supply cost and unmet demand across shortage penalties
   * - :doc:`warped_profiles`
     - Original and reduced profiles on the source coordinates

Plot descriptions remain available in the last cell for vector export, for
example ``dispatch_plot.save("dispatch.pdf", profile="print", fig_size=(7.2, 5.4))``
in the Houston notebook. See :doc:`../../tutorials/additional_features/manuscript_plotting`
for the shared plotting and export interface.

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
