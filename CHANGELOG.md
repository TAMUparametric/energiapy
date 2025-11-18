# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2.1.7] - Unreleased

### Changed
- getattr dunder to pull attrs from constituents in Storage

### Fixed 
- retry to fix strange variable index bug when writing inventory bound



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
