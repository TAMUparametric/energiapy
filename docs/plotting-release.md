# Plotting release validation

Energia 2.3.0 requires `gana[highs]>=1.6.0,<2`. Gana owns chart construction,
rendering, composition, the default theme and export. Energia owns registered
result-domain selection, physical labels/units and temporal interpretation.

[Gana 1.6.0](https://github.com/cacodcar/gana/releases/tag/1.6.0) is published on
PyPI. Energia's PR, main and release jobs install the declared released
dependency; no integration constraint or Rust build toolchain is needed.

## Supported interpreters

Package CI runs the full test suite, coverage gates, distribution builds,
installed-wheel solve and PDF/SVG/PNG export on Python 3.12, 3.13 and 3.14.
Documentation, type checks and the recorded complexity baseline retain their
configured Python 3.12 environment.

Use Python 3.12 or 3.13 on Intel Macs while Numba does not supply Python 3.14
binary wheels for that platform. Python 3.14 compatibility is validated on
Linux; this does not establish support for newer or free-threaded interpreters.

## Release preparation

- Preserve the declared Gana and Vaelchi ranges and the existing quality floors.
- Include the result figures from PR #370 in all 12 case-study notebooks, keeping
  their model inputs, assertions and previously saved outputs.
- Run the configured checks against released dependencies. Execute notebook
  copies outside the source tree and inspect plots without replacing saved results.
- Build the source distribution and wheel, check their metadata, and test the
  installed wheel outside the checkout with `pip check`, `tools/wheel_smoke.py`
  and `tools/plotting_gallery.py`.

The multi-location comparison keeps its historical dependency pins and source
hashes intact. Its current environment follows Energia's declared dependencies;
its separate historical environment retains Gana 1.4.0.

## Remaining publication steps

1. Review and authorize the release-preparation PR after its checks pass.
2. Merge the approved head, set the final 2.3.0 changelog date, and verify checks
   on the release commit.
3. Publish GitHub release `2.3.0` to trigger `.github/workflows/release.yml`.
   That workflow validates the supported Python matrix and publishes the
   validated distributions to PyPI.
4. Attach the validated wheel and source archive to the GitHub release. Verify
   their hashes against PyPI, the release notes, and the documentation build.

Release preparation does not publish, tag or merge the changes.

## Published-dependency evaluation — 2026-11-22

Before this preparation, Energia main `c689683cef5da65def90d2097816b981420d916d`
was tested with published Gana 1.6.0, whose release commit is
`24be6807eb419ca2b84178e5a36488bf42bb1bc5`.

- All 232 tests passed on Python 3.12 and 3.13 in
  [package CI](https://github.com/TAMUparametric/energiapy/actions/runs/45007826269).
- All 232 tests passed against installed distributions on Python 3.14. Statement
  and branch coverage were 88.19% and 80.82%, above the unchanged floors.
- Fresh installed-wheel solves, dependency checks and PDF/SVG/PNG exports passed.
- All 12 case studies passed in
  [fresh hosted kernels](https://github.com/TAMUparametric/energiapy/actions/runs/45007826287).
- Documentation and model type checks passed against the published dependency.

These checks establish the released dependency contract. The release-preparation
PR separately validates the added notebook figures and Python 3.14 CI entry.

## Release-preparation checks — 2026-11-22

The source at `528f299769210ce87047b9be27338685351df868` passes the following
local checks with Gana 1.6.0 and Vaelchi 0.1.1 installed from PyPI:

| Python | Tests | Statement coverage | Branch coverage |
|---|---:|---:|---:|
| 3.12.14 | 232 passed | 88.24% | 81.01% |
| 3.14.10 | 232 passed | 88.19% | 80.82% |

- All 12 notebooks, including the added plotting cells and their original
  assertions, pass in separate Python 3.14/IPython processes. Local kernel
  startup is blocked by workspace networking; CI executes fresh Jupyter kernels.
- Strict Sphinx, configured Mypy, Radon and Flake8 error checks pass on Python 3.12.
- Source and wheel builds pass strict Twine checks. All 99 packaged Python files
  match the source. A fresh Python 3.14 environment installs the built wheel,
  passes `pip check`, solves the smoke model and exports the PDF/SVG/PNG gallery
  outside the checkout.
- Workflow YAML, interpreter/version metadata, notebook structure and whitespace
  checks pass. Notebook contents match PR #370 exactly.

The required hosted checks must also pass on the final PR head before merge.

## Earlier candidate validation

Gana candidate: `47cf21acc7f78771d5116297fcc32514b53e25bd`
([PR #71](https://github.com/cacodcar/gana/pull/71)).

- Gana: all configured quality gates passed on Python 3.12 and 3.13;
  2,172 tests and 10 subtests per interpreter. Statement/branch coverage:
  91.40%/85.32%. The final source was unchanged throughout both runs.
- All 28 new adapter tests also passed against installed Gana/Energia wheels
  outside the checkouts.

- Energia: 232 tests passed on Python 3.12 and 3.13, including 22 new plotting
  tests. Existing tests, fixtures and coverage thresholds are unchanged.
- Statement/branch coverage: 88.24%/81.01% on both Python 3.12 and 3.13;
  both exceed the configured floors.
- Types, changed-file Ruff checks, strict Flake8 errors, complexity, Sphinx and
  distribution metadata checks passed. Built wheels match the tested Python
  source and install together without dependency conflicts.
- All 12 case-study notebooks' code and assertions passed in independent Python
  processes. This environment cannot start Jupyter kernels because socket binds
  are blocked; the normal notebook workflow also passed in hosted CI.
- The 48-hour multi-location comparison passed against the candidate. This
  verifies the short integration case, not a repeat of the full-year audit.
  Hosted CI also passed the comparison with the pinned historical implementation.
- The gallery uses the default Gana theme and was inspected in colour/grayscale.
  Individual PDFs measure 3.5 × 2.6 inches. The default Latin Modern PDF fonts
  embed as valid Type 3 outlines; no universal journal font compliance is claimed.
