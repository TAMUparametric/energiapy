Mathematical Program
====================


Selecting a deterministic solver
--------------------------------

Energia installs HiGHS and uses it by default for linear and mixed-integer
models.

.. code-block:: python

   from energia import Model, Resource

   model = Model()
   model.labor = Resource(take=True, price=3)
   model.labor.release == 2
   model.cash.spend.obj()
   model.opt()
   assert model.program.active_objective.X == 6
   model.save(as_type="json", path="result.json")

The shorthand ``model.cash.spend.opt()`` sets and solves the
objective in one call. Pass ``using="gurobi"`` to either call to use Gurobi.
Use ``model.solve()`` for multiparametric problems.

.. toctree::
   :maxdepth: 1
   :caption: Mathematical Program
   :hidden:

   the_program
   special_constraints