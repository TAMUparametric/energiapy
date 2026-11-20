# Verification after code-quality review

Code commit: `0bcbb6e209ddac8c40223d1cb3bc97e1f258fc0d`.

The audit is now an explicit Python package. Related block and resource data
are grouped together, helpers meet the existing complexity/argument/local-variable
limits, and the exporter uses Gana's public MPS path. No checks or quality rules
were disabled. Existing tests and all `src/energia` files remain unchanged.

All four 8,760-hour LPs were re-solved from the completed bases and every
original-matrix feasibility/duality and physical-projection check passed.
Both objectives and all four matrix hashes are exactly unchanged from the
[initial recorded run](../2026-11-20/README.md). `results.json` records this code's
file hashes, inputs, versions and residuals. The initial report retains the long
optimizations and hourly schedules; this supplement retains the final solve logs.
The actual historical implementation comparison also passes again at 48 hours.

The 210-test suite passes with the audit's pinned released Gana 1.4.0 environment.
Coverage remains 87.6682% statements and 79.7830% branches. Ruff, the configured
Radon gate, and checks for every reported Pylint/Ruff Codacy rule pass locally.
Hosted results remain attached to PR #367.

## Separate existing-test failure with Gana 1.5.0

The unrestricted Python 3.12 and 3.13 CI jobs install newly released Gana 1.5.0.
They fail `tests/MOO_test.py::test_supermarket` while the other 209 tests pass.
The same failure reproduces on unchanged main commit
`ea42c1a5df65451df664827ca6a67d9793329bcb`; see `unchanged-main-gana15.log`.

The fixture explicitly selects Gurobi for its first two objectives, but calls
`Prg.lb()` for the third. That helper uses Gana's solver default, now HiGHS.
The consumption objective agrees, but the test asserts a particular Gurobi
solution among alternative optima, including unused capacity and its costs.
This is separate from the annual audit, whose own new checks pass in those CI jobs.

A proposed fixture change would replace its third solve with an explicit
minimum-consumption objective and `opt(using="gurobi")`:

```python
from gana import inf

_m._.minimum_consumption = inf(sum(_m._.consume))
_m._.opt(using="gurobi")
```

Both existing test functions were called unchanged against a model built this
way and passed with Gana 1.5.0; see `explicit-gurobi-verification.log`.
[The exact proposed patch](proposed-MOO-fixture.patch) changes only the fixture;
all expected results stay intact. **This fixture change has not been applied.** Repository instructions require
Rahul's explicit approval before editing an existing test. No dependency upper
bound, expectation change, skip, tolerance adjustment or solver-default change
was used to hide the failure.
