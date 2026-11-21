# Approved reference-fixture correction

Rahul approved applying the previously reviewed fixture patch. The patch is
now applied to `tests/MOO_test.py`: the third reference objective is explicitly
minimized using Gurobi, as are the first two. All existing test functions and
assertions are unchanged (verified by comparing their Python ASTs).

This preserves the Gurobi-specific reference dispatch when Gana 1.5.0 selects
HiGHS by default. The library's solver default, production code, tolerances,
expected results, and quality gates are unchanged.

Validation in a separate environment using released Gana 1.5.0:

- All 210 tests pass on Python 3.12.14.
- Statement coverage: 87.6682%; branch coverage: 79.7830%; both existing gates pass.
- Fatal Flake8 checks pass for the changed test; installed dependencies are compatible.
- The exact approved patch was applied. No other existing test was changed.

`checks.json` records versions, coverage counts, file hashes and the base commit.
`tests.log` and `environment.txt` retain the supporting evidence. Hosted Python
3.12/3.13, quality, documentation and parity results are attached to PR #367.
The full-year audit code and original numerical evidence are unchanged by this
fixture correction, so its annual solves were not repeated.

The [earlier report](../2026-11-20-quality/README.md) remains a frozen record of
the pre-approval failure, including the proposed patch and the unchanged-main
reproduction. Its statement that the patch was not yet applied describes that
previous stage, which this report supersedes.
