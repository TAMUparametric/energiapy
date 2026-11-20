Mathematical Program
====================


Selecting a deterministic solver
--------------------------------

Install ``python -m pip install "energiapy[highs]"`` to use HiGHS for
linear and mixed-integer models. Select the solver when setting a sample
objective or when optimizing an objective you have already defined.

.. code-block:: python

   from energia import Model, Resource

   model = Model()
   model.labor = Resource(take=True, price=3)
   model.labor.release == 2
   model.cash.spend.obj()
   model.opt(using="highs")
   assert model.program.active_objective.X == 6
   model.save(as_type="json", path="result.json")

The shorthand ``model.cash.spend.opt(using="highs")`` sets and solves the
objective in one call. Gurobi is the default for deterministic optimization.
Use ``model.solve()`` for multiparametric problems.

.. toctree::
   :maxdepth: 1
   :caption: Mathematical Program
   :hidden:

   the_program
   special_constraints