# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to
[Semantic Versioning].

## Guiding Principles

- Changelogs are for humans, not machines.
- There should be an entry for every single version.
- The same types of changes should be grouped.
- Versions and sections should be linkable.
- The latest version comes first.
- The release date of each version is displayed.
- Mention whether you follow Semantic Versioning.

## Types of Changes:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

## Releases

### [Unreleased]
#### Added
- Javascript file support

### [0.1.1] - 2020-12-14
#### Added
- Media file support
#### Changed
- Removed unsupported panki convert and merge commands

### [0.1.0] - 2020-11-20
#### Added
- Gitlab CI pipeline integration
- `CHANGELOG.md` and backfilled notes for version 0.0.1
#### Changed
- Introduced classes for project configuration
- Reorganized code related to packaging and collections
- Removed dependency on Jinja

### [0.0.1] - 2020-09-03
#### Added
- Initial project scaffolding functionality
- Initial project configuration schema
- Initial project build process
- Example project structures
- Command to dump an Anki `.apkg` or `.colpkg` file's contents
- Project documentation (`README.md` and `CONTRIBUTING.md`)


<!-- releases -->

[Unreleased]: https://gitlab.com/x4ku/panki/-/tree/master/
[0.1.0]: https://gitlab.com/x4ku/panki/-/tree/0.1.0
[0.0.1]: https://gitlab.com/x4ku/panki/-/tree/0.0.1


<!-- links -->

[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
