# Shared documentation baseline 1

Canonical maintenance home: `cacodcar/gana`, `docs/_shared`. Energia and
Vaelchi vendor the same directory. This is build configuration, not a package
runtime dependency. No remote configuration is executed during a build.

Use Python 3.13 and Ubuntu 24.04 for the primary documentation build. Gana also
requires Rust 1.88.0. Install the local project with:

```sh
python -m pip install -c docs/_shared/constraints.txt -e '.[docs]'
python docs/_shared/check.py
python -m sphinx -W --keep-going -b html docs /tmp/docs-html
```

Build a disposable copy when preserving tracked autosummary stubs matters;
the Gana/Vaelchi quality runner already does this. Package imports resolve
through the installed project (editable installs are used in CI and RTD).
The quality runners explicitly select their measured source through PYTHONPATH.
Notebook outputs are rendered statically; execution checks remain separate.

`requirements.in` defines the family docs toolchain; `constraints.txt` records
its Python 3.13 resolution. Local docs extras select the extensions they use.
The common Sphinx/Book Theme bounds also live in package extras for ordinary
installs. Local bibliographies, API hooks, styles, and scientific dependencies
remain package-owned. Existing `ref.python` warning exceptions in Gana/Energia
are retained pending a separate API-reference audit; no new exceptions are added.

The pinned theme owns System/Light/Dark behavior, persistence and OS updates.
The shared header override prevents duplicate hidden sidebar controls.

## Updates and drift checks

Change the canonical copy, resolve `requirements.in` again, validate all three
builds, increment the baseline version, and regenerate the manifest's SHA-256
entries for every file except the manifest itself and Python caches. Copy the
whole directory to consumers in coordinated PRs; record those PRs below or in
the coordination plan. CI and RTD verify the manifest before building. Compare
checkouts before submitting an update:

```sh
python docs/_shared/check.py --against ../energia/docs/_shared
python docs/_shared/check.py --against ../vaelchi/docs/_shared
```

The manifest detects local edits; the explicit comparison detects consumer
version drift. Upgrades are reviewed changes, never automatic downloads.

## Family links and inventories

Family navigation points explicitly to development documentation. It is a
product-discovery route, not a compatibility declaration. Development builds
can use explicit named Intersphinx roles, for example
`:external+gana:py:class:\`gana.block.program.Prg\`` in reStructuredText.
Implicit cross-project lookup is disabled to avoid changing existing references.

Inventory snapshots were retrieved on 2026-11-22 from each project's
`/en/latest/objects.inv`. Gana and Energia publish blank inventory versions;
Vaelchi publishes 0.2.0. The checked `/en/v1.6.0/` and `/en/1.6.0/` Gana,
`/en/v2.3.0/` and `/en/2.3.0/` Energia, and `/en/v0.1.1/` and `/en/0.1.1/`
Vaelchi inventories returned 404. Do not invent release URLs or treat mutable
`stable` aliases as tested dependency versions.

Tag/stable builds have no sibling API mappings until compatible release
inventories are verified and configured. Energia excludes Vaelchi's development
inventory because its dependency is `<0.2`; its discovery link remains visible.
Snapshots keep strict builds independent of sibling-site availability. Refresh
them deliberately and verify target anchors when adding cross-project content.
RTD's actual Git identifier selects repository source/edit links.

`browser-check.cjs` tests the rendered home page with Playwright 1.62.1. CI
runs it on Python 3.13 after the strict build, checking appearance choices,
persistence, live system changes, keyboard activation, and mobile navigation.
