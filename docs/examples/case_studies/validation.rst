Case-study validation
=====================

Scope
-----

These twelve notebooks are compact adaptations of the
`Kuru legacy examples <https://github.com/cacodcar/kuru/tree/db35908bd9056ef8f484c425bf2d2cb428677a83/studies/examples_old>`_.
Representative periods, rescaled loads, and illustrative costs remain explicitly
identified in each example. Executing them does not establish full-data parity
with every original study.

Deterministic objectives now use ``Model.opt()``, which selects HiGHS by default
in Energia. ``parametric_hydrogen`` retains ``Model.solve()`` and PPOPT.
Use the merged Energia source containing the HiGHS adapter; the older 2.2.0
distribution predates that adapter. This check used the released Gana 1.4.0,
Vaelchi 0.1.1, and HiGHS 1.16.0 on Python 3.12.

On November 20, 2026, all 12 notebooks and their 31 Python cells passed.
All 27 deterministic solves also passed a separate HiGHS/Gurobi comparison
on the corrected formulations. The largest absolute objective difference was
1.40e-9. Independently recomputing the HiGHS matrix rows and bounds gave a
maximum row violation of 3.30e-10 and zero bound violation.

Reproduce the notebook checks from a checkout::

   python -m pip install -e '.[docs]' ipykernel
   python tools/run_case_studies.py /tmp/energia-case-studies

Each notebook runs in a fresh kernel. Executed copies go to the output directory;
the source notebooks are preserved. The Case studies GitHub Actions job runs
the same command and retains executed notebooks as an artifact. The ordinary
documentation build alone does not execute these notebooks.

Fixed incidental charges
------------------------

The lignin port omitted unconditional incidental charges and included solvolysis,
which the source defines but excludes from both study configurations. The
corrected notebook uses the original process set and embeds all incidental
charges alongside the conversion and cost tables.

The legacy cost implementation charges every registered process at every
location. Its location aggregation does not filter out processes unavailable at
that location. Preserving this behavior adds 1,232.129 to annual single-site
spending and 3,696.387 to annual three-site spending, including idle processes.
These are constants, not capacity costs, per-day costs, or activation charges.

The notebook asserts that its negative net cost matches the saved profits in
`the original lignin notebook <https://github.com/cacodcar/kuru/blob/db35908bd9056ef8f484c425bf2d2cb428677a83/studies/examples_old/lignin/case_study_combined.ipynb>`_:

.. list-table:: Archived profit references
   :header-rows: 1

   * - Configuration
     - Annual profit
   * - Single site
     - 1,543,806,741.072
   * - Three sites
     - 1,543,447,562.076

The absolute comparison tolerance is 0.05 currency units. The archived
distributed solve itself has a 0.029 gap between its incumbent and bound.
Removing the unused solvolysis option did not change the optimal production in
these cases. Restoring the constants changes profit, not PHA output.

Transport and full-year scope
-----------------------------

``Transport(resource) == coefficient`` scales both ends of the transported
stream. It does not express a delivery efficiency. The representative-day
multi-location example now uses unit transport coefficients and explicit loss
processes at New York. Every period checks hydrogen consumption, rail losses,
grid losses, and delivered electricity.

The rail-only case now ships 39.36185567 tonnes to deliver 38.181 tonnes to the
fuel cell. Its daily cost changes from 67,284.21 to 69,499.68. The rail-plus-grid
case changes from 30,409.82 to 30,615.83. These changes reflect explicit 3% rail
and 0.1% grid losses and consistent costing of the dispatched flow.

The full legacy multi-location study is a different formulation:

.. list-table:: Distinguish the two studies
   :header-rows: 1

   * - Property
     - Executed teaching example
     - Archived full-year study
   * - Time grid
     - Four six-hour representative blocks
     - 8,760 chronological hours
   * - New York peak demand
     - 35 MW
     - 80 MW
   * - Technologies and costs
     - Illustrative PV, gas, electrolysis, fuel cell
     - Original site-specific technology and storage sets
   * - Rail balance
     - Explicit 3% loss
     - Lossless in the implemented legacy equations
   * - Purpose
     - Demonstrate spatial modeling and transport options
     - Reproduce the original annual study

The saved Gurobi outputs in
`ml-sp-milp.ipynb <https://github.com/cacodcar/kuru/blob/db35908bd9056ef8f484c425bf2d2cb428677a83/studies/examples_old/multiperiod/ml-sp-milp.ipynb>`_
record a minimum annual cost of 1,847,843,268.177 and maximum annual New York
electricity delivery of 3,202,802,043.034 MWh. An earlier separate HiGHS
reconstruction reported agreement with these values, preserving the implemented
lossless rail balance. That earlier reconstruction is not part of this notebook
or its CI check and was not rerun for this correction. The archived values are
reference results, not outputs of the representative-day example. Reproducing
that full-year verification requires the original hourly inputs, implementation
revision, and reconstruction scripts.

Demand mappings and solution differences
----------------------------------------

The solver change preserves every notebook's existing demand relation. Coffee,
lignin, and chance-constrained scheduling use lower bounds. Houston, the
representative multi-location example, material choices, hydrogen pathways,
and warped-profile dispatch use equalities. Flexibility, renewable production,
and network disruption model shortages or limited service explicitly. The
parametric notebook keeps hydrogen demand as a parameterized lower bound.

Houston has alternative optimal battery schedules: HiGHS and Gurobi both give
a daily cost of 77,267.90. The recorded dispatch can differ while satisfying
the same constraints. Equal objectives do not require identical primal vectors.
