# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.2] - 2025-09-11

### Fixed

- Schema
    - apply default value (if configured), even if the property is missing

## [1.2.1] - 2025-04-07

### Fixed

- Schema
    - additional properties were omitted in `result.unwrap()`, even if additional properties were allowed

## [1.2.0] - 2025-03-24

### Added

- Schema
    - `OneOf` now provides meaningful error descriptions

### Fixed

- Schema
    - nullable schemas could cause runtime errors

## [1.1.0] - 2024-08-15

### Added

- Schema
    - constant values can now be set (`Object({"static": 5, dynamic: Integer()})`)
    - added the parameter `nullable=True` `optional()`

### Fixed

- Schema
    - nullable schemas could cause runtime errors

## [1.0.5] - 2023-01-14

### Fixed

- Schema
    - `enum` with multiple values specified raised an error

## [1.0.4] - 2023-01-13

### Added

- Schema
    - Added `OneOf`

## [1.0.3] - 2023-01-11

### Added

- Schemas now support expect, throwing an error if the data is invalid

### Fixed

- Schema
    - Minor fixes

## [1.0.2] - 2022-12-28

### Added

- Schema
    - String: now supports `.url()`, providing a default regex

## [1.0.1] - 2022-12-24

### Changed

- Schema
    - Object: additional properties are now disallowed by default

### Fixed

- Schema
    - inclusive min/max didn't work
    - typing failed when working with min/max/enum

## [1.0.0] - 2022-12-23

### Added

- Schema validation
- Chains: support `assertGet`

## [0.10.2] - 2022-11-07

### Added

- Chains: Support normal array indexing (`chain["list[0].name"]` instead of `chain["list.[0].name"]`). Both ways are supported.

## [0.10.1] - 2022-11-06

### Added

- Improved type hints

## [0.10.0] - 2022-11-04

### Changed

- Renamed `tryGet` to `optionalCast`

### Fixed

- Unhandled exceptions with chains

## [0.9.2] - 2022-11-02

### Added

- Added support for chaining (`.chain`)

## [0.9.1] - 2022-10-27

### Added

- Marked package as typed

## [0.9.0] - 2022-10-27

### Added

- JDict implementation
- JList implementation
