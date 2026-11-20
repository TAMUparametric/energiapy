# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2.1.7] - Unreleased

### Changed
- Clustering is maintained in Vaelchi. Energia depends on `vaelchi>=0.1.0,<0.2`
  and preserves `energia.surrogate.aggregation` and its `ahc` module as
  compatibility imports. New examples import from `vaelchi` directly.
- Documentation uses the new cubist logos and a light/dark theme switcher.
- getattr dunder to pull attrs from constituents in Storage
- AHC defaults to `selection="legacy"` to preserve historical representative
  selection. `selection="nearest_centroid"` is an explicit alternative, with
  earliest-period tie breaking. The chosen policy is recorded in `AHCResult`.

### Added
- `Sample.weighted_sum()` builds an explicit representative-period total for an
  objective or constraint using occurrence counts from Vaelchi or `Periods.weight`.
- `Model.save(as_type="json")` exports deterministic results in Gana's
  versioned JSON format. A rebuilt model can import a result after Gana
  verifies that its formulation matches the saved fingerprint.
- Standalone chronology-constrained AHC aggregation with representative profiles,
  labels, occurrence weights, reconstruction, and behavioral tests.
- Historical-data comparisons for five datasets at 20 and 35 representative
  days. Legacy-mode indices, weights, and profiles match the historical function
  in all ten cases; see `docs/validation/ahc/README.md` for scope and reproduction.

### Fixed
- The notebook exporter reports missing example notebooks before creating an
  output directory. Its dependencies are declared in the `docs` extra.
- Importing or reloading Energia respects the application's log level and
  handlers. Applications can enable progress messages through Python logging.
- `Model.save()` writes the latest or selected solver result atomically. It
  accepts an explicit destination and raises before writing if no result exists.
- A time scale inferred from a profile, or declared by dividing a coarser
  period, now creates a solver index for every subdivision. Time-sum
  constraints link the resulting decisions to their coarser totals.
- Each model copies its initializer list. Reusing a list across models now runs
  the default recipes and instructions only for models that request them, once per model.
- One-period process conversions accept a single coefficient in a list, such
  as `[-5]`, and expand scalar coefficients to the same length.
- Locating an operation applies its default capacity bound at the finest operating
  time scale introduced by the conversion. Explicit upper and equality bounds are
  preserved, and repeated placement keeps the same operating constraints.
- A process, transport, or storage can now be located before any operating activity
  is declared. The first operating bound uses the model horizon when no local
  operating time scale has been declared.
- Locating storage now recognizes upper and equality bounds on inventory capacity
  in the scenario at the selected location and horizon, including a bound of zero.
- Locating storage preserves an explicit upper bound or equality on inventory at
  the selected location and period. A lower bound alone still allows placement
  to apply the default inventory limit.
- `Sample` equality and hashing use the aspect and its selected domain. Samples
  at different times or locations keep separate dictionary entries, and selecting
  the same sample again retrieves its entry after binding.
- Normalization uses a common scale for interval endpoints and preserves a
  shared resource price interval passed to `prep()`. Constant series normalize
  to zero with min–max scaling. Max scaling keeps an all-zero series at zero.
- DataFrame scaling preserves the index and column labels for `minmax` and
  `standard`, handles zero maxima, and raises `ValueError` for an unknown method.
- Ordinary variable mappings use `Aspect.maps` and reporting variable mappings use
  `Aspect.maps_report`. Repeating a mapping preserves the constraint coefficients.
- The `price` instruction now handles a resource price interval through Gana 1.2.0. It calculates `spend` as resource price times `consume`. The tiny example evaluates `spend` across that interval and initializes the paper-sorting model independently.
- Process conversion balances use the appropriate time scale for each resource, including lagged outputs ([#330](https://github.com/TAMUparametric/energiapy/pull/330)).
- `Model.output()` displays solutions with Gana 1.1.0's output API ([#331](https://github.com/TAMUparametric/energiapy/pull/331)).
- Conversion arithmetic accumulates repeated commodities, preserves saved operands, and combines time-varying coefficients elementwise ([#332](https://github.com/TAMUparametric/energiapy/pull/332)).
- Repeated linkage-parent lookups no longer duplicate routes in spatial sums.
  This restores the Seattle-Topeka example's total cost to 153,675 instead of
  counting each route five times.
- Registered linkages appear as leaves under their containing location in
  `Location.tree` and `Space.tree`. `Location.all()` yields each route once.
- Register Markdown documents with the loaded `myst-nb` parser, fixing the
  Read the Docs error "Source parser for markdown not registered". Constrain
  Sphinx and the book theme to the tested compatible versions.
- retry to fix strange variable index bug when writing inventory bound
- AHC error reporting uses actual cluster centroids and accumulates squared
  errors across all parent groups. Both selection modes report centroid SSE
  (`inertia`) and selected-profile SSE (`reconstruction_error`); the historical
  final-parent-only, cluster-count-divided `wcss_sum` is not retained.



## [2.1.6] - 2025-11-17

### Changed 
- Read Me
- Using helper functions to simplify classes 


## [2.1.5] - 2025-11-12

### Changed 
- Arranged classes better

### Fixed 
- Fixed printing issue for calculations 


## [2.1.4] - 2025-11-4
### New 
- Better plotting

## [2.1.3] - 2025-11-3
### Changed 
- Made Conversion subtypes for clarity

### Fixed
- Reverse Spatial Mapping

### New 
- Multilocation examples and tests
- Supply chain examples in energia.library.examples

## [2.1.2] - 2025-11-1
### Changed
- Samples write Calculate Constraint Directly
- Constraints made functions of Aspect 
- Domain tree simplified
- Active representation returned form list

### Fixed
- Passing sample as indices
- Documentation import issue

### New 
- Scenario to collect parameter input

## [2.1.1] - 2025-10-29
### Changed 
- More descriptive logging, with inline time 
- Horizon determination and period, tree
- Mode nomenclature and birthing

### Fixed
- Placed checks to avoid repeated mode constraints 
- Automatic generation of temporal objects (Periods)

### New 
- Handling of time, allows for better mapping


## [2.1.0] - 2025-10-20
### Changed
- **kwargs for parameter input 
- Instruct for specialized parameters
- Allows aliasing aspects 

## [2.0.2] - 2025-10-20
### Changed
- Use logging instead of print
- X | None instead of Optional[X] 
