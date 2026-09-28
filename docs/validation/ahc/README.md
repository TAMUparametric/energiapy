# Historical AHC comparison

The default is `selection="legacy"`. Select `selection="nearest_centroid"`
explicitly to use the nearest member of each cluster, breaking numerical ties
with the earliest period. Both modes retain corrected error reporting.

## Results and scope

`results.json` records actual outputs for both modes and the historical function,
input-file SHA-256 hashes, the current implementation hash, dependency versions,
and per-day cluster labels. All day indices are zero-based.

Five historical datasets, each with 8,760 hourly observations, were reduced to
20 and 35 representative days. In all ten comparisons, default legacy mode
matches the historical representative indices, weights, and selected profiles
exactly. Nearest-centroid mode matches the historical cluster membership but
selects different representative days. This is not whole-model or solver parity.

The baseline is commit `0604a26ee45a564bcd83c736077944cb1c59a50d` (v1.0.7).
Its AHC blob is identical to that at `4e9a986e` (2023-09-19). Exact historical
function definitions are executed after AST extraction, excluding unrelated
model imports. Both implementations use the same installed dependencies;
these are not recreated historical dependency environments.

Inputs come from Kuru's `studies/examples_old/data`:

- `ho_solar.csv` (`dni`) and `ho_wind.csv` (`wind_speed`), joined on timestamps.
- `ho_solar19.csv` and `sd_solar19.csv` (`wind_speed`, `dni`).
- `ny_solar19.csv` (`DNI`, `Wind Speed`).
- `NYC_load.csv` (`Load`, dated 2018).

Raw numeric columns are used without physical conversion or case-study-specific
preprocessing. Weather and load from different years are tested separately.
Original datasets are not duplicated here; their hashes are recorded.

## Error reporting fix

`inertia` sums squared distances to the actual cluster centroids.
`reconstruction_error` sums squared distances to the selected profiles.
Both accumulate across all parent groups. Legacy `wcss_sum` used misassociated
centroids, divided by cluster count, and retained only the last parent. It is
recorded for provenance, not treated as the same metric as current SSE.

Legacy representative behavior can select outside the associated cluster or
repeat a representative. It is retained by choice. With one cluster, where the
historical NearestCentroid call cannot run, legacy mode uses nearest-member
selection. The small regression tests cover repeated representatives, default
selection, and error accumulation across parents.

## Reproduction

From the repository root, with the package's numerical dependencies installed:

```sh
python docs/validation/ahc/compare.py --data-dir /path/to/kuru/studies/examples_old/data --output /tmp/ahc-results.json
python -m pytest tests/ahc_test.py tests/time_test.py -q
```

The historical commit must exist in the local Git object database. The comparison
asserts exact legacy indices, weights, and selected profiles, and checks
nearest-centroid membership and independent representative selection. Independent
SSE comparisons use relative tolerance 1e-12. The targeted suite passed 28 tests.

## Local Git hooks inspected

At the time of this change, `.git/hooks/pre-commit` invokes
`$HOME/Research/kuru/.venv/bin/pytest $HOME/Research/packages/energiapy/tests/`.
It prints a warning on failure but always exits zero, so commit success alone
is not evidence of passing tests. `.git/hooks/pre-push` invokes the same suite
and also exits zero. No custom `core.hooksPath` was configured. These hooks are
local Git metadata, not distributed by this commit. Commit execution is captured
separately in `/private/tmp/energia-ahc-commit.log` and its Git trace file.
