# Annual multi-location validation — 2026-11-20

All 8,760 chronological hours pass for both objectives. These results reproduce
the original **lossless** rail equations; the representative-day teaching
notebook includes 3% rail losses and is a different model.

| Objective | Printed archive | Energia / HiGHS | Independent / HiGHS | Absolute archive difference |
|---|---:|---:|---:|---:|
| cost | 1847843268.177000 | 1847843268.176695 | 1847843268.176698 | 0.000304937 |
| delivery | 3202802043.034000 | 3202802043.033573 | 3202802043.033573 | 0.000426769 |

Delivery is in MWh. Cost uses the source study's monetary units. Both archive
comparisons and agreement between implementations use absolute tolerance 0.001.

| Case and formulation | Primal–dual gap | Maximum row violation | Bound violation | Dual stationarity residual |
|---|---:|---:|---:|---:|
| cost, energia | 1.85966492e-05 | 1.9309665e-11 | 1.61685781e-10 | 8.05594027e-08 |
| cost, independent | 7.62939453e-06 | 2.72848411e-11 | 7.63975549e-11 | 1.03376806e-07 |
| delivery, energia | 1.76429749e-05 | 1.16415322e-10 | 0 | 2.84217094e-12 |
| delivery, independent | 1.33514404e-05 | 1.16415322e-10 | 0 | 0 |

Every value above is recomputed from the original matrices. Dual sign violations
are also checked and recorded in `results.json`. All feasibility, stationarity
and sign residuals must be at most 1e-6; the absolute primal–dual gap must be at
most 0.001. The complete Energia hourly solution is separately checked against
the independent physical equations.

## Reproduction and provenance

Run from the Energia repository using Python 3.12:

```bash
python -m pip install -e . -r tools/multilocation_parity/requirements.txt
python -m tools.multilocation_parity /tmp/multilocation-full
```

The verified source is commit `0ad18aafffc84f144fe98f42f965b740d35e5892`.
The long cost optimizations ran using code commit
`08e05459db238705a60a4881aa9dfe282ca69272`; `initial-results.json` and
`initial-cost-*.log` retain that run, including IPM crossover warnings and
successful simplex cleanup. Maximum delivery used previously saved bases.
The final run at `0ad18aa` loaded the completed bases, solved all four LPs again,
and recomputed every check; its JSON, logs and schedules are the unprefixed files.
No saved success flags are used. The only code changes between these commits
split functions to meet the complexity limit. All four annual matrices, bounds,
objective vectors and semantic column keys are byte-identical, as recorded in
`annual-matrix-equivalence.json`.

The Energia LP has 1,550,548 rows and 1,296,508 columns. The independent LP has
394,200 rows and 289,104 columns. Stored matrix entries include explicit zero
coefficients where present. This is one simultaneous annual optimization with
shared investment decisions and all five inventory trajectories linked across
hours. It is not a set of independent two-hour optimizations.

The archived notebook commit/blob, original input hashes, package versions,
platform, script hashes and Energia source hash are in `results.json`.
The raw data are in `../../data`; all four input hashes are checked before a solve.
`environment.txt` and `legacy-environment.txt` record the installed environments.
No unpublished sibling checkout was substituted for Gana 1.4.0 or Vaelchi 0.1.1.
The original library runtime was not recorded in the notebook. The pinned 2023
implementation is a compatible historical reference, not a recovered exact
runtime. That implementation is rerun for 48 hours; the annual old Gurobi model
is compared through its saved objectives, not a new licensed Gurobi solve.

The two current formulations share the transcribed technology table and inputs;
the old implementation uses copied original resource/process definitions.
Agreement does not require identical optimal hourly schedules or zero-cost
capacities. Fixed incidental charges were unspecified in this source case and
remain zero; fixed operating costs multiply capacity.

## Additional verification

- 210 tests pass; existing tests and coverage floors are unchanged.
- Statement coverage: 87.6682%; branch coverage: 79.7830%; both configured gates pass.
- Direct Energia versus assembled equations, bounds and objective coefficients:
  exact comparison at 6, 24 and 48 hours.
- Actual pinned historical implementation versus current Energia: both 48-hour
  objectives agree within 0.001 (`legacy-48.json`, `current-48.json`).
- Ruff lint and formatting, configured Radon complexity and strict Sphinx pass.
- Original notebook outputs and research inputs are preserved.

Hourly CSVs and capacity JSONs contain the two Energia solutions, including
zero and idle options. Large solver basis files are deliberately kept out of
Git; the runner and workflow can save them in their output/artifact directories.
`SHA256SUMS` covers all evidence files in this directory except itself.
