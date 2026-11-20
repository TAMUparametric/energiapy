# Full-year multi-location parity

This audit reproduces the two saved objectives in Rahul Kakodkar's
[`ml-sp-milp.ipynb`](https://github.com/cacodcar/kuru/blob/db35908bd9056ef8f484c425bf2d2cb428677a83/studies/examples_old/multiperiod/ml-sp-milp.ipynb):
minimum annual cost and maximum annual New York electricity delivery. It uses
all 8,760 chronological hours and the original Houston, San Diego and New York
technology sets. The representative-day teaching notebook is a separate model.

From the repository root, using Python 3.12:

```bash
python -m venv .venv
.venv/bin/python -m pip install -e . -r tools/multilocation_parity/requirements.txt
.venv/bin/python -m tools.multilocation_parity /tmp/multilocation-full
```

The output contains `results.json`, four HiGHS logs, hourly schedules and
capacity tables for both Energia solutions. The command fails if either
annual objective differs from the printed archive by more than **0.001**,
if the two implementations disagree, or if feasibility/duality checks fail.
It requires no Gurobi license, Drive login, or access to the private Kuru repo.
Allow several GB of memory and substantial solver time for the full-year run.
The cost solve first verifies a feasible renewable-only design, then uses its
cost to bound paid capacities. Free capacities take their maximum values.
These choices improve solver conditioning. Reduced costs for fixed free
capacities are transferred back to the original bound rows; feasibility,
dual signs, stationarity and the primal-dual gap are all checked against the
**original, unrestricted matrices**. An active artificial bound cannot silently
certify the wrong problem. The cost solve uses HiGHS IPM with crossover;
delivery uses simplex. The barrier hands over to crossover at a relative
1e-3 threshold; this is an intermediate stopping rule, not the accepted
solution accuracy. Final absolute feasibility and primal-dual checks retain
their 1e-6 and 0.001 tolerances against the original constraints.

`--basis-dir /path/to/previous/output` can reuse saved solver bases. Every LP
is still loaded, solved and independently verified; this does not reuse a
saved success flag.
A quick check is `--hours 48`; only a full 8,760-hour run asserts the archived
annual objectives. All shorter windows are normalized using the **full-year**
maxima before slicing.

## What is compared

1. `energia_model.py` builds the source case with Energia's resources, processes,
   locations, storage, transport, capacity, operation and demand aspects.
2. `assembly.py` exports a two-hour Energia/Gana matrix and expands it to one
   annual LP. It shares investment columns, charges investment once, and links
   all five inventories between adjacent blocks. This is not temporal
   aggregation: every hourly variable, equation, input and inventory link is
   retained. The entire year is solved simultaneously.
3. `linear.py` independently writes the physical balance equations after
   eliminating zero flows, accounting auxiliaries and redundant binary choices.
   Both full LPs are solved with released HiGHS. Energia's complete hourly
   solution is also projected into these independent equations and checked.
4. New regression tests compare **every equation, bound and objective
   coefficient** in the block assembly with a directly built Energia model for
   6, 24 and 48 hours. They test inter-block and inter-day inventory continuity,
   shared capacities, changing weather, prices and demand.
5. `legacy.py` optionally checks short cases against the actual pinned 2023
   Pyomo implementation, using copied original resource/process definitions.
   See the separate environment below.

The independent LP and Energia model share the transcribed technology table
and hourly inputs, so agreement between them alone does not validate that
transcription. The original-code checks and the two archived full-year
objectives provide additional independent references. Different optimal hourly
schedules and zero-cost capacities are permitted; equality of every primal
variable is not required.

## Preserved source assumptions

| Item | Original behavior retained by this audit |
|---|---|
| Time | 8,760 consecutive one-hour steps; zero initial inventory; no terminal inventory equality |
| Weather | 2019 DNI and wind **speed**, each divided by its own site's annual maximum; no turbine power curve |
| Load | 2018 NYC profile, normalized to an 80 MW peak |
| Gas price | Source 2020 data, days 1–365, previous-day fill, source outlier rule, then maximum normalization; each daily value used for 24 hours |
| Cost demand | NY Power release **at least** the hourly demand; HO and SD Power release zero |
| Delivery objective | Maximize NY Power release without the cost case's demand requirement |
| Rail | HO–NY 2,366; SD–NY 2,620 distance units; flow cost 0.001667 per distance unit; **lossless implemented balances** |
| Installed plants | HO/SD: LiI, PV, WF, SMRH, AWE, AQoff_SMR; NY: LiI, H2FC; automatic LiI discharge at each site |
| AWE basis | One unit of electricity consumed produces 0.019 units of hydrogen |
| Battery | Charge capacity costs 3,516,428 + 87,910; discharge capacity and energy capacity have no capital charge; inventory limit 10,000 |
| CO2 storage | Cumulative inventory capped at 10,000 per source site; no discharge |
| Fixed incidental charges | None specified in this source case, hence zero; fixed operating costs multiply installed capacity |
| Integer choices | Single mode, zero minimum capacities and no binary objective charges. All availability binaries can be one; this completion preserves the continuous feasible region exactly |

The source declares 3% rail loss but its implemented transport balances do not
apply it. This audit preserves that behavior. The corrected teaching notebook
models the loss explicitly. It would be wrong to silently add that loss here
and still claim parity with the archived solve.

The four original CSV files are included byte-for-byte. `provenance.json`
records their Drive IDs and SHA-256 hashes, the notebook commit/blob, and the
historical implementation pin. The runner verifies the input hashes before
solving. The unused Houston/San Diego load spreadsheets and New York weather
are unnecessary: source-site electricity demand is zero and New York has no
PV or wind plant. No source input is replaced with a synthetic profile.

## Historical implementation check

The original notebook does not record its library commit. The compatible
historical implementation pinned here is
`TAMUparametric/energiapy@c78c8902a7b45be4ed6d56a47341286271e855bf`.
This is **not a claim to have recovered the original runtime**. In particular,
the later `v1.0.7` branch changes demand handling and is not an interchangeable
baseline for the notebook as written.

Use a separate environment and preserve the historical source unchanged:

```bash
python -m venv /tmp/energia-legacy-venv
/tmp/energia-legacy-venv/bin/python -m pip install -r tools/multilocation_parity/legacy-requirements.txt
curl -L --fail https://codeload.github.com/TAMUparametric/energiapy/tar.gz/c78c8902a7b45be4ed6d56a47341286271e855bf -o /tmp/energia-legacy.tar.gz
printf '%s  %s\n' 7eccb26670817b09eb9c88d8672c950a04bf447c29dbc78f4bbb1d47957636e4 /tmp/energia-legacy.tar.gz | sha256sum --check
mkdir -p /tmp/energia-legacy-source
tar -xzf /tmp/energia-legacy.tar.gz -C /tmp/energia-legacy-source --strip-components=1
PYTHONPATH=/tmp/energia-legacy-source/src /tmp/energia-legacy-venv/bin/python -m tools.multilocation_parity.legacy /tmp/multilocation-legacy --hours 48
```

The legacy wrapper fixes redundant availability binaries to one and disables
presolve for the short legacy check. Unused cost accounting rows at the very
large maximum-delivery solution can show absolute cancellation error even
when their relative residual is near machine precision; the report retains
both absolute and scaled residuals. It does not loosen the full Energia
physical feasibility check.

CI runs the short check, the pinned historical comparison and the regression tests. A manual workflow dispatch
can run all 8,760 hours and retain the solver logs and schedules as an artifact.
Recorded annual evidence is in `results/`; it is not overwritten by the CLI.
