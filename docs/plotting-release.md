# Coordinated plotting release

Energia 2.3.0 requires `gana[highs]>=1.6.0,<2`. Gana 1.5.0 cannot provide
this adapter contract. Gana owns chart construction, rendering, composition,
the default theme and export. Energia owns registered-domain selection,
physical labels/units and temporal interpretation.

## Alignment checks before either merge

- Keep Gana PR #71 and the companion Energia PR open until both heads pass.
- Verify both supported Python versions (3.12 and 3.13), existing tests,
  coverage floors, types, complexity, lint, docs and package checks.
- Test installed wheels together outside both checkouts; run `pip check`, solve
  the bundled example, inspect the plotted values and export PDF/SVG/PNG.
- Inspect individual 3.5-inch figures and the 7.2-inch gallery in colour and
  grayscale. Keep declared units, time coordinates, missing values and solution
  selection unchanged. Publisher-specific font requirements remain explicit.

`requirements/plotting-integration.txt` pins the tested Gana commit. Feature-branch and PR jobs
apply it as an installation constraint; main and release jobs resolve the
published dependency normally. The distribution metadata contains a released
version requirement, not a Git URL. To reproduce integration locally:

```sh
python -m pip install -c requirements/plotting-integration.txt -e '.[test,docs]'
python -m pytest tests/plotting_test.py
python tools/plotting_gallery.py /tmp/energia-figures
```

## Authorized merge/publication order

1. Review the paired evidence and approve Gana's merge.
2. Merge and release Gana 1.6.0 using its existing build/publish workflows.
   Verify PyPI wheels, source distribution, release assets and documentation.
3. Remove the temporary PR constraint wiring and integration pin from Energia.
   Re-run Energia's full required checks using **released Gana 1.6.0 from PyPI**.
   Rebuild and install Energia's wheel in a clean environment.
4. Approve and merge Energia only after the released-dependency checks pass.
   Set the final changelog dates and release Energia 2.3.0 with its existing
   release workflow. Verify PyPI, assets and documentation.

The staged package versions do not authorize a merge, tag or publication.
Do not enable auto-merge. A Gana change after the pinned integration commit
requires refreshing the pin and repeating affected integration checks.

## Initial scope

The bindings cover profiles, scatter, grouped/stacked bars, areas, supplied
bands/intervals, composition and export. They deliberately require a unique
registered domain and perform no implicit physical aggregation. RTNs, heatmaps,
automatic flow reconciliation and cross-scenario result collections remain
separate work. Existing notebooks and manuscript results are unchanged.

## Integration evidence

Gana candidate: `e250cfd094bcea2339199295b8c6bba23dbb61dc`
([PR #71](https://github.com/cacodcar/gana/pull/71)).

- Gana: all configured quality gates passed on Python 3.12 and 3.13;
  2,172 tests and 10 subtests per interpreter. Statement/branch coverage:
  91.40%/85.32%. The final source was unchanged throughout both runs.
- All 28 new adapter tests also passed against installed Gana/Energia wheels
  outside the checkouts.

- Energia: 232 tests passed on Python 3.12 and 3.13, including 22 new plotting
  tests. Existing tests, fixtures and coverage thresholds are unchanged.
- Statement/branch coverage: 88.29%/81.04% on Python 3.12 and
  87.93%/79.93% on Python 3.13; both exceed the configured floors.
- Types, changed-file Ruff checks, strict Flake8 errors, complexity, Sphinx and
  distribution metadata checks passed. Built wheels match the tested Python
  source and install together without dependency conflicts.
- All 12 case-study notebooks' code and assertions passed in independent Python
  processes. This environment cannot start Jupyter kernels because socket binds
  are blocked; the normal notebook workflow remains enabled in CI.
- The gallery uses the default Gana theme and was inspected in colour/grayscale.
  Individual PDFs measure 3.5 × 2.6 inches. The default Latin Modern PDF fonts
  embed as valid Type 3 outlines; no universal journal font compliance is claimed.

The published-package check in release step 3 remains required: local sibling
builds establish integration with the pinned candidate, not availability on PyPI.
